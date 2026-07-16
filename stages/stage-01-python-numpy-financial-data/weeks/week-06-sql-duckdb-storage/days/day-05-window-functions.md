# 第 6 周第 5 天：窗口函数与金融时间序列

## 今日目标

- 理解窗口函数为什么不会减少结果行数。
- 掌握 `LAG()`、`LEAD()`、`ROW_NUMBER()`、`RANK()` 和滚动窗口。
- 能使用 SQL 计算收益率、移动均线和滚动波动率。
- 能区分时间序列窗口与截面排名窗口。

## 一、窗口函数基本结构

```sql
函数() OVER (
    PARTITION BY 分组字段
    ORDER BY 排序字段
)
```

窗口函数与 `GROUP BY` 的区别：

- `GROUP BY` 会把多行压缩为一行聚合结果。
- 窗口函数保留原始每一行，同时增加统计字段。

例如，行情表有 1000 行，增加移动均线后仍然有 1000 行。

## 二、时间序列窗口

股票时间序列计算通常使用：

```sql
PARTITION BY symbol
ORDER BY trade_date
```

含义：

- 不同股票分别计算。
- 每只股票内部按日期升序排列。

如果遗漏 `PARTITION BY symbol`，上一行可能来自另一只股票，造成跨股票污染。

## 三、使用 `LAG()` 获取前一期数据

### 前一日收盘价

```sql
SELECT
    trade_date,
    symbol,
    close,
    LAG(close) OVER (
        PARTITION BY symbol
        ORDER BY trade_date
    ) AS previous_close
FROM daily_prices;
```

每只股票第一条记录没有上一交易日，因此 `previous_close` 应为 `NULL`。

### 获取前 5 个交易日收盘价

```sql
SELECT
    trade_date,
    symbol,
    close,
    LAG(close, 5) OVER (
        PARTITION BY symbol
        ORDER BY trade_date
    ) AS close_5d_ago
FROM daily_prices;
```

## 四、计算日收益率

简单收益率：

$$
r_t = \frac{P_t}{P_{t-1}} - 1
$$

SQL：

```sql
SELECT
    trade_date,
    symbol,
    close,
    close / LAG(close) OVER (
        PARTITION BY symbol
        ORDER BY trade_date
    ) - 1 AS daily_return
FROM daily_prices;
```

建议先创建收益率视图：

```sql
CREATE OR REPLACE VIEW daily_returns AS
SELECT
    trade_date,
    symbol,
    close,
    close / LAG(close) OVER (
        PARTITION BY symbol
        ORDER BY trade_date
    ) - 1 AS daily_return
FROM daily_prices;
```

## 五、使用 `LEAD()` 获取未来数据

```sql
SELECT
    trade_date,
    symbol,
    close,
    LEAD(close) OVER (
        PARTITION BY symbol
        ORDER BY trade_date
    ) AS next_close
FROM daily_prices;
```

未来 1 日收益率标签：

```sql
SELECT
    trade_date,
    symbol,
    close,
    LEAD(close) OVER (
        PARTITION BY symbol
        ORDER BY trade_date
    ) / close - 1 AS future_return_1d
FROM daily_prices;
```

注意：

- `LEAD()` 可以用于构造监督学习标签。
- 未来信息不能作为当日特征。
- 回测中必须避免未来数据泄漏。

## 六、移动平均

### 5 日移动平均

```sql
SELECT
    trade_date,
    symbol,
    close,
    AVG(close) OVER (
        PARTITION BY symbol
        ORDER BY trade_date
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) AS ma5
FROM daily_prices;
```

窗口包含：

```text
当前行 + 前 4 行 = 5 个交易日
```

### 20 日移动平均

```sql
SELECT
    trade_date,
    symbol,
    close,
    AVG(close) OVER (
        PARTITION BY symbol
        ORDER BY trade_date
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) AS ma20
FROM daily_prices;
```

### 严格要求完整窗口

默认情况下，前几天即使不足 5 条记录，也会计算均值。如果研究要求至少 5 条有效记录，可以同时计算窗口数量：

```sql
WITH features AS (
    SELECT
        trade_date,
        symbol,
        close,
        COUNT(close) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS count_5d,
        AVG(close) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS raw_ma5
    FROM daily_prices
)
SELECT
    trade_date,
    symbol,
    close,
    CASE
        WHEN count_5d = 5 THEN raw_ma5
        ELSE NULL
    END AS ma5
FROM features;
```

## 七、滚动波动率

日收益率标准差：

$$
\sigma = \sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(r_i-\bar r)^2}
$$

20 日滚动波动率：

```sql
SELECT
    trade_date,
    symbol,
    daily_return,
    STDDEV_SAMP(daily_return) OVER (
        PARTITION BY symbol
        ORDER BY trade_date
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) AS volatility_20d
FROM daily_returns;
```

年化波动率：

$$
\sigma_{annual} = \sigma_{daily}\sqrt{252}
$$

SQL：

```sql
SELECT
    trade_date,
    symbol,
    volatility_20d,
    volatility_20d * SQRT(252) AS annual_volatility_20d
FROM rolling_features;
```

## 八、累计值

每只股票累计成交额：

```sql
SELECT
    trade_date,
    symbol,
    amount,
    SUM(amount) OVER (
        PARTITION BY symbol
        ORDER BY trade_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_amount
FROM daily_prices;
```

累计窗口：

```text
从该股票第一条记录到当前记录
```

## 九、行号和排名

### `ROW_NUMBER()`

```sql
SELECT
    trade_date,
    symbol,
    close,
    ROW_NUMBER() OVER (
        PARTITION BY symbol
        ORDER BY trade_date
    ) AS trading_day_number
FROM daily_prices;
```

用途：

- 标记每只股票第几个交易日。
- 选取每组第一条或最后一条记录。
- 检查数据顺序。

### `RANK()`

```sql
SELECT
    trade_date,
    symbol,
    daily_return,
    RANK() OVER (
        PARTITION BY trade_date
        ORDER BY daily_return DESC
    ) AS return_rank
FROM daily_returns;
```

相同值会并列，并跳过后续名次。

例如：

```text
1, 2, 2, 4
```

### `DENSE_RANK()`

```sql
DENSE_RANK() OVER (
    PARTITION BY trade_date
    ORDER BY daily_return DESC
)
```

相同值并列，但名次连续：

```text
1, 2, 2, 3
```

## 十、截面排名

截面排名通常使用：

```sql
PARTITION BY trade_date
ORDER BY factor_value DESC
```

### 收益率排名

```sql
SELECT
    trade_date,
    symbol,
    daily_return,
    RANK() OVER (
        PARTITION BY trade_date
        ORDER BY daily_return DESC
    ) AS return_rank
FROM daily_returns;
```

### 成交额排名

```sql
SELECT
    trade_date,
    symbol,
    amount,
    ROW_NUMBER() OVER (
        PARTITION BY trade_date
        ORDER BY amount DESC, symbol ASC
    ) AS amount_rank
FROM daily_prices;
```

加入 `symbol ASC` 可以在成交额相同的情况下保持稳定排序。

## 十一、时间序列窗口与截面窗口

时间序列计算：

```sql
PARTITION BY symbol
ORDER BY trade_date
```

用于：

- 前一日收盘价。
- 收益率。
- 移动均线。
- 滚动波动率。
- 累计成交额。

截面计算：

```sql
PARTITION BY trade_date
ORDER BY factor_value DESC
```

用于：

- 每日收益率排名。
- 每日成交额排名。
- 每日因子排名。
- 每日股票分组。

## 十二、综合查询

```sql
WITH returns AS (
    SELECT
        trade_date,
        symbol,
        close,
        amount,
        close / LAG(close) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
        ) - 1 AS daily_return
    FROM daily_prices
),
features AS (
    SELECT
        trade_date,
        symbol,
        close,
        amount,
        daily_return,
        AVG(close) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS ma5,
        STDDEV_SAMP(daily_return) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS volatility_20d
    FROM returns
)
SELECT
    trade_date,
    symbol,
    close,
    amount,
    daily_return,
    ma5,
    volatility_20d,
    RANK() OVER (
        PARTITION BY trade_date
        ORDER BY daily_return DESC
    ) AS return_rank,
    RANK() OVER (
        PARTITION BY trade_date
        ORDER BY amount DESC
    ) AS amount_rank
FROM features
ORDER BY trade_date, symbol;
```

## 十三、今日练习

使用 SQL 计算：

1. 前一日收盘价。
2. 日收益率。
3. 5 日移动均价。
4. 20 日移动均价。
5. 20 日收益波动率。
6. 年化波动率。
7. 每日收益率截面排名。
8. 每日成交额排名。
9. 每只股票的累计成交额。
10. 每只股票的交易日序号。

## 十四、今日输出

建议创建：

```text
sql/factor_queries.sql
```

并创建视图：

```text
daily_returns
rolling_features
daily_rank_features
```

## 十五、检查清单

- [ ] 时间序列计算按 `symbol` 分区。
- [ ] 时间序列计算按 `trade_date` 排序。
- [ ] 截面排名按 `trade_date` 分区。
- [ ] 每只股票第一天收益率为缺失值。
- [ ] 移动窗口包含的行数定义正确。
- [ ] 能解释 `RANK()` 和 `DENSE_RANK()` 的区别。
- [ ] 使用 `LEAD()` 构造标签时没有把未来数据当作特征。
