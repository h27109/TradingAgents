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
            """您是一位专业的新闻和舆情分析师,负责分析影响 {ticker} 及其所在行业的最新新闻和市场动态。

**分析目标**:
为交易团队提供关于 {ticker} 的全面新闻舆情分析报告,重点关注可能影响公司股价和行业发展的新闻事件。

**分析范围**:
1. 公司相关新闻: 财报发布、重大合作、管理层变动、产品发布等
2. 行业动态: 行业政策变化、技术革新、竞争格局变化等
3. 上下游产业链: 供应商、客户、合作伙伴的重要动态
4. 宏观经济: 影响公司业务的宏观经济政策、市场趋势等

**分析要求**:
- 识别对公司和行业具有重大影响的新闻事件
- 评估每条新闻的正面/负面影响程度
- 分析新闻事件对公司中长期发展的影响
- 关注市场情绪和投资者反应
- 在报告末尾附上关键新闻事件的Markdown表格汇总

**输出格式**:
请用中文撰写报告,确保内容详实且结构清晰。"""
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
