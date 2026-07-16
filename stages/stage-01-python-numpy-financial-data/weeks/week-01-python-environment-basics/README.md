# 第 1 周：Python 开发环境与基础语法

## 本周目标

完成从 Python 环境搭建到第一个可测试量化函数的完整入门流程。

本周结束时应能够：

- 创建并激活 Python 虚拟环境；
- 理解变量、数据类型、条件判断和循环；
- 编写带类型提示、文档字符串和参数校验的函数；
- 使用 `pathlib` 和异常处理安全读取文件；
- 使用 Git 检查、暂存和提交变化；
- 完成一个单资产收益率工具及基础测试。

## 本周学习安排

| 天 | 内容 | 预期产出 | 状态 |
|---:|---|---|---|
| 1 | Python 开发环境 | 可重复创建的项目环境 | [已完成](days/day-01-python-environment.md) |
| 2 | 变量与数据类型 | 股票基础数据脚本 | [已完成](days/day-02-variables-and-data-types.md) |
| 3 | 条件判断与循环 | 价格变化统计程序 | [已完成](days/day-03-conditionals-and-loops.md) |
| 4 | 函数 | 带校验的收益率函数 | [已完成](days/day-04-functions-and-return-calculation.md) |
| 5 | 异常、路径与文件 | 安全价格文件读取器 | [已完成](days/day-05-exceptions-paths-and-files.md) |
| 6 | Git 基础 | 首次规范提交 | [已完成](days/day-06-git-basics.md) |
| 7 | 综合项目 | 单资产收益率工具和测试 | [已完成](days/day-07-week-project.md) |

## 核心公式

简单收益率：

$$
R_t=\frac{P_t}{P_{t-1}}-1
$$

累计收益率：

$$
R_{cum}=\prod_{t=1}^{n}(1+R_t)-1
$$

## 核心成果

建立一个包含以下内容的基础量化研究项目：

```text
quant-research/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
├── src/
└── tests/
```

并完成：

- 价格文件读取；
- 简单收益率计算；
- 涨跌天数统计；
- 累计收益率计算；
- 输入校验和错误提示；
- 基础 `pytest` 测试。

## 每日入口

[查看第一周每日学习路径](days/README.md)

## 完成标准

- [x] 能独立创建、激活和退出虚拟环境；
- [x] 能解释基础 Python 数据类型；
- [x] 能使用条件和循环处理价格序列；
- [x] 能编写带参数校验的收益率函数；
- [x] 能安全读取价格文件并处理异常；
- [x] 能完成一次规范 Git 提交；
- [x] 综合项目通过基础单元测试。
