# 第 1 周每日学习路径

| 天 | 主题 | 学习与实践 | 当天输出 | 课程正文 |
|---:|---|---|---|---|
| 1 | Python 环境 | Python、虚拟环境、`pip`、编辑器和项目目录 | 可重复创建的项目环境 | [查看](day-01-python-environment.md) |
| 2 | 变量与数据类型 | 数值、字符串、布尔值、列表、元组、字典和类型转换 | 股票基础数据脚本 | [查看](day-02-variables-and-data-types.md) |
| 3 | 条件与循环 | `if`、`for`、`while`、`range`、`enumerate`、`zip` | 价格变化统计程序 | [查看](day-03-conditionals-and-loops.md) |
| 4 | 函数 | 参数、返回值、类型提示、文档字符串和输入校验 | 第一个收益率函数 | [查看](day-04-functions-and-return-calculation.md) |
| 5 | 异常与路径 | `try/except`、`pathlib`、上下文管理器和文件读写 | 安全价格文件读取器 | [查看](day-05-exceptions-paths-and-files.md) |
| 6 | Git 基础 | 工作区、暂存区、提交、差异检查和 `.gitignore` | 首次规范提交 | [查看](day-06-git-basics.md) |
| 7 | 综合项目 | 整合函数、文件输入、统计汇总、测试和 README | 单资产收益率工具 | [查看](day-07-week-project.md) |

## 本周核心公式

简单收益率：

$$
R_t=\frac{P_t}{P_{t-1}}-1
$$

累计收益率：

$$
R_{cum}=\prod_{t=1}^{n}(1+R_t)-1
$$

在无分红、拆股等公司行为时：

$$
R_{cum}=\frac{P_n}{P_0}-1
$$

## 完成状态

- [x] Python 环境与虚拟环境课程已完成；
- [x] Python 基础数据类型课程已完成；
- [x] 条件、循环与价格遍历课程已完成；
- [x] 收益率函数与参数校验课程已完成；
- [x] 异常、文件路径与读写课程已完成；
- [x] Git 基础与规范提交课程已完成；
- [x] 第一周综合项目与基础测试已完成。
