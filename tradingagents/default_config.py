import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "openai",
    # "deep_think_llm": "o4-mini",
    # "quick_think_llm": "gpt-4o-mini",
    # "backend_url": "https://api.openai.com/v1",
    "deep_think_llm": "deepseek-reasoner",
    "quick_think_llm": "deepseek-chat",
    "backend_url": "https://api.deepseek.com",
    "embedding_model": "Qwen/Qwen3-Embedding-8B",
    "embedding_backend_url": "https://api.siliconflow.cn/v1",
    "embedding_api_key": "sk-ssvmxoionahtxtbrvvufgvvusienqzltntdbechjstykxddq",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,
    "use_mcp_server": True,
    "mcp_server": {
        "stock_data": {
            "transport": "streamable_http",
            "url": "http://39.108.114.122:8000/stock/mcp",
            "headers": {
                "Authorization": "Bearer abcdyyyhbabcd",
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        },
        "financial_data": {
            "transport": "streamable_http",
            "url": "http://39.108.114.122:8000/finance/mcp",
            "headers": {
                "Authorization": "Bearer abcdyyyhbabcd",
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        },
        "fund_data": {
            "transport": "streamable_http",
            "url": "http://39.108.114.122:8000/fund/mcp",
            "headers": {
                "Authorization": "Bearer abcdyyyhbabcd",
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        },
    }
}
