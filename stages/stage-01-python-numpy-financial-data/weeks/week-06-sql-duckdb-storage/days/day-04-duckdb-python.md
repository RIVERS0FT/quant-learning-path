# 第 6 周第 4 天：DuckDB 与 Python 集成

## 今日目标

- 理解 DuckDB 为什么适合个人量化研究。
- 能直接查询 CSV、Parquet 和 pandas DataFrame。
- 能创建持久化 DuckDB 数据库。
- 能编写可复用的行情导入与查询函数。

## 一、为什么选择 DuckDB

DuckDB 是本地分析型数据库，适合个人量化研究的原因包括：

- 不需要单独启动数据库服务。
- 可以直接查询 CSV 和 Parquet。
- 可以直接查询 pandas DataFrame。
- 支持标准 SQL。
- 支持窗口函数和复杂聚合。
- 数据库可以保存为单个本地文件。
- 适合批量分析，不需要维护服务器。

DuckDB 更适合分析型任务，例如：

- 扫描大量历史行情。
- 按股票或日期聚合。
- 计算滚动指标。
- 读取 Parquet 数据湖。

## 二、安装依赖

```bash
pip install duckdb pandas pyarrow
```

依赖作用：

| 包 | 用途 |
|---|---|
| `duckdb` | 本地 SQL 查询引擎 |
| `pandas` | DataFrame 数据处理 |
| `pyarrow` | Parquet 读写支持 |

## 三、创建数据库连接

```python
import duckdb

connection = duckdb.connect("database/market.duckdb")
```

使用完成后关闭：

```python
connection.close()
```

推荐使用上下文管理器：

```python
import duckdb

with duckdb.connect("database/market.duckdb") as connection:
    result = connection.execute(
        "SELECT 1 AS value"
    ).fetchdf()

print(result)
```

上下文管理器可以保证程序结束时自动关闭连接。

## 四、直接查询 CSV

```python
import duckdb

query = """
SELECT *
FROM read_csv_auto('data/raw/daily_prices.csv')
LIMIT 10
"""

result = duckdb.sql(query).df()
print(result)
```

`read_csv_auto()` 会自动推断：

- 分隔符。
- 字段名称。
- 字段类型。
- 日期和数值格式。

在正式研究中，仍应检查自动推断结果，特别是：

- 股票代码是否被识别为整数。
- 日期是否被识别为日期类型。
- 成交量和成交额是否被识别为数值。

## 五、直接查询 Parquet

```python
query = """
SELECT
    trade_date,
    symbol,
    close
FROM read_parquet('data/processed/daily_prices/*.parquet')
WHERE symbol = '000001.SZ'
ORDER BY trade_date
"""

result = duckdb.sql(query).df()
```

Parquet 的优势：

- 只读取查询需要的列。
- 可以跳过不符合筛选条件的数据块。
- 保留日期和数值类型。
- 文件体积通常小于 CSV。

## 六、查询 pandas DataFrame

```python
import pandas as pd
import duckdb

prices = pd.read_csv(
    "data/raw/daily_prices.csv",
    parse_dates=["trade_date"],
)

result = duckdb.sql("""
    SELECT
        symbol,
        AVG(close) AS avg_close
    FROM prices
    GROUP BY symbol
    ORDER BY symbol
""").df()

print(result)
```

DuckDB 可以直接识别当前 Python 作用域中的 DataFrame 名称。

这种方式适合：

- 用 pandas 完成清洗后，使用 SQL 聚合。
- 对 pandas 结果做复杂连接。
- 逐步把 pandas 工作流迁移到 SQL。

## 七、创建持久化表

```python
import duckdb

with duckdb.connect("database/market.duckdb") as connection:
    connection.execute("""
        CREATE OR REPLACE TABLE daily_prices AS
        SELECT *
        FROM read_csv_auto(
            'data/raw/daily_prices.csv'
        )
    """)
```

创建完成后，可以直接查询：

```python
with duckdb.connect("database/market.duckdb") as connection:
    result = connection.execute("""
        SELECT
            trade_date,
            symbol,
            close
        FROM daily_prices
        WHERE symbol = ?
        ORDER BY trade_date
    """, ["000001.SZ"]).fetchdf()
```

## 八、参数化查询

不要直接把用户输入拼接到 SQL 中。

不推荐：

```python
query = f"""
SELECT *
FROM daily_prices
WHERE symbol = '{symbol}'
"""
```

推荐：

```python
query = """
SELECT *
FROM daily_prices
WHERE symbol = ?
"""

result = connection.execute(
    query,
    [symbol],
).fetchdf()
```

参数化查询的优点：

- 避免引号和转义问题。
- 降低 SQL 注入风险。
- 查询代码更清晰。

## 九、导入行情函数

```python
from pathlib import Path

import duckdb


def import_market_data(
    database_path: str | Path,
    source_path: str | Path,
) -> None:
    """将 CSV 行情导入 DuckDB。"""
    database_path = Path(database_path)
    source_path = Path(source_path)

    if not source_path.exists():
        raise FileNotFoundError(
            f"行情文件不存在: {source_path}"
        )

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with duckdb.connect(str(database_path)) as connection:
        connection.execute(
            """
            CREATE OR REPLACE TABLE daily_prices AS
            SELECT *
            FROM read_csv_auto(?)
            """,
            [str(source_path)],
        )
```

## 十、查询行情函数

```python
from pathlib import Path

import duckdb
import pandas as pd


def query_stock_prices(
    database_path: str | Path,
    symbol: str,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """查询指定股票和日期范围的日线行情。"""
    if start_date > end_date:
        raise ValueError("start_date 不能晚于 end_date")

    query = """
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
    WHERE symbol = ?
      AND trade_date BETWEEN ? AND ?
    ORDER BY trade_date
    """

    with duckdb.connect(str(database_path)) as connection:
        result = connection.execute(
            query,
            [symbol, start_date, end_date],
        ).fetchdf()

    return result
```

## 十一、常用 DuckDB 接口

```python
duckdb.connect()
connection.execute()
connection.sql()
connection.close()
fetchone()
fetchall()
fetchdf()
df()
```

### `fetchone()`

返回一行：

```python
row = connection.execute(
    "SELECT COUNT(*) FROM daily_prices"
).fetchone()
```

### `fetchall()`

返回所有行组成的列表：

```python
rows = connection.execute(
    "SELECT symbol FROM daily_prices LIMIT 10"
).fetchall()
```

### `fetchdf()`

返回 pandas DataFrame：

```python
frame = connection.execute(
    "SELECT * FROM daily_prices LIMIT 10"
).fetchdf()
```

## 十二、今日练习

1. 安装 DuckDB、pandas 和 pyarrow。
2. 连接内存数据库 `:memory:`。
3. 连接本地数据库文件。
4. 使用 SQL 查询 CSV。
5. 使用 SQL 查询 Parquet。
6. 使用 SQL 查询 pandas DataFrame。
7. 将 CSV 导入持久化表。
8. 编写参数化查询。
9. 实现 `import_market_data()`。
10. 实现 `query_stock_prices()`。

## 十三、今日输出

建议创建：

```text
src/import_market_data.py
src/query_market_data.py
database/market.duckdb
```

## 十四、检查清单

- [ ] DuckDB 可以正常连接本地数据库。
- [ ] 能直接查询 CSV 和 Parquet。
- [ ] 能将查询结果转换为 DataFrame。
- [ ] 查询函数使用参数化 SQL。
- [ ] 查询结果按交易日期排序。
- [ ] 文件不存在时能够给出明确错误。
- [ ] 日期范围错误时能够提前检查。
