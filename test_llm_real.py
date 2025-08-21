#!/usr/bin/env python3
"""
使用真实LLM测试重构后的history_analyst.py的summary功能
"""
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

# 设置测试环境
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_API_KEY"] = "sk-5a68f1b53cfb478bb478f158c7a7af5f"  # 使用测试密钥
os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com/v1"
os.environ["LLM_DEEP_MODEL"] = "deepseek-chat"
os.environ["LLM_QUICK_MODEL"] = "deepseek-chat"

async def test_real_llm_summary():
    """使用真实LLM测试summary功能"""
    print("🎯 开始真实LLM summary测试...")
    
    # 创建测试数据
    test_ticker = "300130.SZ"
    
    # 创建简化的测试报告
    test_reports = [
        {
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "content": """最终交易决策：300130.SZ今日大涨8.5%，成交量放大3倍，MACD金叉确认，建议买入，置信度85%，目标价26.5元，止损位21.5元。"""
        },
        {
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "content": """最终交易决策：300130.SZ缩量调整，微跌0.8%，20日线支撑有效，建议持有观望，置信度60%，等待放量突破23元。"""
        },
        {
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "content": """最终交易决策：300130.SZ受大盘影响下跌3.8%，回踩21.8元支撑位，建议逢低买入，置信度78%，分批建仓。"""
        }
    ]
    
    # 创建测试目录和文件
    for report_data in test_reports:
        date_str = report_data["date"]
        test_dir = Path(f"./results/{test_ticker}/{date_str}-12-00")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        with open(test_dir / "最终交易决策.md", "w", encoding="utf-8") as f:
            f.write(report_data["content"])
    
    print(f"✅ 已创建 {len(test_reports)} 天测试数据")
    
    try:
        # 使用项目配置
        from tradingagents.config import get_config
        config = get_config().to_dict()
        
        # 使用deepseek配置
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.3,
            max_tokens=150,
            openai_api_key="sk-5a68f1b53cfb478bb478f158c7a7af5f",
            base_url="https://api.deepseek.com/v1"
        )
        
        # 创建历史分析师
        from tradingagents.agents.analysts.history_analyst import create_history_analyst
        history_analyst = await create_history_analyst(llm, config)
        
        # 测试
        test_state = {
            "company_of_interest": test_ticker,
            "trade_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        print("🔄 开始LLM总结...")
        result = await history_analyst(test_state)
        
        # 解析结果
        history_data = json.loads(result.get("history_analysis_report", "{}"))
        
        print(f"\n{'='*60}")
        print("🎯 LLM总结结果:")
        print(f"{'='*60}")
        
        for date_str, summary in sorted(history_data.items(), reverse=True):
            print(f"📅 {date_str}: {summary}")
            print(f"   长度: {len(summary)}字符")
        
        print(f"\n✅ 测试完成！共处理{len(history_data)}天数据")
        return history_data
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return None

if __name__ == "__main__":
    result = asyncio.run(test_real_llm_summary())