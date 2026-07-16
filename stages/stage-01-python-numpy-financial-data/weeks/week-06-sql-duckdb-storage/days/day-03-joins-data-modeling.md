# 第 6 周第 3 天：多表连接与数据建模

## 今日目标

- 理解为什么量化数据库需要多张表。
- 掌握 `INNER JOIN` 和 `LEFT JOIN`。
- 理解连接键、主键和重复记录之间的关系。
- 能把行情、股票信息和交易状态组合成研究数据集。

## 一、为什么不能把所有信息放在一张表

量化研究中常见的数据类型包括：

- 每日变化的行情数据。
- 很少变化的股票基础信息。
- 每日变化的交易状态。
- 行业分类、指数成分和财务数据。

如果把所有字段都放在一张表中，会产生大量重复数据，也不利于维护。

推荐至少建立三张基础表。

## 二、基础表设计

### 1. 行情表 `daily_prices`

```text
trade_date
symbol
open
high
low
close
volume
amount
```

建议主键：

```text
trade_date + symbol
```

### 2. 股票基础信息表 `stock_info`

```text
symbol
stock_name
list_date
delist_date
industry
exchange
```

建议主键：

```text
symbol
```

### 3. 交易状态表 `trading_status`

```text
trade_date
symbol
is_trading
is_st
is_suspended
is_limit_up
is_limit_down
```

建议主键：

```text
trade_date + symbol
```

## 三、JOIN 类型

| JOIN | 含义 |
|---|---|
| `INNER JOIN` | 只保留两张表都存在的记录 |
| `LEFT JOIN` | 保留左表全部记录 |
| `RIGHT JOIN` | 保留右表全部记录 |
| `FULL JOIN` | 保留两张表的全部记录 |

个人量化研究中最常用的是：

```text
INNER JOIN
LEFT JOIN
```

## 四、连接股票名称

```sql
SELECT
    p.trade_date,
    p.symbol,
    s.stock_name,
    s.industry,
    p.close
FROM daily_prices AS p
LEFT JOIN stock_info AS s
    ON p.symbol = s.symbol;
```

这里的连接键是：

```text
p.symbol = s.symbol
```

使用 `LEFT JOIN` 的原因：

- 行情表通常是研究主表。
- 即使部分股票基础信息缺失，也希望保留行情记录。
- 缺失的基础信息会显示为 `NULL`，便于后续检查。

## 五、连接每日交易状态

```sql
SELECT
    p.trade_date,
    p.symbol,
    p.close,
    t.is_trading,
    t.is_st,
    t.is_suspended,
    t.is_limit_up,
    t.is_limit_down
FROM daily_prices AS p
LEFT JOIN trading_status AS t
    ON p.trade_date = t.trade_date
    AND p.symbol = t.symbol;
```

连接键必须同时包含：

```text
trade_date + symbol
```

## 六、错误连接示例

错误写法：

```sql
SELECT *
FROM daily_prices AS p
LEFT JOIN trading_status AS t
    ON p.symbol = t.symbol;
```

问题：

- 某只股票在 `trading_status` 中有很多日期。
- 行情表的一条记录会匹配该股票所有日期的状态。
- 连接后行数会成倍增加。
- 不同日期的数据会错误组合。

这类问题叫作“多对多连接爆炸”。

## 七、连接后的重复检查

### 1. 检查主键重复

```sql
SELECT
    trade_date,
    symbol,
    COUNT(*) AS row_count
FROM joined_prices
GROUP BY trade_date, symbol
HAVING COUNT(*) > 1;
```

正常情况下应返回 0 行。

### 2. 比较连接前后行数

```sql
SELECT COUNT(*)
FROM daily_prices;
```

```sql
SELECT COUNT(*)
FROM joined_prices;
```

对于以行情表为左表的正确 `LEFT JOIN`，如果右表连接键唯一，连接前后行数通常应一致。

### 3. 检查右表连接键唯一性

```sql
SELECT
    trade_date,
    symbol,
    COUNT(*) AS row_count
FROM trading_status
GROUP BY trade_date, symbol
HAVING COUNT(*) > 1;
```

连接前必须先检查右表主键是否重复。

## 八、筛选可交易股票

```sql
SELECT
    p.trade_date,
    p.symbol,
    s.stock_name,
    s.industry,
    p.close,
    p.amount
FROM daily_prices AS p
LEFT JOIN stock_info AS s
    ON p.symbol = s.symbol
LEFT JOIN trading_status AS t
    ON p.trade_date = t.trade_date
    AND p.symbol = t.symbol
WHERE t.is_trading = TRUE
  AND t.is_st = FALSE
  AND t.is_suspended = FALSE;
```

注意：

- `is_trading = TRUE` 不一定等价于成交量大于零。
- 涨跌停股票仍可能处于交易状态，但实际策略可能无法按理想价格成交。
- 后续回测要根据策略需要决定是否排除涨跌停。

## 九、查询指定行业

```sql
SELECT
    p.trade_date,
    p.symbol,
    s.stock_name,
    s.industry,
    p.close
FROM daily_prices AS p
INNER JOIN stock_info AS s
    ON p.symbol = s.symbol
WHERE s.industry = '医药生物'
ORDER BY p.trade_date, p.symbol;
```

## 十、`INNER JOIN` 与 `LEFT JOIN` 对比

### `INNER JOIN`

```sql
SELECT *
FROM daily_prices AS p
INNER JOIN stock_info AS s
    ON p.symbol = s.symbol;
```

只保留基础信息表中也存在的股票。

### `LEFT JOIN`

```sql
SELECT *
FROM daily_prices AS p
LEFT JOIN stock_info AS s
    ON p.symbol = s.symbol;
```

保留全部行情，缺失基础信息的字段为 `NULL`。

研究中选择原则：

- 需要完整保留主表记录时使用 `LEFT JOIN`。
- 只需要两边都完整的数据时使用 `INNER JOIN`。

## 十一、今日练习

1. 创建三张模拟数据表。
2. 将行情表和股票信息表连接。
3. 将行情表和交易状态表连接。
4. 查询非 ST、非停牌股票。
5. 查询某个行业的全部股票。
6. 故意省略日期连接键，观察行数变化。
7. 检查连接后是否出现重复记录。
8. 比较 `INNER JOIN` 和 `LEFT JOIN` 的结果差异。

## 十二、今日输出

建议创建：

```text
sql/join_queries.sql
```

核心查询：

```sql
CREATE OR REPLACE VIEW tradable_daily_prices AS
SELECT
    p.trade_date,
    p.symbol,
    s.stock_name,
    s.industry,
    p.open,
    p.high,
    p.low,
    p.close,
    p.volume,
    p.amount
FROM daily_prices AS p
LEFT JOIN stock_info AS s
    ON p.symbol = s.symbol
LEFT JOIN trading_status AS t
    ON p.trade_date = t.trade_date
    AND p.symbol = t.symbol
WHERE COALESCE(t.is_trading, FALSE) = TRUE
  AND COALESCE(t.is_st, TRUE) = FALSE
  AND COALESCE(t.is_suspended, TRUE) = FALSE;
```

## 十三、检查清单

- [ ] 每张表都有明确主键。
- [ ] 股票基础信息使用 `symbol` 连接。
- [ ] 每日状态使用 `trade_date + symbol` 连接。
- [ ] 连接前检查右表主键重复。
- [ ] 连接后检查行数和联合主键重复。
- [ ] 能解释 `INNER JOIN` 与 `LEFT JOIN` 的差异。
