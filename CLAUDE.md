# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 提供在此代码库中工作的指导。

## 项目概述
TradingAgents 是一个多智能体 LLM 金融交易框架，通过专业化的智能体模拟真实交易公司的结构，包括分析、研究、交易和风险管理，使用 LangGraph 进行编排。

## 快速开始命令

### 安装与配置
```bash
# 克隆并安装依赖
uv sync
# 或者: pip install -e .

# 配置环境
cp .env.example .env
# 编辑 .env 文件，填入 API 密钥（至少需要 LLM_API_KEY 和 EMBEDDING_API_KEY）
```

### 运行系统
```bash
# 交互式 CLI
python -m cli.main

# 直接分析
python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.config import get_config
import asyncio
async def run():
    ta = TradingAgentsGraph(config=get_config().to_dict())
    await ta.async_init()
    _, decision = await ta.propagate('300130.SZ', '2024-05-10')
    print(decision)
asyncio.run(run())
"
```

### 开发命令
```bash
# 运行特定测试
python -m pytest test_history_analyst.py -v
python -m pytest test_llm_integration.py::TestLLMIntegration::test_specific_method -v

# 代码质量检查
black tradingagents/ cli/
isort tradingagents/ cli/
mypy tradingagents/
flake8 tradingagents/ --max-line-length=88 --ignore=E203,W503

# 完整测试套件
python -m pytest --cov=tradingagents --cov-report=html
```

## 架构概述

### 核心组件
- **TradingAgentsGraph**: 主协调器，负责整个工作流的协调
- **AgentState**: 所有智能体的状态管理，包含分析结果和决策
- **FinancialSituationMemory**: 使用 ChromaDB 的持久化记忆系统，用于学习历史决策
- **McpServers**: 通过模型上下文协议集成外部数据源
- **LangGraph**: 多智能体协调和状态管理

### 智能体工作流
1. **分析师团队**（并行）：市场、宏观数据、新闻、基本面、历史分析
2. **研究团队**：多头/空头研究员 + 研究经理辩论
3. **交易员**：制定投资计划
4. **风险管理**：风险评估辩论
5. **投资组合经理**：最终决策批准

### 关键配置
- `LLM_PROVIDER`: openai, anthropic, google, ollama, openrouter, deepseek
- `ONLINE_TOOLS=true`: 启用实时数据（需要 TAVILY_API_KEY, FINNHUB_API_KEY）
- `MAX_DEBATE_ROUNDS`: 控制研究辩论轮数
- `DEBUG_MODE=true`: 启用详细日志

### 目录结构
```
tradingagents/
├── graph/                 # LangGraph 编排
│   ├── trading_graph.py   # 主协调器
│   ├── setup.py          # 智能体初始化
│   └── propagation.py    # 状态管理
├── agents/
│   ├── analysts/         # 市场、宏观、新闻、基本面、历史分析
│   ├── researchers/      # 多头/空头研究员
│   ├── trader/           # 交易决策
│   ├── risk_mgmt/        # 风险评估
│   └── mcp_server/       # 外部数据工具
├── config.py             # 环境配置
├── mcp_server_config.py  # 可用的MCP服务器配置
├── cli/main.py           # 交互式 CLI
└── web/                  # FastAPI Web 接口
```

### 数据流
1. 输入：股票代码 + 分析日期
2. 通过 MCP 工具进行数据处理
3. 并行分析师评估
4. 研究辩论阶段
5. 交易决策 + 风险评估
6. 输出：最终信号 + 详细报告
7. 记忆更新以持续学习

### 自定义配置
```python
from tradingagents.config import get_config
config = get_config().to_dict()
config.update({
    "max_debate_rounds": 3,
    "deep_think_llm": "gpt-4",
    "selected_analysts": ["market", "fundamentals"]
})
```

### 调试
```bash
# 启用调试模式
DEBUG_MODE=true python -m cli.main

# 查看日志
tail -f eval_results/*/TradingAgentsStrategy_logs/*.log

# 监控 API 调用
LLM_PROVIDER=openai DEBUG_MODE=true python -c "..."
```