# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

# 运行单个测试文件
python -m pytest path/to/test_file.py -v

# 运行特定测试类或方法
python -m pytest path/to/test_file.py::TestClass::test_method -v
```

## 架构概述

### 核心组件
- **TradingAgentsGraph**: 主协调器，负责整个工作流的协调，管理各智能体之间的通信和数据流转
- **AgentState**: 所有智能体的状态管理，包含分析结果、辩论记录和最终决策的统一状态存储
- **FinancialSituationMemory**: 使用 ChromaDB 的持久化记忆系统，用于学习历史决策并为未来决策提供参考
- **McpServers**: 通过模型上下文协议集成外部数据源，为各分析师提供实时或历史的市场、新闻、财务数据
- **LangGraph**: 多智能体协调和状态管理框架，负责定义智能体之间的依赖关系和执行顺序

### 智能体工作流
1. **分析师团队**（并行）：市场技术分析师、宏观经济分析师、新闻舆情分析师、基本面分析师、历史数据分析员同时进行各自领域的深度分析
2. **研究团队**：多头研究员（看涨观点）与空头研究员（看跌观点）基于分析师报告进行多轮辩论，研究经理负责协调辩论过程
3. **交易员**：整合所有分析师报告和辩论结果，制定具体的投资计划并做出买入/持有/卖出的决策
4. **风险管理**：激进、保守、中性三种不同风险偏好的辩论者对投资决策进行风险评估辩论
5. **投资组合经理**：最终决策批准，综合考虑所有分析报告、辩论结果和风险评估

### 高级架构说明
TradingAgents框架采用模块化设计，基于LangGraph构建，实现了多智能体协作的金融交易系统。整个系统分为以下几个主要模块：

1. **Graph模块** (`tradingagents/graph/`)
   - `trading_graph.py`: 主协调器，负责整个工作流的协调
   - `setup.py`: 智能体初始化和图构建
   - `propagation.py`: 状态管理和传播逻辑
   - `conditional_logic.py`: 条件逻辑处理
   - `reflection.py`: 反思和记忆更新机制
   - `signal_processing.py`: 信号处理

2. **Agents模块** (`tradingagents/agents/`)
   - `analysts/`: 各类分析师代理（市场、宏观、新闻、基本面）
        - `fundamentals_analyst`: 基本面分析师模块，专门分析公司的财务文件、业务模式、竞争优势和长期增长潜力，提供详细的财务指标分析和行业对比
        - `market_analyst`: 市场技术分析师模块，分析技术指标和市场趋势，从移动平均线、MACD、RSI等指标中选择最相关的组合进行综合技术分析
        - `news_analyst`: 新闻和舆情分析师模块，监控和分析影响公司及行业的最新新闻事件、政策变化和市场动态，评估每条新闻的正面/负面影响
        - `macro_data_analyst`: 宏观经济分析师模块，分析货币政策、通胀数据、经济增长指标等宏观经济因素对公司业务和行业发展的潜在影响
        - `history_analyst`: 历史数据分析员模块，收集和总结历史交易决策报告，为当前决策提供参考和策略校准
   - `researchers/`: 研究员代理（多头/空头研究员），分别从看涨和看跌角度分析公司投资价值，通过辩论形式形成更全面的投资观点
   - `managers/`: 管理代理（研究经理、风险经理），负责协调研究员辩论过程和风险管理评估
   - `trader/`: 交易员代理，整合所有分析师报告和历史决策数据，制定具体的投资计划并做出最终的买入/持有/卖出决策
   - `risk_mgmt/`: 风险管理代理，包含不同风险偏好的辩论者（激进、保守、中性），从多角度评估投资风险
   - `mcp_server/`: MCP服务器集成

3. **Utils模块** (`tradingagents/agents/utils/`)
   - `agent_states.py`: 智能体状态定义
   - `memory.py`: 记忆系统实现
   - `agent_utils.py`: 通用工具函数

4. **配置模块**
   - `config.py`: 环境配置管理
   - `mcp_servers_config.py`: MCP服务器配置

5. **CLI模块** (`cli/`)
   - `main.py`: 交互式命令行界面
   - `analyze.py`: 分析执行模块
   - `utils.py`: 工具函数

6. **Web模块** (`web/`)
   - `main.py`: Web接口主文件
   - `run.py`: Web服务运行脚本

### 关键配置
- `LLM_PROVIDER`: openai, anthropic, google, ollama, openrouter, deepseek
- `ONLINE_TOOLS=true`: 启用实时数据（需要 TAVILY_API_KEY, FINNHUB_API_KEY）
- `MAX_DEBATE_ROUNDS`: 控制研究辩论轮数
- `DEBUG_MODE=true`: 启用详细日志

### MCP服务器配置
TradingAgents通过MCP（Model Context Protocol）与外部数据源集成。MCP服务器配置定义在`tradingagents/mcp_servers_config.py`文件中，包含以下数据源：

1. **新闻数据源** (`news`):
   - weibo: 微博新闻数据
   - macro_china: 中国宏观经济数据
   - macro_international: 国际宏观经济数据
   - jin10_news: 金十新闻数据

2. **市场数据源** (`market`):
   - stock: 股票交易数据
   - stock_index: 股票指数数据

3. **财务数据源** (`financial`):
   - finance: 财务数据
   - fund: 基金数据

4. **宏观数据源** (`macro_data`):
   - macro_china: 中国宏观经济数据
   - macro_international: 国际宏观经济数据
   - stock_index: 股票指数数据
   - jin10_news: 金十新闻数据

每个MCP服务器配置包含:
- `transport`: 传输协议（streamable_http）
- `url`: 服务器地址
- `headers`: 请求头（如Authorization）
- `timeout`: 请求超时时间（秒）

### 目录结构
```
tradingagents/
├── graph/                 # LangGraph 编排
│   ├── trading_graph.py   # 主协调器
│   ├── setup.py          # 智能体初始化
│   └── propagation.py    # 状态管理
├── agents/
│   ├── analysts/         # 分析师团队（市场、宏观、新闻、基本面、历史分析）
│   ├── researchers/      # 研究员代理（多头/空头研究员）
│   ├── managers/         # 管理代理（研究经理、风险经理）
│   ├── trader/           # 交易员代理
│   ├── risk_mgmt/        # 风险管理代理（激进、保守、中性辩论者）
│   └── mcp_server/       # MCP服务器集成
├── config.py             # 环境配置
├── mcp_server_config.py  # 可用的MCP服务器配置
├── cli/main.py           # 交互式 CLI
└── web/                  # FastAPI Web 接口
```

### Web接口
TradingAgents提供基于FastAPI的Web接口，用户可以通过浏览器访问图形化界面进行分析。

启动Web服务：
```bash
# 方法1: 使用uvicorn直接运行
uvicorn web.main:app --host 0.0.0.0 --port 8000 --reload

# 方法2: 使用提供的运行脚本
python web/run.py
```

访问地址：http://localhost:8000

Web接口特性：
- 图形化用户界面
- 实时状态更新
- 消息日志显示
- 报告展示
- WebSocket通信

### 数据流
1. 输入：股票代码 + 分析日期
2. 通过 MCP 工具获取市场、新闻、财务等实时数据
3. 五个分析师（市场技术、宏观经济、新闻舆情、基本面、历史数据）并行进行深度分析
4. 多头研究员（看涨）与空头研究员（看跌）基于分析师报告进行多轮辩论
5. 交易员整合所有分析报告和辩论结果，制定投资计划并做出买入/持有/卖出决策
6. 风险管理团队（激进、保守、中性辩论者）对投资决策进行风险评估
7. 输出：最终交易信号 + 详细分析报告
8. 记忆系统更新以持续学习和优化 future decisions

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

### 性能和成本优化
TradingAgents框架在运行过程中会进行大量的API调用，这可能会产生较高的成本。为了优化性能和降低成本，建议：

1. **选择合适的LLM模型**：
   - 对于测试和开发，推荐使用成本较低的模型如`gpt-4o-mini`或`o4-mini`
   - 对于生产环境，可以根据需要选择性能更强的模型如`gpt-4o`或`o1-preview`

2. **控制辩论轮数**：
   - 通过调整`MAX_DEBATE_ROUNDS`和`MAX_RISK_DISCUSS_ROUNDS`配置项来控制研究辩论的轮数
   - 减少辩论轮数可以显著降低API调用次数

3. **使用离线工具**：
   - 设置`ONLINE_TOOLS=false`以使用缓存的离线数据，减少实时API调用
   - 离线工具依赖于Tauric TradingDB数据集

4. **监控API使用**：
   - 启用调试模式可以查看详细的API调用日志
   - 定期检查日志以了解API使用模式和成本

