# TradingAgents/graph/trading_graph.py

import os
from pathlib import Path
import json
from datetime import date
from typing import Dict, Any, Tuple, List, Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from tradingagents.agents.mcp_server.mcp_servers import McpServers

from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.config import get_config
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)
from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor


class TradingAgentsGraph:
    """Main class that orchestrates the trading agents framework."""

    def __init__(
        self,
        selected_analysts=["market", "macro_data", "news", "fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
    ):
        """Initialize the trading agents graph and components.

        Args:
            selected_analysts: List of analyst types to include
            debug: Whether to run in debug mode
            config: Configuration dictionary. If None, uses default config
        """
        self.debug = debug
        self.config = config or get_config().to_dict()
        self.selected_analysts = selected_analysts

        # Create necessary directories
        project_dir = self.config.get("project_dir")
        os.makedirs(
            os.path.join(project_dir, "dataflows/data_cache"),
            exist_ok=True,
        )

        # Initialize LLMs
        llm_provider = self.config.get("llm_provider", "openai").lower()
        if llm_provider in ["openai", "ollama", "openrouter", "deepseek"]:
            self.deep_thinking_llm = ChatOpenAI(model=self.config.get("deep_think_llm"), 
                                                base_url=self.config.get("llm_api_url"),
                                                api_key = self.config.get("llm_api_key"))
            self.quick_thinking_llm = ChatOpenAI(model=self.config.get("quick_think_llm"), 
                                                base_url=self.config.get("llm_api_url"),
                                                api_key = self.config.get("llm_api_key"))
        elif llm_provider == "anthropic":
            self.deep_thinking_llm = ChatAnthropic(model=self.config.get("deep_think_llm"), base_url=self.config.get("backend_url"))
            self.quick_thinking_llm = ChatAnthropic(model=self.config.get("quick_think_llm"), base_url=self.config.get("backend_url"))
        elif llm_provider == "google":
            self.deep_thinking_llm = ChatGoogleGenerativeAI(model=self.config.get("deep_think_llm"))
            self.quick_thinking_llm = ChatGoogleGenerativeAI(model=self.config.get("quick_think_llm"))
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
        
        self.mcp_servers = McpServers()
        self.search_tool = TavilySearch()

        # Initialize memories
        self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
        self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory", self.config)

        # Initialize components
        self.conditional_logic = ConditionalLogic()
        self.graph_setup = GraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
            self.mcp_servers,
            self.search_tool,
            self.config,
        )

        self.propagator = Propagator()
        self.reflector = Reflector(self.quick_thinking_llm)
        self.signal_processor = SignalProcessor(self.quick_thinking_llm)

        # State tracking
        self.curr_state = None
        self.ticker = None
        self.log_states_dict = {}  # date to full state dict

        # Initialize graph as None, will be set up in async_init
        self.graph = None

    async def async_init(self):
        """Async initialization method to set up the graph."""
        if self.graph is None:
            # Set up the graph
            self.graph = await self.graph_setup.setup_graph(self.selected_analysts)

    async def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for different data sources."""
        tool_nodes = {}
        
        for source in ["market", "macro_data", "news", "fundamentals"]:
            try:
                tools = await self.mcp_server.get_client(source).get_tools()
                tool_nodes[source] = ToolNode(tools)
            except Exception as e:
                raise RuntimeError(f"{source} MCP工具获取失败: {e}") from e
        
        return tool_nodes

    async def propagate(self, company_name, trade_date, stream_output=True):
        """Run the trading agents graph for a company on a specific date with optional streaming output."""

        self.ticker = company_name

        # Initialize state
        init_agent_state = self.propagator.create_initial_state(
            company_name, trade_date
        )
        args = self.propagator.get_graph_args()

        if stream_output:
            # Streaming mode with real-time output
            print(f"\n🚀 开始分析 {company_name} 在 {trade_date} 的交易决策...")
            print("=" * 80)
            
            trace = []
            step_count = 0
            tool_usage = {}  # 记录工具使用统计
            
            async for chunk in self.graph.astream(init_agent_state, **args):
                step_count += 1
                
                if len(chunk["messages"]) > 0:
                    latest_message = chunk["messages"][-1]
                    
                    # 检查是否是工具调用
                    if hasattr(latest_message, 'tool_calls') and latest_message.tool_calls:
                        print(f"\n🔧 工具调用 (步骤 {step_count}):")
                        print("-" * 40)
                        
                        for tool_call in latest_message.tool_calls:
                            tool_name = tool_call.get('name', '未知工具')
                            tool_args = tool_call.get('args', {})
                            tool_id = tool_call.get('id', '未知ID')
                            
                            # 记录工具使用统计
                            if tool_name not in tool_usage:
                                tool_usage[tool_name] = 0
                            tool_usage[tool_name] += 1
                            
                            print(f"🛠️  工具名称: {tool_name}")
                            print(f"📝 工具ID: {tool_id}")
                            print(f"📋 参数:")
                            for key, value in tool_args.items():
                                # 格式化参数显示
                                if isinstance(value, str) and len(value) > 100:
                                    print(f"   {key}: {value[:100]}...")
                                else:
                                    print(f"   {key}: {value}")
                            print("-" * 20)
                    
                    # 检查是否有工具响应
                    if hasattr(latest_message, 'tool_call_id') and latest_message.tool_call_id:
                        print(f"📤 工具响应:")
                        print(f"   ID: {latest_message.tool_call_id}")
                        if hasattr(latest_message, 'content') and latest_message.content:
                            content = latest_message.content
                            # 格式化响应内容显示
                            if len(content) > 500:
                                print(f"   响应内容: {content[:250]}...")
                                print(f"   ... (内容过长，已截断)")
                            else:
                                print(f"   响应内容: {content}")
                        print("-" * 20)
                    
                    # 检查消息类型并输出相应的信息
                    if hasattr(latest_message, 'content') and latest_message.content and not hasattr(latest_message, 'tool_call_id'):
                        # 根据消息来源输出不同的标识
                        if "market_report" in chunk:
                            print(f"\n📊 市场分析师报告 (步骤 {step_count}):")
                            print("-" * 40)
                            print(latest_message.content[:200] + "..." if len(latest_message.content) > 200 else latest_message.content)
                        elif "sentiment_report" in chunk:
                            print(f"\n💬 社交媒体分析师报告 (步骤 {step_count}):")
                            print("-" * 40)
                            print(latest_message.content[:200] + "..." if len(latest_message.content) > 200 else latest_message.content)
                        elif "news_report" in chunk:
                            print(f"\n📰 新闻分析师报告 (步骤 {step_count}):")
                            print("-" * 40)
                            print(latest_message.content[:200] + "..." if len(latest_message.content) > 200 else latest_message.content)
                        elif "fundamentals_report" in chunk:
                            print(f"\n📈 基本面分析师报告 (步骤 {step_count}):")
                            print("-" * 40)
                            print(latest_message.content[:200] + "..." if len(latest_message.content) > 200 else latest_message.content)
                        elif "investment_debate_state" in chunk:
                            print(f"\n🤝 投资辩论 (步骤 {step_count}):")
                            print("-" * 40)
                            print(latest_message.content[:200] + "..." if len(latest_message.content) > 200 else latest_message.content)
                        elif "trader_investment_plan" in chunk:
                            print(f"\n💼 交易员投资计划 (步骤 {step_count}):")
                            print("-" * 40)
                            print(latest_message.content[:200] + "..." if len(latest_message.content) > 200 else latest_message.content)
                        elif "risk_debate_state" in chunk:
                            print(f"\n⚠️  风险管理讨论 (步骤 {step_count}):")
                            print("-" * 40)
                            print(latest_message.content[:200] + "..." if len(latest_message.content) > 200 else latest_message.content)
                        elif "final_trade_decision" in chunk:
                            print(f"\n🎯 最终交易决策 (步骤 {step_count}):")
                            print("-" * 40)
                            print(latest_message.content)
                            print("=" * 80)
                        else:
                            print(f"\n🔄 处理中 (步骤 {step_count}):")
                            print("-" * 40)
                            print(latest_message.content[:100] + "..." if len(latest_message.content) > 100 else latest_message.content)
                    
                    trace.append(chunk)
            
            final_state = trace[-1]
            print(f"\n✅ 分析完成！共执行了 {step_count} 个步骤。")
            
            # 显示工具使用统计
            if tool_usage:
                print(f"\n📊 工具使用统计:")
                print("-" * 40)
                for tool_name, count in tool_usage.items():
                    print(f"   {tool_name}: {count} 次")
                print("-" * 40)
            
        else:
            # Standard mode without streaming
            if self.debug:
                # Debug mode with tracing
                trace = []
                async for chunk in self.graph.astream(init_agent_state, **args):
                    if len(chunk["messages"]) == 0:
                        pass
                    else:
                        chunk["messages"][-1].pretty_print()
                        trace.append(chunk)

                final_state = trace[-1]
            else:
                # Standard mode without tracing
                final_state = await self.graph.ainvoke(init_agent_state, **args)

        # Store current state for reflection
        self.curr_state = final_state

        # Log state
        await self._log_state(trade_date, final_state)

        # Return decision and processed signal
        return final_state, await self.process_signal(final_state["final_trade_decision"])

    async def _log_state(self, trade_date, final_state):
        """Log the final state to a JSON file."""
        self.log_states_dict[str(trade_date)] = {
            "company_of_interest": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            "market_report": final_state["market_report"],
            "sentiment_report": final_state["sentiment_report"],
            "news_report": final_state["news_report"],
            "fundamentals_report": final_state["fundamentals_report"],
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"][
                    "current_response"
                ],
                "judge_decision": final_state["investment_debate_state"][
                    "judge_decision"
                ],
            },
            "trader_investment_decision": final_state["trader_investment_plan"],
            "risk_debate_state": {
                "risky_history": final_state["risk_debate_state"]["risky_history"],
                "safe_history": final_state["risk_debate_state"]["safe_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
        }

        # Save to file
        directory = Path(f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/full_states_log_{trade_date}.json",
            "w",
        ) as f:
            json.dump(self.log_states_dict, f, indent=4)

    async def reflect_and_remember(self, returns_losses):
        """Reflect on decisions and update memory based on returns."""
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    async def process_signal(self, full_signal):
        """Process the final trade decision into a signal."""
        return await self.signal_processor.process_signal(full_signal)
