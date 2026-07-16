# 第 6 周第 7 天：阶段项目——建立本地行情数据库

## 项目目标

建立一个可以被后续回测系统重复使用的本地行情数据库。

项目完成后应支持：

- 查询指定股票和日期范围的行情。
- 查询某一天全部股票。
- 计算每只股票的日收益率。
- 计算 5 日与 20 日移动均价。
- 计算 20 日滚动波动率。
- 按交易日进行收益率和成交额排名。
- 将查询结果转换为 pandas DataFrame。

## 一、建议项目结构

```text
quant-research/
├── data/
│   ├── raw/
│   │   └── daily_prices.csv
│   └── processed/
│       └── daily_prices/
│           ├── year=2025/
│           └── year=2026/
├── database/
│   └── market.duckdb
├── sql/
│   ├── create_views.sql
│   ├── basic_queries.sql
│   └── factor_queries.sql
├── src/
│   ├── import_market_data.py
│   ├── query_market_data.py
│   └── validate_market_data.py
└── tests/
    └── test_market_database.py
```

## 二、第一步：检查原始数据

行情表至少包含：

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

需要检查：

- 日期格式是否正确。
- 股票代码格式是否统一。
- 是否存在重复记录。
- 是否存在空值。
- 价格是否小于或等于零。
- 最高价是否低于最低价。
- 成交量和成交额是否为负。
- 同一股票内部日期是否有序。

### 数据检查函数

```python
import pandas as pd


def validate_market_data(
    prices: pd.DataFrame,
) -> dict[str, int]:
    """检查日线行情的基础质量问题。"""
    required = {
        "trade_date",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
    }
    missing = required.difference(prices.columns)
    if missing:
        raise ValueError(f"缺少字段: {sorted(missing)}")

    duplicate_count = prices.duplicated(
        ["trade_date", "symbol"]
    ).sum()

    invalid_price_count = (
        (prices[["open", "high", "low", "close"]] <= 0)
        .any(axis=1)
        .sum()
    )

    high_low_error_count = (
        prices["high"] < prices["low"]
    ).sum()

    negative_volume_count = (
        prices["volume"] < 0
    ).sum()

    negative_amount_count = (
        prices["amount"] < 0
    ).sum()

    return {
        "row_count": len(prices),
        "duplicate_count": int(duplicate_count),
        "invalid_price_count": int(invalid_price_count),
        "high_low_error_count": int(high_low_error_count),
        "negative_volume_count": int(negative_volume_count),
        "negative_amount_count": int(negative_amount_count),
    }
```

## 三、第二步：清洗数据

### 1. 统一类型

```python
prices["trade_date"] = pd.to_datetime(
    prices["trade_date"]
)
prices["symbol"] = prices["symbol"].astype("string")
```

### 2. 删除联合主键重复

```python
prices = prices.drop_duplicates(
    subset=["trade_date", "symbol"],
    keep="last",
)
```

删除重复前，应先确认重复记录的来源。正式研究中最好保留清洗日志。

### 3. 按股票和日期排序

```python
prices = prices.sort_values(
    ["symbol", "trade_date"]
).reset_index(drop=True)
```

### 4. 过滤无效价格

```python
prices = prices[
    (prices["open"] > 0)
    & (prices["high"] > 0)
    & (prices["low"] > 0)
    & (prices["close"] > 0)
]
```

### 5. 检查价格关系

```python
prices = prices[
    (prices["high"] >= prices["low"])
    & (prices["high"] >= prices["open"])
    & (prices["high"] >= prices["close"])
    & (prices["low"] <= prices["open"])
    & (prices["low"] <= prices["close"])
]
```

### 6. 检查成交字段

```python
prices = prices[
    (prices["volume"] >= 0)
    & (prices["amount"] >= 0)
]
```

## 四、第三步：保存为分区 Parquet

```python
prices["year"] = prices["trade_date"].dt.year

prices.to_parquet(
    "data/processed/daily_prices",
    partition_cols=["year"],
    index=False,
)
```

目标目录：

```text
data/processed/daily_prices/year=2025/
data/processed/daily_prices/year=2026/
```

## 五、第四步：创建 DuckDB 视图

视图保存查询逻辑，不复制全部数据。

```sql
CREATE OR REPLACE VIEW daily_prices AS
SELECT *
FROM read_parquet(
    'data/processed/daily_prices/**/*.parquet',
    hive_partitioning = true
);
```

创建数据库和视图：

```python
import duckdb

with duckdb.connect("database/market.duckdb") as connection:
    connection.execute("""
        CREATE OR REPLACE VIEW daily_prices AS
        SELECT *
        FROM read_parquet(
            'data/processed/daily_prices/**/*.parquet',
            hive_partitioning = true
        )
    """)
```

## 六、第五步：创建收益率视图

```sql
CREATE OR REPLACE VIEW daily_returns AS
SELECT
    trade_date,
    symbol,
    close,
    amount,
    close / LAG(close) OVER (
        PARTITION BY symbol
        ORDER BY trade_date
    ) - 1 AS daily_return
FROM daily_prices;
```

每只股票第一条记录没有前一日价格，因此 `daily_return` 应为 `NULL`。

## 七、第六步：创建滚动特征视图

```sql
CREATE OR REPLACE VIEW daily_features AS
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
)
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
    AVG(close) OVER (
        PARTITION BY symbol
        ORDER BY trade_date
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) AS ma20,
    STDDEV_SAMP(daily_return) OVER (
        PARTITION BY symbol
        ORDER BY trade_date
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) AS volatility_20d,
    RANK() OVER (
        PARTITION BY trade_date
        ORDER BY daily_return DESC
    ) AS return_rank,
    RANK() OVER (
        PARTITION BY trade_date
        ORDER BY amount DESC
    ) AS amount_rank
FROM returns;
```

## 八、第七步：实现查询函数

### 查询日线行情

```python
from collections.abc import Sequence

import duckdb
import pandas as pd


def get_daily_prices(
    connection: duckdb.DuckDBPyConnection,
    symbols: Sequence[str],
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """查询多只股票的日线行情。"""
    if not symbols:
        raise ValueError("symbols 不能为空")
    if start_date > end_date:
        raise ValueError("start_date 不能晚于 end_date")

    placeholders = ", ".join("?" for _ in symbols)
    query = f"""
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
    WHERE symbol IN ({placeholders})
      AND trade_date BETWEEN ? AND ?
    ORDER BY symbol, trade_date
    """

    parameters = [
        *symbols,
        start_date,
        end_date,
    ]

    return connection.execute(
        query,
        parameters,
    ).fetchdf()
```

### 查询收益率

```python
def get_daily_returns(
    connection: duckdb.DuckDBPyConnection,
    symbols: Sequence[str],
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """查询多只股票的日收益率。"""
    if not symbols:
        raise ValueError("symbols 不能为空")

    placeholders = ", ".join("?" for _ in symbols)
    query = f"""
    SELECT
        trade_date,
        symbol,
        close,
        daily_return
    FROM daily_returns
    WHERE symbol IN ({placeholders})
      AND trade_date BETWEEN ? AND ?
    ORDER BY symbol, trade_date
    """

    return connection.execute(
        query,
        [*symbols, start_date, end_date],
    ).fetchdf()
```

### 查询成交额排名

```python
def get_top_amount_stocks(
    connection: duckdb.DuckDBPyConnection,
    trade_date: str,
    top_n: int = 20,
) -> pd.DataFrame:
    """查询指定交易日成交额最大的股票。"""
    if top_n <= 0:
        raise ValueError("top_n 必须大于 0")

    query = """
    SELECT
        trade_date,
        symbol,
        close,
        amount,
        amount_rank
    FROM daily_features
    WHERE trade_date = ?
    ORDER BY amount_rank
    LIMIT ?
    """

    return connection.execute(
        query,
        [trade_date, top_n],
    ).fetchdf()
```

## 九、测试要求

至少测试以下情况：

- 正常查询一只股票。
- 查询多只股票。
- 日期范围没有数据。
- 股票代码不存在。
- 查询结果按日期排序。
- 每只股票第一条收益率为缺失值。
- 不存在重复的“股票代码—日期”组合。
- 开始日期晚于结束日期时抛出错误。
- `symbols` 为空时抛出错误。
- `top_n` 小于等于零时抛出错误。

### pytest 示例

```python
import duckdb
import pandas as pd


def test_daily_returns_first_row_is_missing(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    result = get_daily_returns(
        connection,
        symbols=["000001.SZ", "000002.SZ"],
        start_date="2026-01-01",
        end_date="2026-06-30",
    )

    first_rows = (
        result.sort_values(["symbol", "trade_date"])
        .groupby("symbol")
        .head(1)
    )

    assert first_rows["daily_return"].isna().all()
```

检查联合主键：

```python
def test_no_duplicate_primary_key(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    result = connection.execute("""
        SELECT
            trade_date,
            symbol
        FROM daily_prices
    """).fetchdf()

    assert not result.duplicated(
        ["trade_date", "symbol"]
    ).any()
```

## 十、项目验收

最终程序应能运行：

```python
import duckdb

with duckdb.connect(
    "database/market.duckdb"
) as connection:
    prices = get_daily_prices(
        connection=connection,
        symbols=["000001.SZ", "000002.SZ"],
        start_date="2026-01-01",
        end_date="2026-06-30",
    )

print(prices)
```

返回结果应满足：

- 字段清晰。
- 日期有序。
- 股票代码格式统一。
- 没有重复联合主键。
- 日期范围正确。
- 可以直接用于后续统计分析和回测。

## 十一、本周最终检查清单

- [ ] 原始行情字段完整。
- [ ] 日期和股票代码类型正确。
- [ ] 联合主键不存在重复。
- [ ] 无效价格和成交字段已经处理。
- [ ] Parquet 按年份分区。
- [ ] DuckDB 视图可以重复创建。
- [ ] 收益率按股票分区计算。
- [ ] 移动均线和波动率窗口正确。
- [ ] 截面排名按交易日期分区。
- [ ] 查询函数使用参数化 SQL。
- [ ] 测试覆盖正常和异常情况。
- [ ] 项目文档说明数据口径和目录结构。
