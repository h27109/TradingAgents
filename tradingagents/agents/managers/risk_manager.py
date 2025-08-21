import time
import json


async def create_risk_manager(llm, memory):
    async def risk_manager_node(state) -> dict:

        company_name = state["company_of_interest"]

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["news_report"]
        macro_report = state["macro_report"]
        trader_plan = state["investment_plan"]

        curr_situation = f"{market_research_report}\n\n{macro_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = await memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""作为风险管理评判员和辩论主持人,您的目标是评估三位风险分析师(激进型、中性型和保守型)之间的辩论,并为交易者确定最佳行动方案。您的决定必须得出明确的建议:买入、卖出或持有。只有在有充分具体论据支持的情况下才选择持有,而不是在所有观点都似乎有效时作为退而求其次的选择。力求清晰和果断。

        决策指南:
        1. **总结关键论点**: 从每位分析师提取最有力的观点,重点关注与背景的相关性。
        2. **提供理由**: 用辩论中的直接引用和反驳论点来支持您的建议。
        3. **完善交易者计划**: 从交易者的原始计划 **{trader_plan}** 开始,根据分析师的见解进行调整。
        4. **从过去的错误中吸取教训**: 利用 **{past_memory_str}** 中的经验教训来纠正之前的判断失误,改进当前的决策,确保不会做出错误的买入/卖出/持有判断而造成损失。

        交付成果:
        - 明确且可执行的建议:买入、卖出或持有。
        - 基于辩论和过往反思的详细理由。

        ---

        **分析师辩论历史:**
        {history}

        ---

        专注于可执行的见解和持续改进。借鉴过往经验教训,批判性地评估所有观点,确保每个决定都能带来更好的结果。"""

        response = llm.invoke(prompt)

        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return risk_manager_node
