from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

async def create_news_analyst(llm, mcp_client, search_tool):
    async def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        try:
            mcp_tools = await mcp_client.get_tools()
        except Exception as e:
            print(f"警告: 获取新闻分析 MCP 工具失败: {e}")
            mcp_tools = []
        tools = list(mcp_tools) + [search_tool]

        system_message = (
            """您是一位新闻研究员,负责分析过去一周的最新新闻和趋势。
            请撰写一份全面的报告,分析与交易和宏观经济相关的当前世界状况。
            重点以公司本身及行业及上下游行业，以及宏观经济中的重要事件，分析对公司和行业中长期的分析。
            不要简单地说趋势好坏参半,而是提供详细和细致的分析见解,以帮助交易者做出决策。
            请确保在报告末尾附上一个Markdown表格,以组织和整理报告中的要点,使其易于阅读。
            请用中文回复，输出文档时请用UTF-8编码。"""
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
            "news_report": report,
        }

    return news_analyst_node
