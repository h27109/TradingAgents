from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

async def create_macro_data_analyst(llm, mcp_client, search_tool):
    async def macro_data_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        try:
            mcp_tools = await mcp_client.get_tools()
        except Exception as e:
            print(f"警告: 获取社交媒体分析 MCP 工具失败: {e}")
            mcp_tools = []
        tools = list(mcp_tools) + [search_tool]

        system_message = (
            """您是一位专业的宏观经济数据分析师,负责分析宏观经济指标、政策变化、利率环境、通胀数据、GDP增长、就业市场、国际贸易等宏观因素对特定公司及所在行业的影响。
             您将获得一个公司的名称,您的目标是撰写一份全面的宏观分析报告,详细说明宏观经济环境对该公司的影响、潜在风险和投资机会。
             这份报告需要基于以下宏观数据维度进行分析：
             1. 货币政策与利率环境：央行政策、利率变化、流动性状况
             2. 通胀数据：CPI、PPI、通胀预期及其对企业成本的影响
             3. 经济增长指标：GDP增长率、PMI、工业产值等
             4. 就业与消费：就业数据、消费者信心、零售销售
             5. 国际贸易：汇率变化、贸易数据、地缘政治影响
             6. 行业周期：所处行业的宏观经济敏感度分析
             7. 股市整体行情：大盘指数走势、市场估值水平、资金流向、板块轮动、市场情绪指标、技术指标（如RSI、MACD在指数层面的表现）
             请结合最新的宏观经济数据和政策动向,提供深入的分析和前瞻性的见解,帮助交易者理解宏观环境对该公司股票价格的潜在影响。
             请确保在报告末尾附上一个Markdown表格,总结关键宏观指标、未来走势预测和对该公司的潜在影响程度。
             请用中文回复，输出文档时请用UTF-8编码。"""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "您是一个专业的宏观经济数据分析师,专注于提供宏观经济环境的深度分析和走势预测。"
                    "您的职责是分析宏观经济数据和政策环境,为其他分析师和研究员提供宏观背景支持。"
                    "请使用提供的工具收集和分析宏观经济数据,重点关注经济周期、政策变化和市场环境的未来走向。"
                    "不需要提供具体的买入卖出建议,而是提供宏观环境的客观分析和前瞻性判断。"
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
            "macro_report": report,
        }

    return macro_data_analyst_node
