import time
import json


def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        history = state["investment_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        investment_debate_state = state["investment_debate_state"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""作为投资组合经理和辩论主持人,您的职责是对本轮辩论进行严格评估,并做出明确的决定:与空头分析师保持一致、与多头分析师保持一致,或者仅在有充分理由的情况下选择持有。

简明扼要地总结双方的关键观点,重点关注最有说服力的证据或推理。您的建议—买入、卖出或持有—必须清晰明确且可执行。不要仅仅因为双方都有合理的观点就默认选择持有;要基于辩论中最有力的论据做出坚定的立场。

此外,为交易者制定详细的投资计划。这应该包括:

您的建议: 由最有说服力的论据支持的明确立场。
理由: 解释为什么这些论据导致您的结论。
战略行动: 实施建议的具体步骤。
考虑您在类似情况下的过往错误。利用这些见解来改进您的决策,确保您在学习和进步。以自然对话的方式呈现您的分析,不需要特殊格式。

以下是您过去对错误的反思:
\"{past_memory_str}\"

以下是辩论内容:
辩论历史:
{history}"""
        response = llm.invoke(prompt)

        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node
