# 第 6 周每日学习路径

| 天 | 主题 | 学习与实践 | 当天输出 |
|---:|---|---|---|
| 1 | [数据库与 SQL 基础](day-01-sql-basics.md) | 表、字段、联合主键、筛选、排序和限制数量 | `basic_queries.sql` |
| 2 | [聚合、分组与统计查询](day-02-aggregation-groupby.md) | 聚合函数、`GROUP BY`、`WHERE` 与 `HAVING` | `aggregation_queries.sql` |
| 3 | [多表连接与数据建模](day-03-joins-data-modeling.md) | `INNER JOIN`、`LEFT JOIN`、连接键和重复检查 | `join_queries.sql` |
| 4 | [DuckDB 与 Python 集成](day-04-duckdb-python.md) | 查询 CSV、Parquet、DataFrame 和持久化数据库 | 行情导入与查询函数 |
| 5 | [窗口函数与金融时间序列](day-05-window-functions.md) | `LAG`、移动均线、滚动波动率和截面排名 | `factor_queries.sql` |
| 6 | [Parquet、分区与查询效率](day-06-parquet-partitioning.md) | 列式存储、年份分区、查询裁剪和性能对比 | 分区行情数据集 |
| 7 | [本地行情数据库综合项目](day-07-market-database-project.md) | 清洗、建库、视图、查询函数和测试 | `market.duckdb` |

## 本周核心 SQL

```sql
SELECT
FROM
WHERE
AND
OR
IN
BETWEEN
ORDER BY
LIMIT
DISTINCT
GROUP BY
HAVING
COUNT
SUM
AVG
MIN
MAX
CASE WHEN
INNER JOIN
LEFT JOIN
LAG
LEAD
ROW_NUMBER
RANK
DENSE_RANK
PARTITION BY
ROWS BETWEEN
CREATE TABLE
CREATE VIEW
```

优先掌握：

```text
SELECT
WHERE
GROUP BY
JOIN
窗口函数
```

## 本周核心 Python 接口

```python
duckdb.connect()
connection.execute()
connection.sql()
connection.close()
fetchone()
fetchall()
fetchdf()
pd.read_csv()
pd.read_parquet()
DataFrame.to_parquet()
pd.to_datetime()
DataFrame.drop_duplicates()
DataFrame.sort_values()
```

## pandas 与 SQL 对照

| pandas | SQL |
|---|---|
| 选择列 | `SELECT` |
| 布尔筛选 | `WHERE` |
| `sort_values()` | `ORDER BY` |
| `groupby()` | `GROUP BY` |
| `merge()` | `JOIN` |
| `shift()` | `LAG()` |
| `rolling()` | 窗口函数 |
| `rank()` | `RANK()` |
| `head()` | `LIMIT` |

## 本周检查清单

- [ ] 能查询指定股票和日期范围。
- [ ] 能区分时间序列统计和截面统计。
- [ ] 能解释 `WHERE` 与 `HAVING` 的区别。
- [ ] 多表连接使用完整连接键。
- [ ] 连接前后检查行数和联合主键重复。
- [ ] 收益率计算使用 `PARTITION BY symbol`。
- [ ] 截面排名使用 `PARTITION BY trade_date`。
- [ ] Parquet 数据按合理字段分区。
- [ ] 查询只读取需要的列和日期范围。
- [ ] DuckDB 查询结果可以转换为 DataFrame。
- [ ] 本地行情数据库和查询脚本可以重复运行。

## 本周最终成果

```text
data/processed/daily_prices/
database/market.duckdb
sql/basic_queries.sql
sql/aggregation_queries.sql
sql/join_queries.sql
sql/factor_queries.sql
src/import_market_data.py
src/query_market_data.py
tests/test_market_database.py
```
