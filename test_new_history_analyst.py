#!/usr/bin/env python3
"""
测试重构后的历史分析师功能
"""
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from tradingagents.config import get_config
from tradingagents.agents.analysts.history_analyst import create_history_analyst

def create_test_reports():
    """创建测试用的历史报告数据"""
    test_ticker = "300130.SZ"
    
    # 创建不同日期的测试报告
    test_reports = [
        {
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "content": """# 最终交易决策

## 分析摘要
今日测试股票放量上涨，突破关键阻力位

## 关键发现
- 成交量放大至5日均量2倍
- MACD金叉确认
- 资金净流入1.2亿
- 板块轮动至科技股

## 最终交易建议: **买入**

## 置信度: 82%

## 风险控制
- 建议仓位不超过30%
- 止损位设在-3%
"""
        },
        {
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "content": """# 最终交易决策

## 分析摘要
测试股票今日震荡调整，量能有所萎缩

## 关键发现
- 跌破10日均线支撑
- RSI指标显示超卖
- 北向资金小幅流出

## 最终交易建议: **持有**

## 置信度: 65%

## 风险控制
- 密切关注20日线支撑
- 如跌破考虑减仓
"""
        },
        {
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "content": """# 最终交易决策

## 分析摘要
测试股票受大盘拖累下跌，但基本面依然稳健

## 关键发现
- 股价回踩重要支撑位
- 估值处于历史低位
- 机构调研频次增加

## 最终交易建议: **买入**

## 置信度: 78%

## 风险控制
- 分批建仓策略
- 关注大盘系统性风险
"""
        },
        {
            "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
            "content": """# 最终交易决策

## 分析摘要
测试股票今日表现平淡，等待方向选择

## 关键发现
- 成交量极度萎缩
- 技术指标中性
- 消息面平静

## 最终交易建议: **观望**

## 置信度: 55%

## 风险控制
- 等待明确信号再操作
"""
        },
        {
            "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "content": """# 最终交易决策

## 分析摘要
测试股票受业绩预增刺激涨停

## 关键发现
- 业绩预告超预期50%
- 涨停封单量大
- 技术形态突破

## 最终交易建议: **买入**

## 置信度: 90%

## 风险控制
- 关注次日高开低走风险
- 不宜盲目追涨
"""
        }
    ]
    
    # 创建测试目录和文件
    for report_data in test_reports:
        date_str = report_data["date"]
        test_dir = Path(f"./results/{test_ticker}/{date_str}-12-00")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        with open(test_dir / "最终交易决策.md", "w", encoding="utf-8") as f:
            f.write(report_data["content"])
    
    print(f"已创建测试数据：{len(test_reports)}天的报告")
    return test_ticker

async def test_new_history_analyst():
    """测试新的历史分析师"""
    print("开始测试重构后的历史分析师...")
    
    # 创建测试数据
    test_ticker = create_test_reports()
    
    # 获取配置
    config = get_config().to_dict()
    
    # 使用test_history_analyst.py中的LLM配置
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.3,
            openai_api_key="sk-5a68f1b53cfb478bb478f158c7a7af5f",
            base_url="https://api.deepseek.com/v1"
        )
        print("已配置LLM连接")
    except Exception as e:
        print(f"LLM配置失败: {e}")
        return None
    
    # 创建历史分析师
    history_analyst = await create_history_analyst(llm, config)
    
    # 测试状态
    test_state = {
        "company_of_interest": test_ticker,
        "trade_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    print("运行历史分析...")
    result = await history_analyst(test_state)
    
    # 解析结果
    try:
        history_data = json.loads(result.get("history_analysis_report", "{}"))
        print(f"\n{'='*60}")
        print("历史分析结果:")
        print(f"{'='*60}")
        print(f"共获取到 {len(history_data)} 天的数据")
        print()
        
        for date_str, summary in sorted(history_data.items(), reverse=True):
            print(f"📅 {date_str}: {summary}")
            print()
            
        # 验证返回格式
        print("验证返回格式:")
        print(f"- 类型: {type(history_data)}")
        print(f"- 键类型: {[type(k) for k in history_data.keys()][:3]}...")
        print(f"- 值类型: {[type(v) for v in history_data.values()][:3]}...")
        print(f"- 示例键: {list(history_data.keys())[:3] if history_data else '无'}")
        
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print("原始结果:", result)
    
    return history_data

if __name__ == "__main__":
    result = asyncio.run(test_new_history_analyst())
    if result:
        print("\n✅ 测试完成！功能正常工作")
    else:
        print("\n❌ 测试失败")