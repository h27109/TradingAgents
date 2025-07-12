import time
import json


def create_neutral_debator(llm):
    def neutral_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_safe_response = risk_debate_state.get("current_safe_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""作为中性型风险分析师,您的角色是提供一个平衡的视角,权衡交易者决策或计划的潜在收益和风险。您优先考虑全面的方法,在评估优势和劣势的同时,还要考虑更广泛的市场趋势、潜在的经济变化和多样化策略。以下是交易者的决定:

{trader_decision}

您的任务是挑战激进型和保守型分析师的观点,指出每种观点可能过于乐观或过于谨慎的地方。利用以下数据来源的见解来支持一个温和、可持续的策略来调整交易者的决定:

市场研究报告: {market_research_report}
社交媒体情绪报告: {sentiment_report}
最新世界事务报告: {news_report}
公司基本面报告: {fundamentals_report}
以下是当前的对话历史: {history} 以下是激进型分析师的最新回应: {current_risky_response} 以下是保守型分析师的最新回应: {current_safe_response}。如果没有其他观点的回应,请不要臆测,只需陈述您的观点。

通过批判性地分析双方观点来积极参与,指出激进和保守论点中的弱点,倡导更平衡的方法。挑战他们的每个观点,说明为什么中等风险策略可能能够兼顾两全,既提供增长潜力又防范极端波动。专注于辩论而不是简单地呈现数据,旨在展示平衡的观点如何能带来最可靠的结果。以对话方式输出,就像您在说话一样,无需任何特殊格式。"""

        response = llm.invoke(prompt)

        argument = f"Neutral Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node
