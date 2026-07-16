# 第 6 周第 6 天：Parquet、分区与查询效率

## 今日目标

- 理解 CSV 与 Parquet 的差异。
- 将日线行情保存为 Parquet。
- 按年份建立分区数据集。
- 使用 DuckDB 查询分区文件。
- 掌握基础查询优化原则。

## 一、CSV 与 Parquet

| 特征 | CSV | Parquet |
|---|---|---|
| 存储方式 | 文本 | 列式存储 |
| 文件体积 | 较大 | 通常较小 |
| 数据类型 | 容易丢失 | 保留类型 |
| 查询速度 | 较慢 | 通常较快 |
| 读取部分列 | 不方便 | 支持 |
| 适合长期行情存储 | 一般 | 适合 |

CSV 适合人工查看、临时交换和小规模数据。Parquet 适合长期保存行情、按列读取和分析型查询。

## 二、读取原始行情

```python
from pathlib import Path

import pandas as pd

source_path = Path("data/raw/daily_prices.csv")

prices = pd.read_csv(
    source_path,
    dtype={"symbol": "string"},
    parse_dates=["trade_date"],
)
```

检查数据类型：

```python
print(prices.dtypes)
print(prices.isna().sum())
```

股票代码必须保持字符串类型，避免丢失前导零。

## 三、保存单个 Parquet 文件

```python
output_path = Path(
    "data/processed/daily_prices.parquet"
)
output_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

prices.to_parquet(
    output_path,
    index=False,
)
```

读取并验证：

```python
loaded = pd.read_parquet(output_path)

assert len(loaded) == len(prices)
assert list(loaded.columns) == list(prices.columns)
```

## 四、按年份分区

增加年份字段：

```python
prices["year"] = prices["trade_date"].dt.year
```

保存为分区数据集：

```python
prices.to_parquet(
    "data/processed/daily_prices",
    partition_cols=["year"],
    index=False,
)
```

目录示例：

```text
data/processed/daily_prices/
├── year=2024/
├── year=2025/
└── year=2026/
```

当查询只需要 2026 年时，分析引擎可以跳过其他年份目录。

## 五、DuckDB 查询分区文件

```sql
SELECT
    trade_date,
    symbol,
    close
FROM read_parquet(
    'data/processed/daily_prices/**/*.parquet',
    hive_partitioning = true
)
WHERE year = 2026
ORDER BY trade_date, symbol;
```

查询指定股票：

```sql
SELECT
    trade_date,
    symbol,
    close,
    amount
FROM read_parquet(
    'data/processed/daily_prices/**/*.parquet',
    hive_partitioning = true
)
WHERE year = 2026
  AND symbol = '000001.SZ'
  AND trade_date BETWEEN '2026-01-01' AND '2026-06-30'
ORDER BY trade_date;
```

## 六、分区设计原则

适合分区的字段：

- 年份。
- 月份。
- 市场。
- 数据类型。

不建议把全部 A 股日线数据直接按股票代码分区，因为容易产生大量小目录和小文件，全市场截面查询也需要扫描很多分区。

## 七、查询效率原则

### 1. 只读取需要的列

低效：

```sql
SELECT *
FROM daily_prices;
```

更合理：

```sql
SELECT
    trade_date,
    symbol,
    close
FROM daily_prices;
```

### 2. 尽早筛选日期和股票

```sql
WHERE year = 2026
  AND symbol IN ('000001.SZ', '000002.SZ')
  AND trade_date >= '2026-01-01'
```

### 3. 避免无意义的全表排序

只有输出、窗口计算或前 N 条查询需要固定顺序时才排序。

### 4. 避免过多小文件

大量小文件会增加文件打开、元数据读取和目录管理成本。

### 5. 分区方式要匹配常用查询

经常按年份查询时，按年份分区有价值。经常读取全部历史时，不应过度细分。

## 八、性能对比实验

比较三种方式：

1. pandas 读取 CSV 后筛选。
2. DuckDB 直接查询 CSV。
3. DuckDB 查询 Parquet。

记录：

| 项目 | pandas CSV | DuckDB CSV | DuckDB Parquet |
|---|---:|---:|---:|
| 文件大小 |  |  |  |
| 查询时间 |  |  |  |
| 返回行数 |  |  |  |
| 读取字段数 |  |  |  |

简单计时：

```python
from time import perf_counter

start = perf_counter()

# 执行查询

elapsed = perf_counter() - start
print(f"耗时: {elapsed:.6f} 秒")
```

本阶段不追求严格基准测试，重点是理解存储格式和查询方式的差异。

## 九、保存分区数据函数

```python
from pathlib import Path

import pandas as pd


def save_partitioned_prices(
    prices: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    """按年份保存日线行情 Parquet 数据集。"""
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

    result = prices.copy()
    result["trade_date"] = pd.to_datetime(
        result["trade_date"]
    )
    result["symbol"] = result["symbol"].astype("string")
    result["year"] = result["trade_date"].dt.year

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    result.to_parquet(
        output_dir,
        partition_cols=["year"],
        index=False,
    )
```

## 十、今日练习

1. 将 CSV 转换为单个 Parquet 文件。
2. 检查转换前后行数和字段类型。
3. 按年份保存分区数据集。
4. 使用 DuckDB 查询单个年份。
5. 查询指定股票和日期范围。
6. 比较三种查询方式。
7. 记录文件大小和查询时间。
8. 检查是否产生过多小文件。

## 十一、今日输出

```text
data/processed/daily_prices/
src/save_partitioned_prices.py
reports/storage_query_comparison.md
```

## 十二、检查清单

- [ ] 股票代码保持字符串类型。
- [ ] 交易日期保持日期类型。
- [ ] Parquet 行数与原始数据一致。
- [ ] 分区目录能被 DuckDB 识别。
- [ ] 查询包含分区字段。
- [ ] 查询只读取必要字段。
- [ ] 没有产生过多细碎文件。
