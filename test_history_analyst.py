#!/usr/bin/env python3
"""
测试历史分析师功能
"""
import asyncio
import os
from pathlib import Path
from datetime import datetime, timedelta
from tradingagents.config import get_config
from tradingagents.agents.analysts.history_analyst import create_history_analyst

# 创建测试数据
def create_test_data():
    """创建测试用的历史报告数据"""
    test_ticker = "002466.SZ"
    test_date = datetime.now().strftime("%Y-%m-%d")
    
    # 创建测试目录
    test_dir = Path(f"./results/{test_ticker}/{test_date}-12-00")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建测试报告内容
    test_reports = [
        """# 最终交易决策

## 分析摘要
基于当前市场情况和技术分析，对天齐锂业(002466.SZ)做出如下评估：

## 关键发现
- 技术指标显示短期超卖状态
- 锂价近期有所回升
- 成交量温和放大

## 风险评估
- 行业周期性风险较高
- 需关注新能源政策变化

## 最终交易建议: **买入**

## 置信度: 75%

## 理由
1. 技术面出现底部信号
2. 基本面有改善预期
3. 市场情绪开始转暖

## 风险控制
- 建议分批建仓
- 设置止损位在-5%
""",
        """# 最终交易决策

## 分析摘要
今日天齐锂业股价震荡调整，整体表现偏弱

## 关键发现
- 股价跌破20日均线
- MACD出现死叉
- 成交量萎缩

## 最终交易建议: **持有**

## 置信度: 60%

## 理由
短期调整仍在合理范围内，等待明确方向信号
""",
        """# 最终交易决策

## 分析摘要
天齐锂业今日强势反弹，量价配合良好

## 关键发现
- 放量突破重要阻力位
- 资金流入明显
- 板块轮动效应

## 最终交易建议: **买入**

## 置信度: 85%

## 理由
技术突破有效，短期上涨空间打开
"""
    ]
    
    # 创建过去几天的测试数据
    for i, content in enumerate(test_reports):
        date = (datetime.now() - timedelta(days=i+1)).strftime("%Y-%m-%d")
        dir_path = Path(f"./results/{test_ticker}/{date}-12-00")
        dir_path.mkdir(parents=True, exist_ok=True)
        
        with open(dir_path / "最终交易决策.md", "w", encoding="utf-8") as f:
            f.write(content)
    
    print(f"创建测试数据完成：{test_ticker}")

async def test_history_analyst():
    """测试历史分析师"""
    print("开始测试历史分析师...")
    
    # 创建测试数据
    create_test_data()
    
    # 获取配置
    config = get_config().to_dict()
    print(f"使用LLM配置: {config.get('llm_provider', 'unknown')}")
    
    # 创建历史分析师 - 使用配置文件中的设置
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(
        model="deepseek-chat",
        temperature=0.3,
        openai_api_key="sk-5a68f1b53cfb478bb478f158c7a7af5f",
        base_url="https://api.deepseek.com/v1"
    )
    
    history_analyst = await create_history_analyst(llm, config)
    
    # 测试状态
    test_state = {
        "company_of_interest": "002466.SZ",
        "trade_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    print("运行历史分析...")
    result = await history_analyst(test_state)
    
    print("\n" + "="*50)
    print("历史分析结果:")
    print("="*50)
    print(result.get("history_analysis_report", "无结果"))
    
    return result

if __name__ == "__main__":
    asyncio.run(test_history_analyst())