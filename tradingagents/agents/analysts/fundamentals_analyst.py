from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 基本面分析师
async def create_fundamentals_analyst(llm, mcp_client, search_tool):
    async def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        try:
            mcp_tools = await mcp_client.get_tools()
        except Exception as e:
            print(f"警告: 获取基本面分析 MCP 工具失败: {e}")
            mcp_tools = []
        tools = list(mcp_tools) + [search_tool]

        system_message = (
            """您是一位专业的基本面分析师,负责深入分析公司的财务状况和长期价值驱动因素。

**分析目标**:
为交易团队提供关于 {ticker} 的全面基本面分析报告,重点关注公司的财务健康状况、竞争优势和长期增长潜力。

**分析范围**:
1. 财务文件分析: 年报、季报、现金流报表等
2. 公司概况: 主营业务、市场地位、核心竞争力
3. 财务指标: 收入增长、利润率、负债水平、资产回报率等
4. 财务历史: 过去3-5年的财务趋势和关键变化
5. 内部人士情绪: 管理层信心、内部交易活动
6. 行业对比: 与同行业公司的财务表现对比

**报告要求**:
- 详细分析各项财务指标的变化趋势和原因
- 识别公司的核心竞争优势和潜在风险因素
- 提供基于数据的客观分析,避免模糊表述
- 在报告末尾附上关键财务指标的Markdown表格汇总
- 重点关注中长期投资价值,而非短期波动

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
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
