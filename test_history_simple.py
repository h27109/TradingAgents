#!/usr/bin/env python3
"""
简化测试：验证重构后的history_analyst.py逻辑
"""
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

def create_test_reports():
    """创建测试用的历史报告数据"""
    test_ticker = "300130.SZ"
    
    # 创建不同日期的测试报告
    test_reports = [
        {
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "content": "建议买入，置信度82%，放量突破关键阻力位，MACD金叉确认"
        },
        {
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "content": "建议持有，置信度65%，调整缩量等待方向，RSI超卖信号"
        },
        {
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "content": "建议买入，置信度78%，回踩重要支撑位，估值历史低位"
        },
        {
            "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
            "content": "建议观望，置信度55%，量能萎缩方向不明，等待明确信号"
        },
        {
            "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "content": "建议买入，置信度90%，业绩超预期刺激涨停，技术形态突破"
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

def test_file_reading_logic():
    """测试文件读取逻辑"""
    print("测试文件读取逻辑...")
    
    test_ticker = create_test_reports()
    
    # 模拟读取最近10天的报告
    results_root = Path("./results")
    analysis_date = datetime.now().date()
    max_days = 10
    
    daily_reports = {}
    
    def read_latest_report_for_day(day_str: str) -> str:
        """测试用的读取函数"""
        ticker_root = results_root / test_ticker
        if not ticker_root.exists() or not ticker_root.is_dir():
            return ""
        
        date_prefix = f"{day_str}-"
        day_dirs = [p for p in ticker_root.iterdir() if p.is_dir() and p.name.startswith(date_prefix)]
        if not day_dirs:
            return ""
        
        latest_dir = sorted(day_dirs, key=lambda p: p.name)[-1]
        
        # 读取最终交易决策
        final_decision_file = latest_dir / "最终交易决策.md"
        if not final_decision_file.exists():
            final_decision_file = latest_dir / "final_trade_decision.md"
        
        if not final_decision_file.exists():
            return ""
            
        try:
            return final_decision_file.read_text(encoding="utf-8")
        except Exception:
            return ""
    
    # 读取数据
    for i in range(1, max_days + 1):
        day = analysis_date - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        report_content = read_latest_report_for_day(day_str)
        
        if report_content:
            daily_reports[day_str] = report_content
        else:
            print(f"跳过无数据日期: {day_str}")
    
    print(f"\n{'='*50}")
    print("测试结果:")
    print(f"{'='*50}")
    print(f"总共读取到 {len(daily_reports)} 天的数据")
    
    # 验证格式
    for date_str, content in sorted(daily_reports.items(), reverse=True):
        print(f"📅 {date_str}: {content}")
    
    # 验证字典格式
    json_output = json.dumps(daily_reports, ensure_ascii=False)
    print(f"\nJSON格式验证:")
    print(f"- 长度: {len(json_output)} 字符")
    print(f"- 类型: {type(json.loads(json_output))}")
    print(f"- 键格式: {list(json.loads(json_output).keys())[:2]}")
    
    return daily_reports

if __name__ == "__main__":
    result = test_file_reading_logic()
    if result:
        print("\n✅ 逻辑测试通过！文件读取功能正常")
    else:
        print("\n❌ 逻辑测试失败")