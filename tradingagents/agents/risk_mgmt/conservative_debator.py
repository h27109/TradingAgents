from langchain_core.messages import AIMessage
import time
import json


async def create_safe_debator(llm):
    async def safe_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        safe_history = risk_debate_state.get("safe_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""作为保守型风险分析师,您的首要目标是保护资产、降低波动性并确保稳定可靠的增长。
                您优先考虑稳定性、安全性和风险缓解,仔细评估潜在损失、经济衰退和市场波动。
                在评估交易者的决策或计划时,要严格审查高风险因素,指出决策可能使公司面临不必要风险的地方,以及更谨慎的替代方案如何能确保长期收益。
                以下是交易者的决定:
                {trader_decision}
                您的任务是积极反驳激进型和中性型分析师的论点,强调他们的观点可能忽视了潜在威胁或未能优先考虑可持续性。
                直接回应他们的观点,利用以下数据来源为交易者的决策构建一个令人信服的低风险方案:
                市场研究报告: {market_research_report}
                社交媒体情绪报告: {sentiment_report}
                最新世界事务报告: {news_report}
                公司基本面报告: {fundamentals_report}
                以下是当前的对话历史: {history} 以下是激进型分析师的最新回应: {current_risky_response} 以下是中性型分析师的最新回应: {current_neutral_response}。如果没有其他观点的回应,请不要臆测,只需陈述您的观点。
                通过质疑他们的乐观态度并强调他们可能忽视的潜在风险来参与讨论。
                针对他们的每个反驳点进行回应,展示为什么保守立场最终是公司资产的最安全路径。专注于辩论和批评他们的论点,以证明低风险策略相对于其他方法的优势。
                以对话方式输出,就像您在说话一样,无需任何特殊格式。"""

        response = llm.invoke(prompt)

        argument = f"Safe Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Safe",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return safe_node
