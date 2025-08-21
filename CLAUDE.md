# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 提供在此代码库中工作的指导。

## 概述
TradingAgents 是一个多智能体 LLM 金融交易框架，模拟真实交易公司的结构，包含分析、研究、交易和风险管理等专门智能体。

## 快速开始

### 安装
```bash
# 克隆并设置
git clone https://github.com/h27109/TradingAgents.git
cd TradingAgents
checkout Chese_stock

# 安装依赖（使用 uv/pip）
uv sync  # 或: pip install -e .

# 配置环境
cp .env.example .env
# 编辑 .env 填入你的 API 密钥
```

### 基本命令

#### CLI 使用
```bash
# 交互式 CLI 与丰富界面
python -m cli.main

# 直接分析
python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.config import get_config
import asyncio

async def run():
    ta = TradingAgentsGraph(debug=True, config=get_config().to_dict())
    await ta.async_init()
    _, decision = await ta.propagate('300130.SZ', '2024-05-10')
    print(decision)

asyncio.run(run())
"
```

#### 配置
.env 中的关键配置参数：
- `LLM_PROVIDER`: openai, anthropic, google, ollama, openrouter, deepseek
- `LLM_API_KEY`: 你的 LLM API 密钥
- `EMBEDDING_API_KEY`: 嵌入模型 API 密钥
- `ONLINE_TOOLS=true`: 启用实时数据（需要 TAVILY_API_KEY, FINNHUB_API_KEY）

## 架构概览

### 核心组件
```
tradingagents/
├── graph/
│   ├── trading_graph.py      # 主协调器
│   ├── setup.py             # 图初始化
│   ├── propagation.py       # 状态管理
│   ├── reflection.py        # 内存更新
│   └── signal_processing.py # 最终信号处理
├── agents/
│   ├── analysts/            # 市场、宏观、新闻、基本面、历史分析
│   ├── researchers/         # 多头/空头研究员
│   ├── trader/              # 交易决策
│   ├── risk_mgmt/           # 风险评估
│   └── mcp_server/          # 工具集成
└── config.py               # 配置管理
```

### 智能体流程
1. **分析师团队**: 市场、宏观、新闻、基本面、历史分析回顾
2. **研究团队**: 多头/空头辩论与研究经理
3. **交易团队**: 投资计划创建
4. **风险管理**: 风险评估辩论
5. **投资组合管理**: 最终决策批准

### 关键类
- `TradingAgentsGraph`: 主入口点
- `AgentState`: 智能体状态管理
- `FinancialSituationMemory`: 智能体持久内存
- `McpServers`: 外部数据源集成

## 开发设置

### 运行测试
```bash
# 安装开发依赖
uv add --dev pytest black flake8 isort mypy

# 格式化代码
black tradingagents/ cli/
isort tradingagents/ cli/

# 类型检查
mypy tradingagents/
```

### 常见开发任务

#### 添加新分析师
1. 在 `tradingagents/agents/analysts/` 中创建智能体
2. 添加到 `tradingagents/graph/setup.py`
3. 在 CLI 中更新智能体选择

#### 自定义配置
```python
from tradingagents.config import get_config

config = get_config().to_dict()
config.update({
    "max_debate_rounds": 3,
    "online_tools": True,
    "deep_think_llm": "gpt-4",
    "quick_think_llm": "gpt-3.5-turbo"
})
```

#### 调试
```python
# 启用调试模式
config["debug_mode"] = True

# 检查日志在 eval_results/{ticker}/TradingAgentsStrategy_logs/
```

## API 使用模式

### 基础分析
```python
ta = TradingAgentsGraph(selected_analysts=["market", "fundamentals"])
await ta.async_init()
state, decision = await ta.propagate("300130.SZ", "2024-01-15")
```

### 高级配置
```python
# 自定义智能体选择
ta = TradingAgentsGraph(
    selected_analysts=["market", "macro_data", "news"],
    config={
        "llm_provider": "anthropic",
        "deep_think_llm": "claude-3-opus",
        "max_debate_rounds": 2
    }
)
```

## 文件结构
- `results/`: 分析输出
- `eval_results/`: 详细日志和状态
- `dataflows/data_cache/`: 缓存的市场数据
- `web/`: Web 界面（FastAPI）

## 重要说明
- 需要 Python 3.10+
- 使用 LangGraph 进行编排
- MCP 服务器用于外部数据
- 内存系统用于从过去决策中学习
- 非投资建议 - 仅为研究框架