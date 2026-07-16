# 第 6 周第 2 天：聚合、分组与统计查询

## 今日目标

- 掌握 `COUNT()`、`SUM()`、`AVG()`、`MIN()`、`MAX()` 和 `STDDEV()`。
- 理解 `GROUP BY` 的作用。
- 能区分时间序列分组与截面分组。
- 理解 `WHERE` 和 `HAVING` 的区别。

## 一、聚合函数

| 函数 | 作用 |
|---|---|
| `COUNT()` | 统计记录数量 |
| `SUM()` | 求和 |
| `AVG()` | 计算均值 |
| `MIN()` | 最小值 |
| `MAX()` | 最大值 |
| `STDDEV()` | 标准差 |

聚合函数会把多条记录压缩为一个统计结果。

## 二、基础聚合

### 1. 统计记录数量

```sql
SELECT COUNT(*) AS row_count
FROM daily_prices;
```

### 2. 统计股票数量

```sql
SELECT COUNT(DISTINCT symbol) AS stock_count
FROM daily_prices;
```

### 3. 计算平均收盘价

```sql
SELECT AVG(close) AS avg_close
FROM daily_prices;
```

### 4. 计算价格范围

```sql
SELECT
    MIN(close) AS min_close,
    MAX(close) AS max_close
FROM daily_prices;
```

### 5. 计算总成交额

```sql
SELECT SUM(amount) AS total_amount
FROM daily_prices;
```

## 三、`GROUP BY` 分组统计

### 1. 每只股票的交易日数量

```sql
SELECT
    symbol,
    COUNT(*) AS trading_days
FROM daily_prices
GROUP BY symbol
ORDER BY symbol;
```

### 2. 每只股票的均价和价格范围

```sql
SELECT
    symbol,
    AVG(close) AS avg_close,
    MIN(close) AS min_close,
    MAX(close) AS max_close
FROM daily_prices
GROUP BY symbol;
```

### 3. 每只股票的平均成交额

```sql
SELECT
    symbol,
    AVG(amount) AS avg_amount
FROM daily_prices
GROUP BY symbol
ORDER BY avg_amount DESC;
```

### 4. 每个交易日的全市场成交额

```sql
SELECT
    trade_date,
    SUM(amount) AS market_amount
FROM daily_prices
GROUP BY trade_date
ORDER BY trade_date;
```

### 5. 每日上涨和下跌股票数量

前提：表中已经有 `daily_return` 字段。

```sql
SELECT
    trade_date,
    SUM(CASE WHEN daily_return > 0 THEN 1 ELSE 0 END) AS up_count,
    SUM(CASE WHEN daily_return < 0 THEN 1 ELSE 0 END) AS down_count,
    SUM(CASE WHEN daily_return = 0 THEN 1 ELSE 0 END) AS flat_count
FROM daily_returns
GROUP BY trade_date
ORDER BY trade_date;
```

## 四、时间序列统计与截面统计

### 时间序列统计

```sql
GROUP BY symbol
```

含义：把同一只股票不同日期的数据放在一起统计。

例如，某只股票的平均收益率：

$$
\bar r_i = \frac{1}{T_i}\sum_{t=1}^{T_i} r_{i,t}
$$

其中：

- $i$ 表示股票。
- $t$ 表示交易日。
- $T_i$ 表示股票 $i$ 的有效交易日数量。

SQL：

```sql
SELECT
    symbol,
    AVG(daily_return) AS mean_return
FROM daily_returns
GROUP BY symbol;
```

### 截面统计

```sql
GROUP BY trade_date
```

含义：把同一天不同股票的数据放在一起统计。

某个交易日的市场平均收益率：

$$
\bar r_t = \frac{1}{N_t}\sum_{i=1}^{N_t} r_{i,t}
$$

其中 $N_t$ 是交易日 $t$ 的有效股票数量。

SQL：

```sql
SELECT
    trade_date,
    AVG(daily_return) AS market_mean_return
FROM daily_returns
GROUP BY trade_date;
```

核心区别：

```text
GROUP BY symbol      → 时间序列统计
GROUP BY trade_date  → 截面统计
```

## 五、`WHERE` 与 `HAVING`

### `WHERE`

在分组前筛选原始记录。

```sql
SELECT
    symbol,
    COUNT(*) AS trading_days
FROM daily_prices
WHERE trade_date >= '2026-01-01'
GROUP BY symbol;
```

### `HAVING`

在分组后筛选聚合结果。

```sql
SELECT
    symbol,
    COUNT(*) AS trading_days
FROM daily_prices
GROUP BY symbol
HAVING COUNT(*) >= 100;
```

### 组合使用

```sql
SELECT
    symbol,
    COUNT(*) AS trading_days,
    AVG(amount) AS avg_amount
FROM daily_prices
WHERE trade_date BETWEEN '2026-01-01' AND '2026-06-30'
GROUP BY symbol
HAVING COUNT(*) >= 80
ORDER BY avg_amount DESC;
```

执行逻辑：

1. `WHERE` 先保留指定日期范围的原始记录。
2. `GROUP BY` 再按股票分组。
3. 聚合函数计算每组结果。
4. `HAVING` 筛选聚合后的股票组。
5. `ORDER BY` 最后排序。

## 六、`CASE WHEN` 条件统计

```sql
SELECT
    trade_date,
    COUNT(*) AS stock_count,
    SUM(CASE WHEN close > open THEN 1 ELSE 0 END) AS up_count,
    SUM(CASE WHEN close < open THEN 1 ELSE 0 END) AS down_count
FROM daily_prices
GROUP BY trade_date
ORDER BY trade_date;
```

也可以计算上涨比例：

```sql
SELECT
    trade_date,
    AVG(CASE WHEN close > open THEN 1.0 ELSE 0.0 END) AS up_ratio
FROM daily_prices
GROUP BY trade_date;
```

## 七、今日练习

完成以下查询：

1. 每只股票的交易日数量。
2. 每只股票的平均收盘价。
3. 每只股票的最高价和最低价。
4. 每个交易日的总成交额。
5. 每个交易日上涨股票数量。
6. 每个交易日下跌股票数量。
7. 平均成交额最大的 20 只股票。
8. 数据不足 100 个交易日的股票。
9. 每日股票数量和平均收益率。
10. 每只股票的收益率标准差。

## 八、今日输出

建议创建：

```text
sql/aggregation_queries.sql
```

核心查询：

```sql
SELECT
    symbol,
    COUNT(*) AS trading_days,
    AVG(close) AS avg_close,
    STDDEV_SAMP(daily_return) AS return_std,
    AVG(amount) AS avg_amount
FROM daily_returns
GROUP BY symbol
HAVING COUNT(*) >= 100
ORDER BY avg_amount DESC;
```

## 九、检查清单

- [ ] 能解释聚合函数为什么会减少结果行数。
- [ ] 能使用 `GROUP BY symbol` 做时间序列统计。
- [ ] 能使用 `GROUP BY trade_date` 做截面统计。
- [ ] 能区分 `WHERE` 和 `HAVING`。
- [ ] 能使用 `CASE WHEN` 完成条件计数。
- [ ] 能检查分组统计中的缺失值和有效样本数量。
