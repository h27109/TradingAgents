"""
异步分析模块，用于处理TradingAgentsGraph的异步初始化和运行
"""

import asyncio
import datetime
from pathlib import Path
from typing import List, Dict, Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from tradingagents.graph.trading_graph import TradingAgentsGraph
from cli.models import AnalystType

console = Console()

async def run_async_analysis(
    ticker: str,
    analysis_date: str,
    selected_analysts: List[AnalystType],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    运行异步分析
    
    Args:
        ticker: 股票代码
        analysis_date: 分析日期
        selected_analysts: 选择的分析师列表
        config: 配置字典
        
    Returns:
        Dict[str, Any]: 分析结果
    """
    # 创建结果目录（合并日期与时间：yyyy-mm-dd-HH-MM）
    date_time_dir = f"{analysis_date}-{datetime.datetime.now().strftime('%H-%M')}"
    results_dir = (Path(config.get("results_dir", "./results")) / ticker / date_time_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 显示初始信息
    console.print(f"[cyan]分析 {ticker} 在 {analysis_date}...[/cyan]")
    
    try:
        # 初始化交易代理图
        console.print("[cyan]初始化交易代理图...[/cyan]")
        graph = TradingAgentsGraph(
            [analyst.value for analyst in selected_analysts],
            config=config,
            debug=True
        )
        
        # 异步初始化图
        await graph.async_init()
        
        # 初始化状态和参数
        console.print("[cyan]创建初始状态...[/cyan]")
        init_agent_state = graph.propagator.create_initial_state(ticker, analysis_date)
        args = graph.propagator.get_graph_args()
        
        # 运行分析（使用流式输出）
        console.print("[cyan]开始流式分析...[/cyan]")
        final_state, processed_signal = await graph.propagate(ticker, analysis_date, stream_output=True)
        
        # 保存结果
        console.print("[green]分析完成！[/green]")
        # 英文段落键到中文文件名的映射
        chinese_filename_map = {
            "market_report": "市场分析.md",
            "sentiment_report": "社交情绪.md",
            "news_report": "新闻分析.md",
            "fundamentals_report": "基本面分析.md",
            "investment_plan": "研究团队决策.md",
            "trader_investment_plan": "交易团队计划.md",
            "final_trade_decision": "最终交易决策.md",
            "history_analysis_report": "历史分析报告.md",
        }

        for section_name, content in final_state.items():
            if isinstance(content, str) and content.strip():
                file_name = chinese_filename_map.get(section_name, f"{section_name}.md")
                with open(results_dir / file_name, "w", encoding="utf-8") as f:
                    f.write(content)
        
        console.print(f"[green]报告已保存到 {results_dir}[/green]")
        
        # 显示最终报告
        console.print("\n[bold green]分析报告[/bold green]\n")
        if "final_trade_decision" in final_state:
            console.print(Panel(
                Markdown(final_state["final_trade_decision"]),
                title=f"{ticker} 最终交易决定",
                border_style="green"
            ))
        
        return final_state
        
    except Exception as e:
        # 检查是否是MCP初始化失败
        if "MCP服务器初始化失败" in str(e) or "MCP客户端初始化失败" in str(e):
            console.print(f"[red]MCP初始化失败，无法继续执行: {str(e)}[/red]")
            console.print("[red]请检查MCP服务器配置和网络连接[/red]")
            return {}
        else:
            console.print(f"[red]分析过程中发生错误: {str(e)}[/red]")
            import traceback
            console.print(f"[red]{traceback.format_exc()}[/red]")
            return {}

def run_analysis(
    ticker: str,
    analysis_date: str,
    selected_analysts: List[AnalystType],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    同步包装函数，直接返回协程对象
    
    Args:
        ticker: 股票代码
        analysis_date: 分析日期
        selected_analysts: 选择的分析师列表
        config: 配置字典
        
    Returns:
        Dict[str, Any]: 分析结果
    """
    return run_async_analysis(ticker, analysis_date, selected_analysts, config) 