# 第 6 周第 1 天：数据库与 SQL 基础

## 今日目标

- 理解数据库、表、字段、记录和主键。
- 掌握 `SELECT`、`FROM`、`WHERE`、`ORDER BY` 和 `LIMIT`。
- 能够查询指定股票和指定日期范围的行情。
- 理解日线行情表的联合主键设计。

## 一、数据库基础概念

| 概念 | 含义 |
|---|---|
| 数据库 | 一组有组织的数据 |
| 表 | 类似 pandas DataFrame |
| 字段 | DataFrame 的列 |
| 记录 | DataFrame 的一行 |
| 主键 | 唯一标识一条记录 |
| 查询 | 从数据库中读取数据 |
| SQL | 操作关系型数据库的语言 |

## 二、日线行情表结构

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

建议将以下字段组合作为日线行情的唯一标识：

```text
trade_date + symbol
```

原因：

- 同一只股票在不同交易日会有多条记录。
- 同一交易日会有多只股票。
- 只有“交易日期 + 股票代码”组合才能唯一标识一条日线行情。

## 三、SQL 查询基本结构

```sql
SELECT 字段
FROM 表名
WHERE 筛选条件
ORDER BY 排序字段
LIMIT 返回数量;
```

重点理解：

```text
SELECT：选择什么字段
FROM：从哪张表读取
WHERE：保留哪些记录
ORDER BY：如何排序
LIMIT：返回多少条记录
```

## 四、基础查询

### 1. 查询指定字段

```sql
SELECT
    trade_date,
    symbol,
    close
FROM daily_prices;
```

### 2. 查询全部字段

```sql
SELECT *
FROM daily_prices;
```

研究代码中不建议长期依赖 `SELECT *`，因为：

- 表结构变化时结果列可能发生变化。
- 会读取不需要的字段。
- 不利于明确数据口径。

### 3. 查询指定股票

```sql
SELECT *
FROM daily_prices
WHERE symbol = '000001.SZ';
```

### 4. 查询指定日期

```sql
SELECT *
FROM daily_prices
WHERE trade_date = '2026-01-05';
```

### 5. 查询日期范围

```sql
SELECT *
FROM daily_prices
WHERE trade_date BETWEEN '2026-01-01' AND '2026-06-30';
```

等价写法：

```sql
SELECT *
FROM daily_prices
WHERE trade_date >= '2026-01-01'
  AND trade_date <= '2026-06-30';
```

### 6. 使用多个筛选条件

```sql
SELECT
    trade_date,
    symbol,
    close,
    amount
FROM daily_prices
WHERE symbol = '000001.SZ'
  AND trade_date >= '2026-01-01'
  AND volume > 0;
```

### 7. 排序

按日期升序：

```sql
SELECT *
FROM daily_prices
ORDER BY trade_date ASC;
```

按日期降序：

```sql
SELECT *
FROM daily_prices
ORDER BY trade_date DESC;
```

多字段排序：

```sql
SELECT *
FROM daily_prices
ORDER BY symbol ASC, trade_date ASC;
```

### 8. 限制返回数量

```sql
SELECT *
FROM daily_prices
ORDER BY trade_date DESC
LIMIT 20;
```

### 9. 使用 `IN`

```sql
SELECT *
FROM daily_prices
WHERE symbol IN (
    '000001.SZ',
    '000002.SZ',
    '600000.SH'
);
```

### 10. 排除无效成交记录

```sql
SELECT *
FROM daily_prices
WHERE volume > 0
  AND amount > 0;
```

## 五、SQL 与 pandas 对照

| pandas | SQL |
|---|---|
| `df[["trade_date", "symbol", "close"]]` | `SELECT trade_date, symbol, close` |
| `df[df["symbol"] == code]` | `WHERE symbol = code` |
| `df.sort_values("trade_date")` | `ORDER BY trade_date` |
| `df.head(20)` | `LIMIT 20` |
| `df["symbol"].isin(codes)` | `WHERE symbol IN (...)` |

## 六、今日练习

编写不少于 10 条 SQL：

1. 查询全部字段。
2. 查询 `trade_date`、`symbol` 和 `close`。
3. 查询指定股票。
4. 查询指定日期。
5. 查询指定日期范围。
6. 按收盘价从高到低排序。
7. 按成交额从高到低排序。
8. 查询前 20 条记录。
9. 使用多个筛选条件。
10. 排除成交量为零的数据。

## 七、今日输出

建议创建：

```text
sql/basic_queries.sql
```

示例：

```sql
-- 查询指定股票在指定日期范围内的行情
SELECT
    trade_date,
    symbol,
    open,
    high,
    low,
    close,
    volume,
    amount
FROM daily_prices
WHERE symbol = '000001.SZ'
  AND trade_date BETWEEN '2026-01-01' AND '2026-06-30'
ORDER BY trade_date ASC;
```

## 八、检查清单

- [ ] 能解释数据库、表、字段和记录。
- [ ] 能解释为什么日线行情使用联合主键。
- [ ] 能独立编写 `SELECT` 查询。
- [ ] 能组合使用 `WHERE`、`ORDER BY` 和 `LIMIT`。
- [ ] 查询结果按交易日期正确排序。
- [ ] 能将常见 pandas 筛选操作改写为 SQL。
