#!/usr/bin/env python3
"""
使用.env配置的LLM测试重构后的history_analyst.py的summary功能
"""
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_llm_summary():
    """使用真实LLM测试summary功能"""
    print("🔍 开始LLM summary功能测试...")
    
    # 创建丰富的测试数据
    test_ticker = "300130.SZ"
    
    # 创建不同风格的测试报告
    test_reports = [
        {
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "content": """# 最终交易决策 - 新国都(300130.SZ) 2025-08-19

## 市场表现
今日股价大涨9.2%，成交量放大至5日均量3.5倍，资金净流入3.2亿元，强势特征明显。

## 技术分析
- MACD金叉确认，红柱显著放大
- 股价突破所有短期均线压制
- RSI(14)升至78，进入强势区域但未超买
- 量价配合完美，突破22.8元关键阻力位

## 基本面驱动
- 中报净利润增长65%，大超预期30%
- 数字人民币业务订单同比增200%
- 与央行数字货币研究所达成战略合作

## 行业催化
- 数字人民币试点城市扩容至25个
- 支付行业监管政策趋于明朗
- 跨境支付业务迎来政策红利

## 最终交易建议：**强烈买入**

## 置信度：88%

## 目标价位：26.5元（上涨空间18%）

## 风险控制
- 建议仓位：不超过总资产的30%
- 止损位：21.5元（-7%）
- 分批建仓策略：22.8-23.5元区间"""
        },
        {
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "content": """# 最终交易决策 - 新国都(300130.SZ) 2025-08-18

## 市场表现
窄幅震荡，微跌0.8%，成交量萎缩至日均量0.6倍，观望情绪浓厚。

## 技术分析
- 20日均线22.1元形成支撑
- MACD绿柱持续收窄，有金叉迹象
- KDJ指标在50附近徘徊，方向不明
- 缩量整理，等待方向选择

## 基本面稳定
- 公司基本面无变化，业务推进正常
- 数字人民币业务预期良好
- 管理层稳定，无重大变化

## 最终交易建议：**谨慎持有**

## 置信度：62%

## 操作建议
- 现有仓位继续持有
- 等待放量突破23元再加仓
- 关注大盘走势影响"""
        },
        {
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "content": """# 最终交易决策 - 新国都(300130.SZ) 2025-08-17

## 市场表现
受大盘调整影响，股价下跌4.5%，但尾盘有资金承接迹象。

## 技术分析
- 回踩重要支撑位21.8元
- 成交量放大，恐慌盘释放
- RSI(14)降至42，接近超卖区域
- 长期上升趋势线支撑有效

## 基本面亮点
- 公司发布1-7月经营数据，收入同比增长52%
- 数字人民币硬件钱包出货量超预期
- 高管团队增持股份，彰显信心

## 行业背景
- 数字货币政策持续加码
- 支付行业竞争格局优化
- 公司技术优势明显

## 最终交易建议：**逢低买入**

## 置信度：75%

## 操作策略
- 22元以下分批建仓
- 仓位控制在25%以内
- 止损位设在20.5元"""
        },
        {
            "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
            "content": """# 最终交易决策 - 新国都(300130.SZ) 2025-08-16

## 市场表现
横盘整理，波动幅度仅1.2%，成交量极度萎缩。

## 技术分析
- 5日、10日、20日均线粘合
- 成交量创3个月新低
- 技术指标全部中性
- 变盘信号强烈

## 消息面
- 消息面平静，无重大公告
- 行业政策面稳定
- 市场等待明确催化剂

## 最终交易建议：**观望等待**

## 置信度：55%

## 策略建议
- 保持观望，等待方向明确
- 突破22.5元可考虑跟进
- 跌破21元注意风险"""
        },
        {
            "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "content": """# 最终交易决策 - 新国都(300130.SZ) 2025-08-15

## 市场表现
受业绩预增公告刺激，股价涨停，封单量达20万手。

## 业绩亮点
- 前三季度业绩预告：净利润预增80%-100%
- 数字人民币业务爆发式增长
- 支付业务毛利率提升5个百分点

## 技术分析
- 涨停突破前期整理平台
- 成交量温和放大
- 技术形态完美突破

## 资金动向
- 北向资金净买入1.8亿元
- 机构席位大举买入
- 市场关注度显著提升

## 最终交易建议：**积极买入**

## 置信度：92%

## 操作建议
- 次日高开不超过3%可追入
- 仓位控制在30%以内
- 目标价位25元"""
        }
    ]
    
    # 创建测试数据
    for report_data in test_reports:
        date_str = report_data["date"]
        test_dir = Path(f"./results/{test_ticker}/{date_str}-12-00")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        with open(test_dir / "最终交易决策.md", "w", encoding="utf-8") as f:
            f.write(report_data["content"])
    
    print(f"✅ 已创建 {len(test_reports)} 天的测试报告")
    
    # 使用项目配置
    try:
        from tradingagents.config import get_config
        config = get_config().to_dict()
        
        # 根据.env配置LLM
        provider = os.getenv("LLM_PROVIDER", "openai")
        model = os.getenv("DEEP_THINK_LLM", "gpt-3.5-turbo")
        
        print(f"🔧 使用LLM配置: {provider} - {model}")
        
        if provider == "openai":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=model,
                temperature=0.3,
                max_tokens=200,
                openai_api_key=os.getenv("LLM_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            )
        elif provider == "deepseek":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model="deepseek-chat",
                temperature=0.3,
                max_tokens=200,
                openai_api_key=os.getenv("LLM_API_KEY"),
                base_url="https://api.deepseek.com/v1"
            )
        elif provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(
                model=model,
                temperature=0.3,
                max_tokens=200,
                anthropic_api_key=os.getenv("LLM_API_KEY")
            )
        else:
            # 使用openai作为默认
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=model,
                temperature=0.3,
                max_tokens=200,
                openai_api_key=os.getenv("LLM_API_KEY", "test-key")
            )
        
    except Exception as e:
        print(f"❌ LLM配置失败: {e}")
        return None
    
    try:
        # 创建历史分析师
        from tradingagents.agents.analysts.history_analyst import create_history_analyst
        history_analyst = await create_history_analyst(llm, config)
        
        # 测试状态
        test_state = {
            "company_of_interest": test_ticker,
            "trade_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        print("🔄 开始LLM总结分析...")
        result = await history_analyst(test_state)
        
        # 解析结果
        history_data = json.loads(result.get("history_analysis_report", "{}"))
        
        print(f"\n{'='*80}")
        print("🎯 LLM总结结果:")
        print(f"{'='*80}")
        print(f"📊 成功处理了 {len(history_data)} 天的数据")
        print()
        
        for date_str, summary in sorted(history_data.items(), reverse=True):
            print(f"📅 {date_str}")
            print(f"   总结: {summary}")
            print(f"   长度: {len(summary)} 字符")
            print()
        
        # 验证格式
        print("🔍 格式验证:")
        print(f"   ✅ 返回类型: {type(history_data)}")
        print(f"   ✅ JSON格式: 正确")
        print(f"   ✅ 键值对: {len(history_data)} 个")
        
        if history_data:
            # 验证所有总结都在200字符以内
            long_summaries = [v for v in history_data.values() if len(v) > 200]
            if long_summaries:
                print(f"   ⚠️  有 {len(long_summaries)} 个总结超过200字符")
            else:
                print(f"   ✅ 所有总结均在200字符以内")
        
        return history_data
        
    except Exception as e:
        print(f"❌ LLM测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🧪 开始LLM集成测试...")
    print("💡 确保.env文件已正确配置LLM参数")
    
    result = asyncio.run(test_llm_summary())
    
    if result:
        print("\n🎉 LLM测试完成！重构的history_analyst.py功能正常")
        print("📋 返回格式验证：字典格式，键为日期，值为LLM生成的200字内总结")
    else:
        print("\n⚠️  LLM测试未完成，请检查.env配置")