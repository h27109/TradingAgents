import functools
import time
import json


async def create_trader(llm, memory):
    async def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        history_analysis_report = state.get("history_analysis_report", "")

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = await memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        context = {
            "role": "user",
            "content": f"""基于分析师团队的全面分析,这里为{company_name}定制了一份投资计划。
                        该计划整合了当前技术市场趋势、宏观经济指标和社交媒体情绪的见解。
                        请以此计划作为评估您下一个交易决策的基础
                        分析的目的是作中长期投资，可以短期接受一定的损失波动。
                        建议的投资计划: {investment_plan}
                        请利用这些见解做出明智和战略性的决定。
            """
        }

        messages = []
        
        # 构建system消息，包含历史分析和基本指令
        system_content = "您是一位交易员,负责分析市场数据以做出投资决策。"
        
        if history_analysis_report.strip():
            system_content += (
                "\n\n以下为你的历史自评摘要（你此前在同一标的上的'最终交易决策'精炼回顾，仅用于策略校准）：\n"
                f"{history_analysis_report}\n"
                "请在新的判断中：明确'相对上次的策略调整点与权重变化'，并保持最终格式：\n"
                "最终交易建议: **买入/持有/卖出**"
            )
        
        system_content += (
            f"\n\n根据您的分析,提供一个具体的建议,买入、持有或卖出。"
            f"最后以坚定的决策结束,并在您的回复中始终以'最终交易建议: **买入/持有/卖出**'来确认您的建议。"
            f"不要忘记利用过去决策的教训来吸取经验。以下是一些类似情况的反思和经验教训: {past_memory_str}"
        )

        messages.extend([
            {
                "role": "system",
                "content": system_content,
            },
            context,
        ])

        result = await llm.ainvoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
