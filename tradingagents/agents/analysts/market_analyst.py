from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_YFin_data_online,
                toolkit.get_stockstats_indicators_report_online,
            ]
        else:
            tools = [
                toolkit.get_YFin_data,
                toolkit.get_stockstats_indicators_report,
            ]

        system_message = (
            """您是一位负责分析金融市场的交易助手。您的职责是从以下列表中选择**最相关的指标**来分析给定的市场状况或交易策略。目标是选择最多**8个指标**,这些指标能提供互补的洞察而不重复。以下是指标类别及每个类别的具体指标:

移动平均线:
- close_50_sma: 50日简单移动平均线: 中期趋势指标。用途: 识别趋势方向并作为动态支撑/阻力位。提示: 它滞后于价格;需要与更快的指标结合使用以获得及时信号。
- close_200_sma: 200日简单移动平均线: 长期趋势基准。用途: 确认整体市场趋势并识别金叉/死叉形态。提示: 反应较慢;最适合用于战略性趋势确认而非频繁交易入场。
- close_10_ema: 10日指数移动平均线: 反应灵敏的短期均线。用途: 捕捉动量的快速变化和潜在入场点。提示: 在震荡市场中容易受噪音影响;需要与较长期均线一起使用来过滤虚假信号。

MACD相关指标:
- macd: MACD指标: 通过EMA差值计算动量。用途: 寻找趋势变化的交叉信号和背离。提示: 在低波动或横盘市场中需要其他指标确认。
- macds: MACD信号线: MACD线的EMA平滑。用途: 用与MACD线的交叉来触发交易。提示: 应作为更广泛策略的一部分以避免虚假信号。
- macdh: MACD柱状图: 显示MACD线与其信号线之间的差距。用途: 可视化动量强度并及早发现背离。提示: 可能波动较大;在快速市场中需要额外的过滤器配合。

动量指标:
- rsi: RSI相对强弱指标: 测量动量以标示超买/超卖状况。用途: 应用70/30阈值并观察背离来预示反转。提示: 在强势趋势中,RSI可能保持在极端水平;始终需要与趋势分析交叉验证。

波动率指标:
- boll: 布林带中线: 作为布林带基础的20日SMA。用途: 作为价格运动的动态基准。提示: 与上下轨一起使用可有效发现突破或反转。
- boll_ub: 布林带上轨: 通常是中线上方2个标准差。用途: 标示潜在超买条件和突破区域。提示: 需要其他工具确认信号;在强势趋势中价格可能沿带运行。
- boll_lb: 布林带下轨: 通常是中线下方2个标准差。用途: 指示潜在超卖条件。提示: 需要额外分析以避免虚假反转信号。
- atr: 真实波幅均值: 平均真实波幅来衡量波动性。用途: 设置止损位置并根据当前市场波动调整仓位大小。提示: 这是一个反应性指标,应作为更广泛风险管理策略的一部分。

基于成交量的指标:
- vwma: 成交量加权移动平均线: 由成交量加权的移动平均线。用途: 通过整合价格行为和成交量数据来确认趋势。提示: 注意成交量突增可能导致结果偏差;需要与其他成交量分析配合使用。

- 选择能提供多样化和互补信息的指标。避免重复(例如,不要同时选择rsi和stochrsi)。同时简要解释为什么这些指标适合给定的市场环境。当您调用工具时,请使用上面提供的指标的确切名称,因为这些是定义好的参数,否则您的调用将会失败。请确保首先调用get_YFin_data来获取生成指标所需的CSV数据。编写一份非常详细和细致的趋势观察报告。不要简单地说趋势好坏参半,而是提供详细和细致的分析见解,以帮助交易者做出决策。"""
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
            "market_report": report,
        }

    return market_analyst_node
