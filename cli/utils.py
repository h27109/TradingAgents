import os
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm

from cli.models import AnalystType

console = Console()

# 定义分析师顺序
ANALYST_ORDER = [
    ("Market Analyst", AnalystType.MARKET),
    ("Macro Data Analyst", AnalystType.MACRO_DATA),
    ("News Analyst", AnalystType.NEWS),
    ("Fundamentals Analyst", AnalystType.FUNDAMENTALS),
]

def get_ticker() -> str:
    """获取股票代码"""
    ticker = Prompt.ask("请输入要分析的股票代码", default="002466.SZ")
    if not ticker:
        console.print("\n[red]未提供股票代码。退出...[/red]")
        exit(1)
    return ticker.strip().upper()

def get_analysis_date() -> str:
    """获取分析日期"""
    import re
    from datetime import datetime

    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            # 确保日期不在未来
            if date_obj.date() > datetime.now().date():
                console.print("[red]错误：分析日期不能在未来[/red]")
                return False
            return True
        except ValueError:
            return False

    default_date = datetime.now().strftime("%Y-%m-%d")
    while True:
        date = Prompt.ask("请输入分析日期 (YYYY-MM-DD)", default=default_date)
        if validate_date(date.strip()):
            return date.strip()
        console.print("[red]请输入有效的日期格式 YYYY-MM-DD[/red]")

def select_analysts() -> List[AnalystType]:
    """选择分析师"""
    console.print("\n[bold]选择您的分析师团队:[/bold]")
    console.print("(使用空格选择/取消选择，至少选择一个)")
    
    selected = []
    for display, value in ANALYST_ORDER:
        if Confirm.ask(f"添加 {display}?", default=True):
            selected.append(value)
    
    if not selected:
        console.print("\n[red]未选择分析师。退出...[/red]")
        exit(1)
    
    return selected

def select_research_depth() -> int:
    """选择研究深度"""
    console.print("\n[bold]选择研究深度:[/bold]")
    
    DEPTH_OPTIONS = [
        ("1: 浅度 - 快速研究，较少的辩论和策略讨论轮次", 1),
        ("2: 中度 - 适中的辩论轮次和策略讨论", 3),
        ("3: 深度 - 全面研究，深入的辩论和策略讨论", 5),
    ]
    
    for i, (display, _) in enumerate(DEPTH_OPTIONS):
        console.print(f"[cyan]{display}[/cyan]")
    
    while True:
        choice = Prompt.ask("请选择研究深度 (1-3)", default="2")
        if choice in ["1", "2", "3"]:
            return DEPTH_OPTIONS[int(choice) - 1][1]
        console.print("[red]请输入有效的选项 (1-3)[/red]")
