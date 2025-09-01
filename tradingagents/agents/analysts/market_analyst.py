from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

async def create_market_analyst(llm, mcp_client, search_tool):

    async def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        try:
            mcp_tools = await mcp_client.get_tools()
        except Exception as e:
            print(f"警告: 获取市场分析 MCP 工具失败: {e}")
            mcp_tools = []
        tools = list(mcp_tools) + [search_tool]

        system_message = (
            """您是一位专业的市场技术分析师,负责分析 {ticker} 的技术指标和市场趋势,为交易团队提供技术分析报告。

**分析目标**:
为交易团队提供关于 {ticker} 的全面技术分析报告,重点关注价格趋势、技术指标信号和市场动量变化。

**分析方法**:
1. 从以下指标类别中选择最多8个最相关的指标进行分析:
   - 移动平均线: close_50_sma, close_200_sma, close_10_ema
   - MACD相关: macd, macds, macdh
   - 动量指标: rsi
   - 波动率指标: boll, boll_ub, boll_lb, atr
   - 成交量指标: vwma

2. 选择原则:
   - 选择能提供多样化和互补信息的指标
   - 避免功能重复的指标
   - 根据当前市场环境选择最合适的指标组合

**分析要求**:
- 详细分析所选指标的当前状态和信号
- 识别价格趋势、支撑阻力位和潜在买卖点
- 评估市场动量和波动性水平
- 结合多个指标信号进行综合判断
- 在报告末尾附上关键指标的Markdown表格汇总

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
            "market_report": report,
        }

    return market_analyst_node
