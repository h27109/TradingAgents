import functools
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

from langchain.memory import ConversationSummaryMemory

async def create_history_analyst(llm, config: Dict[str, Any]):
    async def history_analyst_node(state, name):
        ticker: str = state["company_of_interest"]
        analysis_date_str: str = state["trade_date"]

        results_root = Path(config.get("results_dir", "./results"))
        max_days = int(config.get("history_review_max_days", 10))

        try:
            analysis_date = datetime.strptime(analysis_date_str, "%Y-%m-%d").date()
        except Exception:
            # 无法解析日期则直接返回空报告
            return {"history_analysis_report": ""}

        def read_latest_report_for_day(day_str: str) -> str:
            # 新目录结构：results/<ticker>/<yyyy-mm-dd-HH-MM>
            ticker_root = results_root / ticker
            if not ticker_root.exists() or not ticker_root.is_dir():
                return ""
            # 过滤出以当天日期开头的目录，例如 2025-08-12-21-02
            date_prefix = f"{day_str}-"
            day_time_dirs: List[Path] = [p for p in ticker_root.iterdir() if p.is_dir() and p.name.startswith(date_prefix)]
            if not day_time_dirs:
                return ""
            # 取按名称排序的最后一个（时间最大的）
            latest_dir = sorted(day_time_dirs, key=lambda p: p.name)[-1]
            final_decision_file = latest_dir / "最终交易决策.md"
            if final_decision_file.exists():
                try:
                    return final_decision_file.read_text(encoding="utf-8")
                except Exception:
                    return ""
            # 兜底：尝试英文文件名
            fallback = latest_dir / "final_trade_decision.md"
            if fallback.exists():
                try:
                    return fallback.read_text(encoding="utf-8")
                except Exception:
                    return ""
            return ""

        def extract_recommendation_line(text: str) -> str:
            # 提取“最终交易建议: **买入/持有/卖出**”整行，若无则返回第一行摘要
            for line in text.splitlines():
                if re.search(r"最终交易建议[:：]", line):
                    return line.strip()
            # 兜底英文
            for line in text.splitlines():
                if re.search(r"Final\s*Trade\s*Advice", line, re.I):
                    return line.strip()
            # 再兜底：截取前100字
            return (text.strip()[:100] + "...") if text.strip() else ""

        history_lines: List[str] = []

        for i in range(1, max_days + 1):
            day = analysis_date - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            report_text = read_latest_report_for_day(day_str)
            if not report_text:
                continue
            rec_line = extract_recommendation_line(report_text) or "(未提取)"
            history_lines.append(f"{day_str}  {rec_line}")

        # 若没有历史，返回空字符串
        if not history_lines:
            return {"history_analysis_report": ""}

        # 使用 ConversationSummaryMemory 进行压缩摘要
        # 为确保摘要为中文，提示LLM输出中文
        memory = ConversationSummaryMemory(llm=llm, return_messages=False)
        for line in history_lines:
            # 将每条历史最终建议作为输入写入记忆，输出留空仅触发压缩
            memory.save_context({"input": line}, {"output": ""})

        variables = memory.load_memory_variables({})
        memory_summary = variables.get("history") or "\n".join(history_lines)

        header = (
            "历史自评摘要（你此前在同一标的上的‘最终交易决策’，最近≤10天，每天取最后一次）：\n"
        )

        # 若LLM可能输出英文，追加一个中文化兜底提示
        if re.search(r"[A-Za-z]", memory_summary) and not re.search(r"[\u4e00-\u9fa5]", memory_summary):
            memory_summary = "\n".join(history_lines)

        return {
            "history_analysis_report": f"{header}{memory_summary}",
        }

    return functools.partial(history_analyst_node, name="History Analyst")


