#!/usr/bin/env python3
"""
使用LLM实际测试重构后的history_analyst.py
"""
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from tradingagents.config import get_config
from tradingagents.agents.analysts.history_analyst import create_history_analyst

# 使用环境变量中的API密钥
API_KEY = os.getenv("OPENAI_API_KEY", "sk-your-key-here")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

async def test_with_llm():
    """使用真实LLM测试历史分析师"""
    print("🚀 开始LLM集成测试...")
    
    # 创建测试数据
    test_ticker = "300130.SZ"
    
    # 创建更丰富的测试报告
    test_reports = [
        {
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "content": """# 最终交易决策 - 2025年8月19日

## 股票代码：300130.SZ（新国都）

## 今日市场表现
今日股价强势上涨8.5%，成交量放大至日均量的3倍，资金净流入2.1亿元。

## 技术面分析
- MACD金叉确认，DIF上穿DEA线
- KDJ指标J值突破80，显示强势
- 股价站上5日、10日、20日均线之上
- RSI(14)达到72，进入强势区域

## 基本面亮点
- 中报业绩增长45%，超预期20%
- 支付业务恢复强劲，收入占比提升至68%
- 数字人民币业务开始贡献收入

## 行业动态
- 央行数字货币政策利好持续释放
- 支付行业监管趋稳，竞争格局优化

## 最终交易建议：**强烈买入**

## 置信度：85%

## 目标价位：25.6元（上涨空间15%）

## 风险控制
- 建议仓位不超过总资产的25%
- 止损位设在22.8元（-8%）
- 关注大盘系统性风险"""
        },
        {
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "content": """# 最终交易决策 - 2025年8月18日

## 股票代码：300130.SZ（新国都）

## 今日市场表现
震荡调整，微跌1.2%，成交量萎缩至日均量的0.7倍。

## 技术面分析
- 股价在20日均线获得支撑
- MACD绿柱收窄，有金叉迹象
- RSI(14)在45附近，处于中性区域

## 基本面分析
- 行业政策面稳定，监管预期明确
- 公司基本面无变化，业务正常推进

## 最终交易建议：**持有观望**

## 置信度：60%

## 操作建议
- 现有仓位继续持有
- 等待放量突破信号再考虑加仓
- 关注明日美联储议息会议影响"""
        },
        {
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "content": """# 最终交易决策 - 2025年8月17日

## 股票代码：300130.SZ（新国都）

## 今日市场表现
受大盘拖累下跌3.8%，但尾盘有资金承接。

## 技术面分析
- 回踩前期重要支撑位23.5元
- 成交量放大，有恐慌盘涌出
- KDJ指标进入超卖区域

## 基本面亮点
- 公司发布1-7月经营数据，同比增长38%
- 数字人民币业务订单超预期
- 管理层增持计划提振信心

## 最终交易建议：**逢低买入**

## 置信度：78%

## 操作建议
- 在23.5-24元区间分批建仓
- 仓位控制在20%以内
- 止损位设在22元"""
        }
    ]
    
    # 创建测试目录和文件
    for report_data in test_reports:
        date_str = report_data["date"]
        test_dir = Path(f"./results/{test_ticker}/{date_str}-12-00")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        with open(test_dir / "最终交易决策.md", "w", encoding="utf-8") as f:
            f.write(report_data["content"])
    
    print(f"✅ 已创建测试数据：{len(test_reports)}天的报告")
    
    # 配置LLM
    try:
        from langchain_openai import ChatOpenAI
        
        # 使用配置文件中的设置
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            max_tokens=150,  # 限制输出长度
            openai_api_key=API_KEY,
            base_url=BASE_URL
        )
        print("✅ LLM配置成功")
    except Exception as e:
        print(f"❌ LLM配置失败: {e}")
        return None
    
    # 获取配置
    config = get_config().to_dict()
    
    try:
        # 创建历史分析师
        history_analyst = await create_history_analyst(llm, config)
        
        # 测试状态
        test_state = {
            "company_of_interest": test_ticker,
            "trade_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        print("🔄 运行历史分析...")
        result = await history_analyst(test_state)
        
        # 解析结果
        history_data = json.loads(result.get("history_analysis_report", "{}"))
        
        print(f"\n{'='*70}")
        print("🎯 LLM历史分析结果:")
        print(f"{'='*70}")
        print(f"📊 共获取到 {len(history_data)} 天的有效数据")
        print()
        
        for date_str, summary in sorted(history_data.items(), reverse=True):
            print(f"📅 {date_str}")
            print(f"   {summary}")
            print(f"   长度: {len(summary)} 字符")
            print()
        
        # 验证返回格式
        print("🔍 格式验证:")
        print(f"   - 返回类型: {type(history_data)}")
        print(f"   - JSON序列化: ✅ 成功")
        print(f"   - 键值对数量: {len(history_data)}")
        
        if history_data:
            sample_key = list(history_data.keys())[0]
            sample_value = history_data[sample_key]
            print(f"   - 示例键: {sample_key} ({type(sample_key)})")
            print(f"   - 示例值: {sample_value[:50]}... ({type(sample_value)})")
            print(f"   - 值长度: {len(sample_value)} 字符")
        
        return history_data
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_with_mock_llm():
    """使用模拟LLM测试，验证逻辑流程"""
    print("\n🎭 使用模拟LLM测试逻辑流程...")
    
    class MockLLM:
        async def ainvoke(self, prompt):
            # 模拟LLM响应
            if "建议买入" in prompt:
                return type('obj', (object,), {'content': '买入信号强烈，置信度85%，技术突破确认'})()
            elif "建议持有" in prompt:
                return type('obj', (object,), {'content': '持有观望，等待明确信号，风险可控'})()
            else:
                return type('obj', (object,), {'content': '逢低布局，基本面支撑，短期调整不改长期趋势'})()
    
    # 创建测试数据
    test_ticker = "300130.SZ"
    test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    test_dir = Path(f"./results/{test_ticker}/{test_date}-12-00")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    with open(test_dir / "最终交易决策.md", "w", encoding="utf-8") as f:
        f.write("建议买入，置信度82%，技术突破确认，MACD金叉")
    
    config = {"results_dir": "./results"}
    
    # 测试
    try:
        from tradingagents.agents.analysts.history_analyst import create_history_analyst
        history_analyst = await create_history_analyst(MockLLM(), config)
        
        test_state = {
            "company_of_interest": test_ticker,
            "trade_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        result = await history_analyst(test_state)
        history_data = json.loads(result.get("history_analysis_report", "{}"))
        
        print("✅ 模拟LLM测试通过")
        print(f"结果: {history_data}")
        return history_data
        
    except Exception as e:
        print(f"❌ 模拟测试失败: {e}")
        return None

if __name__ == "__main__":
    async def main():
        # 测试模拟LLM
        mock_result = asyncio.run(test_with_mock_llm())
        
        # 测试真实LLM（如果有配置）
        if API_KEY != "sk-your-key-here":
            real_result = asyncio.run(test_with_llm())
            if real_result:
                print("\n🎉 真实LLM测试完成！")
            else:
                print("\n⚠️  真实LLM测试未完成，请检查API配置")
        else:
            print("\n⚠️  未配置API密钥，跳过真实LLM测试")
            print("💡 请设置环境变量 OPENAI_API_KEY 来启用真实LLM测试")
    
    asyncio.run(main())