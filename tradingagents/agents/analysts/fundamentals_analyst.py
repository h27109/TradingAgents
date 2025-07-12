from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from utils import Toolkit
import utils.tushare_mcp as tushare_mcp

def create_fundamentals_analyst(llm, toolkit: Toolkit):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_fundamentals_openai]
        else:
            tools = [
                # toolkit.get_finnhub_company_insider_sentiment,
                # toolkit.get_finnhub_company_insider_transactions,
                # toolkit.get_simfin_balance_sheet,
                # toolkit.get_simfin_cashflow,
                # toolkit.get_simfin_income_stmt,
                tushare_mcp.get_tools(),
            ]

        system_message = (
            "您是一位研究员,负责分析过去一周某公司的基本面信息。请撰写一份全面的公司基本面信息报告,包括财务文件、公司简介、基本财务数据、公司财务历史、内部人士情绪和内部交易等,以全面了解公司的基本面信息,为交易者提供参考。请务必尽可能详细。不要简单地说趋势好坏参半,而是要提供详细和细致的分析见解,帮助交易者做出决策。"
            + " 请在报告末尾附上一个 Markdown 表格,以组织和整理报告中的要点,使其易于阅读。"
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
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
