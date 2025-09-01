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
            """您是一位专业的宏观经济分析师,负责分析宏观经济环境对 {ticker} 及其所在行业的影响。

**分析目标**:
为交易团队提供关于 {ticker} 的全面宏观环境分析报告,帮助理解宏观经济因素对公司股价和行业发展的潜在影响。

**分析维度**:
1. 货币政策与利率环境: 央行政策、利率变化、流动性状况
2. 通胀数据: CPI、PPI、通胀预期及其对企业成本的影响
3. 经济增长指标: GDP增长率、PMI、工业产值等
4. 就业与消费: 就业数据、消费者信心、零售销售
5. 国际贸易: 汇率变化、贸易数据、地缘政治影响
6. 行业周期: 所处行业的宏观经济敏感度分析
7. 股市整体行情: 大盘指数走势、市场估值水平、资金流向、板块轮动

**分析要求**:
- 结合最新宏观经济数据和政策动向进行分析
- 评估宏观环境对公司业务的直接影响
- 识别潜在的宏观经济风险和投资机会
- 提供前瞻性判断和趋势预测
- 在报告末尾附上关键宏观指标的Markdown表格汇总

**输出格式**:
请用中文撰写报告,确保内容详实且结构清晰。"""
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
