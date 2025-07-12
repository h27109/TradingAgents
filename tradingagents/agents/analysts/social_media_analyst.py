from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_social_media_analyst(llm, toolkit):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_stock_news_openai]
        else:
            tools = [
                toolkit.get_reddit_stock_info,
            ]

        system_message = (
            "您是一位社交媒体和公司新闻研究分析师,负责分析过去一周特定公司的社交媒体帖子、最新公司新闻和公众情绪。您将获得一个公司的名称,您的目标是撰写一份全面的长篇报告,详细说明您的分析、见解以及对交易者和投资者的启示。这份报告需要基于对该公司社交媒体内容、人们对该公司的评论、每日情绪数据分析以及最新公司新闻的研究。请尽可能查看所有来源,包括社交媒体、情绪数据和新闻。不要简单地说趋势好坏参半,而是要提供详细和细致的分析见解,以帮助交易者做出决策。"
            + """ 请确保在报告末尾附上一个Markdown表格,以组织和整理报告中的要点,使其易于阅读。"""
            + " 请用中文回复。",
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "您是一个乐于助人的AI助手,正在与其他助手合作。"
                    "请使用提供的工具来推进问题的解答。"
                    "如果您无法完全回答,没关系;另一个拥有不同工具的助手会接手您未完成的部分。请尽可能执行您能做的工作以取得进展。"
                    "如果您或其他任何助手有最终交易建议: **买入/持有/卖出**或可交付成果,"
                    "请在回复前加上'最终交易建议: **买入/持有/卖出**',以便团队知道可以停止。"
                    "您可以使用以下工具: {tool_names}。\n{system_message}"
                    "供您参考,当前日期是 {current_date}。我们要分析的公司是 {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return social_media_analyst_node
