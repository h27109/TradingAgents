# TradingAgents/graph/setup.py

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_tavily import TavilySearch

from tradingagents.agents import *
from tradingagents.agents.utils.agent_states import AgentState
from tradingagents.agents.utils.agent_utils import create_msg_delete
from tradingagents.agents.mcp_server.mcp_servers import McpServers

from .conditional_logic import ConditionalLogic


class GraphSetup:
    """Handles the setup and configuration of the agent graph."""

    def __init__(
        self,
        quick_thinking_llm: ChatOpenAI,
        deep_thinking_llm: ChatOpenAI,
        bull_memory,
        bear_memory,
        trader_memory,
        invest_judge_memory,
        risk_manager_memory,
        conditional_logic: ConditionalLogic,
        mcp_servers: McpServers,
        search_tool: TavilySearch,
        config: Dict[str, Any],
    ):
        """Initialize with required components."""
        self.quick_thinking_llm = quick_thinking_llm
        self.deep_thinking_llm = deep_thinking_llm
        self.bull_memory = bull_memory
        self.bear_memory = bear_memory
        self.trader_memory = trader_memory
        self.invest_judge_memory = invest_judge_memory
        self.risk_manager_memory = risk_manager_memory
        self.conditional_logic = conditional_logic
        self.mcp_servers = mcp_servers
        self.search_tool = search_tool
        self.config = config

    async def setup_graph(
        self, selected_analysts=["market", "macro_data", "news", "fundamentals"]
    ):
        """Set up and compile the agent workflow graph.

        Args:
            selected_analysts (list): List of analyst types to include. Options are:
                - "market": Market analyst
                - "macro_data": Macro data analyst
                - "news": News analyst
                - "fundamentals": Fundamentals analyst
        """

        if len(selected_analysts) == 0:
            raise ValueError("Trading Agents Graph Setup Error: no analysts selected!")
        
        # MCP初始化失败时直接报错并退出
        try:
            await self.mcp_servers.init_all_client()
        except Exception as e:
            raise RuntimeError(f"MCP服务器初始化失败，无法继续执行。错误详情: {type(e).__name__}: {e}") from e

        # 检查并报告无法访问的MCP服务
        unavailable_servers = []
        for server_name, client in self.mcp_servers.clients.items():
            try:
                await client.get_tools()
            except Exception as e:
                # 提取关键错误信息，避免输出完整的异常组
                error_msg = f"{type(e).__name__}: {str(e)}".split('\n')[0]  # 只取第一行
                unavailable_servers.append(f"{server_name}: {error_msg}")
        
        if unavailable_servers:
            error_details = "; ".join(unavailable_servers)
            raise RuntimeError(f"以下MCP服务器无法访问: {error_details}。为确保分析结果的准确性，程序将退出。")

        # Create analyst nodes
        analyst_nodes = {}
        delete_nodes = {}
        tool_nodes = {}

        # 创建可用的分析师节点
        if "market" in selected_analysts:
            try:
                analyst_nodes["market"] = await create_market_analyst(
                    self.quick_thinking_llm, self.mcp_servers.get_client("market"), self.search_tool
                )
                delete_nodes["market"] = await create_msg_delete()
                tools = await self.mcp_servers.get_client("market").get_tools() + [self.search_tool]
                tool_nodes["market"] = ToolNode(tools)
            except Exception as e:
                print(f"警告: 无法创建Market Analyst节点: {type(e).__name__}: {str(e).split(chr(10))[0]}")
                # 从selected_analysts中移除，避免后续处理
                selected_analysts = [a for a in selected_analysts if a != "market"]

        if "macro_data" in selected_analysts:
            try:
                analyst_nodes["macro_data"] = await create_macro_data_analyst(
                    self.quick_thinking_llm, self.mcp_servers.get_client("macro_data"), self.search_tool
                )
                delete_nodes["macro_data"] = await create_msg_delete()
                tools = await self.mcp_servers.get_client("macro_data").get_tools() + [self.search_tool]
                tool_nodes["macro_data"] = ToolNode(tools)
            except Exception as e:
                print(f"警告: 无法创建Macro Data Analyst节点: {type(e).__name__}: {str(e).split(chr(10))[0]}")
                # 从selected_analysts中移除，避免后续处理
                selected_analysts = [a for a in selected_analysts if a != "macro_data"]

        if "news" in selected_analysts:
            try:
                analyst_nodes["news"] = await create_news_analyst(
                    self.quick_thinking_llm, self.mcp_servers.get_client("news"), self.search_tool
                )
                delete_nodes["news"] = await create_msg_delete()
                tools = await self.mcp_servers.get_client("news").get_tools() + [self.search_tool]
                tool_nodes["news"] = ToolNode(tools)
            except Exception as e:
                print(f"警告: 无法创建News Analyst节点: {type(e).__name__}: {str(e).split(chr(10))[0]}")
                # 从selected_analysts中移除，避免后续处理
                selected_analysts = [a for a in selected_analysts if a != "news"]

        if "fundamentals" in selected_analysts:
            try:
                analyst_nodes["fundamentals"] = await create_fundamentals_analyst(
                    self.quick_thinking_llm, self.mcp_servers.get_client("financial"), self.search_tool
                )
                delete_nodes["fundamentals"] = await create_msg_delete()
                tools = await self.mcp_servers.get_client("financial").get_tools() + [self.search_tool]
                tool_nodes["fundamentals"] = ToolNode(tools)
            except Exception as e:
                print(f"警告: 无法创建Fundamentals Analyst节点: {type(e).__name__}: {str(e).split(chr(10))[0]}")
                # 从selected_analysts中移除，避免后续处理
                selected_analysts = [a for a in selected_analysts if a != "fundamentals"]

        # 检查是否有可用的分析师
        if len(analyst_nodes) == 0:
            raise RuntimeError("没有可用的分析师节点，无法继续执行。")

        # Create researcher and manager nodes
        bull_researcher_node = await create_bull_researcher(
            self.quick_thinking_llm, self.bull_memory
        )
        bear_researcher_node = await create_bear_researcher(
            self.quick_thinking_llm, self.bear_memory
        )
        research_manager_node = await create_research_manager(
            self.deep_thinking_llm, self.invest_judge_memory
        )
        # History analyst: 回顾近10天历史分析
        history_analyst_node = await create_history_analyst(self.quick_thinking_llm, self.config)
        trader_node = await create_trader(self.quick_thinking_llm, self.trader_memory)

        # Create risk analysis nodes
        risky_analyst = await create_risky_debator(self.quick_thinking_llm)
        neutral_analyst = await create_neutral_debator(self.quick_thinking_llm)
        safe_analyst = await create_safe_debator(self.quick_thinking_llm)
        risk_manager_node = await create_risk_manager(
            self.deep_thinking_llm, self.risk_manager_memory
        )

        # Create workflow
        workflow = StateGraph(AgentState)

        # Add analyst nodes to the graph
        for analyst_type, node in analyst_nodes.items():
            workflow.add_node(f"{analyst_type.capitalize()} Analyst", node)
            workflow.add_node(
                f"Msg Clear {analyst_type.capitalize()}", delete_nodes[analyst_type]
            )
            # 确保只有在tool_nodes中存在对应条目时才添加工具节点
            if analyst_type in tool_nodes:
                workflow.add_node(f"tools_{analyst_type}", tool_nodes[analyst_type])

        # Add other nodes
        workflow.add_node("Bull Researcher", bull_researcher_node)
        workflow.add_node("Bear Researcher", bear_researcher_node)
        workflow.add_node("Research Manager", research_manager_node)
        workflow.add_node("History Analyst", history_analyst_node)
        workflow.add_node("Trader", trader_node)
        workflow.add_node("Risky Analyst", risky_analyst)
        workflow.add_node("Neutral Analyst", neutral_analyst)
        workflow.add_node("Safe Analyst", safe_analyst)
        workflow.add_node("Risk Judge", risk_manager_node)

        # Define edges
        # Start with the first available analyst
        available_analysts = [a for a in selected_analysts if a in analyst_nodes]
        if not available_analysts:
            raise RuntimeError("没有可用的分析师节点，无法构建工作流。")
            
        first_analyst = available_analysts[0]
        workflow.add_edge(START, f"{first_analyst.capitalize()} Analyst")

        # Connect analysts in sequence
        # 只连接实际创建成功的分析师节点
        for i, analyst_type in enumerate(available_analysts):
            current_analyst = f"{analyst_type.capitalize()} Analyst"
            current_tools = f"tools_{analyst_type}"
            current_clear = f"Msg Clear {analyst_type.capitalize()}"

            # Add conditional edges for current analyst
            # 只有当对应的工具节点存在时才添加条件边
            if analyst_type in tool_nodes:
                workflow.add_conditional_edges(
                    current_analyst,
                    getattr(self.conditional_logic, f"should_continue_{analyst_type}"),
                    [current_tools, current_clear],
                )
                workflow.add_edge(current_tools, current_analyst)
            else:
                # 如果没有工具节点，则直接连接到清理节点
                workflow.add_edge(current_analyst, current_clear)

            # Connect to next analyst or to Bull Researcher if this is the last analyst
            if i < len(available_analysts) - 1:
                next_analyst = f"{available_analysts[i+1].capitalize()} Analyst"
                workflow.add_edge(current_clear, next_analyst)
            else:
                workflow.add_edge(current_clear, "Bull Researcher")

        # Add remaining edges
        workflow.add_conditional_edges(
            "Bull Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bear Researcher": "Bear Researcher",
                "Research Manager": "Research Manager",
            },
        )
        workflow.add_conditional_edges(
            "Bear Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bull Researcher": "Bull Researcher",
                "Research Manager": "Research Manager",
            },
        )
        # 在交易员前插入历史分析
        workflow.add_edge("Research Manager", "History Analyst")
        workflow.add_edge("History Analyst", "Trader")
        workflow.add_edge("Trader", "Risky Analyst")
        workflow.add_conditional_edges(
            "Risky Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Safe Analyst": "Safe Analyst",
                "Risk Judge": "Risk Judge",
            },
        )
        workflow.add_conditional_edges(
            "Safe Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Neutral Analyst": "Neutral Analyst",
                "Risk Judge": "Risk Judge",
            },
        )
        workflow.add_conditional_edges(
            "Neutral Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Risky Analyst": "Risky Analyst",
                "Risk Judge": "Risk Judge",
            },
        )

        workflow.add_edge("Risk Judge", END)

        # Compile and return
        app = workflow.compile()

        app.get_graph().draw_mermaid_png(output_file_path="graph.png")
        
        return app
