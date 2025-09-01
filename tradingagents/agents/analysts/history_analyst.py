import functools
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

async def create_history_analyst(llm, config: Dict[str, Any]):
    async def history_analyst_node(state, name):
        ticker: str = state["company_of_interest"]
        analysis_date_str: str = state["trade_date"]

        results_root = Path(config.get("results_dir", "./results"))
        max_days = int(config.get("history_review_max_days", 10))

        try:
            analysis_date = datetime.strptime(analysis_date_str, "%Y-%m-%d").date()
        except Exception:
            # 无法解析日期则直接返回空字典
            return {"history_analysis_report": json.dumps({}, ensure_ascii=False)}

        def read_latest_report_for_day(day_str: str) -> str:
            """读取指定日期的完整分析报告内容"""
            ticker_root = results_root / ticker
            if not ticker_root.exists() or not ticker_root.is_dir():
                return ""
            
            date_prefix = f"{day_str}-"
            day_dirs = [p for p in ticker_root.iterdir() if p.is_dir() and p.name.startswith(date_prefix)]
            if not day_dirs:
                return ""
            
            # 获取当天的最新目录
            latest_dir = sorted(day_dirs, key=lambda p: p.name)[-1]
            
            # 读取最终交易决策
            final_decision_file = latest_dir / "最终交易决策.md"
            if not final_decision_file.exists():
                final_decision_file = latest_dir / "final_trade_decision.md"
            
            if not final_decision_file.exists():
                return ""
                
            try:
                return final_decision_file.read_text(encoding="utf-8")
            except Exception:
                return ""

        # 收集最近10天的分析报告
        daily_summaries: Dict[str, str] = {}
        
        for i in range(1, max_days + 1):
            day = analysis_date - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            report_content = read_latest_report_for_day(day_str)
            
            if report_content:
                try:
                    # 构建针对单日报告的总结提示
                    prompt = f"""您是一位专业的历史数据分析员,负责总结 {ticker} 的历史交易决策报告。

**总结目标**:
为当前交易决策提供历史参考,帮助交易团队了解该标的的历史表现和决策模式。

**报告内容**:
{report_content}

**总结要求**:
1. 交易建议: 明确指出历史报告中的交易建议（买入/持有/卖出）
2. 置信度: 提取报告中提到的置信度水平（如百分比）
3. 核心逻辑: 用1-2句话概括最重要的决策理由
4. 简洁明了: 总结控制在200字符以内

**输出格式**:
请用中文直接输出总结内容,无需额外说明。"""

                    # 使用LLM生成单日总结
                    response = await llm.ainvoke(prompt)
                    daily_summary = response.content if hasattr(response, 'content') else str(response)
                    
                    # 清理总结内容
                    daily_summary = daily_summary.strip()
                    if daily_summary:
                        daily_summaries[day_str] = daily_summary
                        
                except Exception:
                    # LLM调用失败，跳过该天
                    continue

        # 返回字典格式的总结，如果没有数据则返回空字典
        return {
            "history_analysis_report": json.dumps(daily_summaries, ensure_ascii=False)
        }

    return functools.partial(history_analyst_node, name="History Analyst")