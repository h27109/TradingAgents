# 所有的数据源配置。
# 按照使用目的来分类
mcp_servers_config = {
    # 新闻mcp配置
    "news": {
        "weibo": {
            "transport": "streamable_http",
            "url": "http://39.108.114.122:4200/mcp/",
            "timeout": 60.0,  # 请求超时时间60秒
        },
        "macro_china": {
            "transport": "streamable_http",
            "url": "http://39.108.114.122:8000/macro_china/mcp/",
            "headers": {
                "Authorization": "Bearer abcdyyyhbabcd",
                "Content-Type": "application/json",
            },
            "timeout": 60.0,  # 请求超时时间60秒
        },
        "macro_international": {
            "transport": "streamable_http",
            "url": "http://39.108.114.122:8000/macro_international/mcp/",
            "headers": {
                "Authorization": "Bearer abcdyyyhbabcd",
                "Content-Type": "application/json",
            },
            "timeout": 60.0,  # 请求超时时间60秒
        },
        # 新闻mcp配置
        "jin10_news": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8100/mcp/",
            "timeout": 60.0,  # 请求超时时间60秒
        }
    },
    # 市场和交易数据
    "market": {
        "stock": {
            "transport": "streamable_http",
            "url": "http://39.108.114.122:8000/stock/mcp/",
            "headers": {
                "Authorization": "Bearer abcdyyyhbabcd",
                "Content-Type": "application/json",
            },
            "timeout": 60.0,  # 请求超时时间60秒
        },
        "stock_index": {
            "transport": "streamable_http",
            "url": "http://39.108.114.122:8000/stock_index/mcp/",
            "headers": {
                "Authorization": "Bearer abcdyyyhbabcd",
                "Content-Type": "application/json",
            },
            "timeout": 60.0,  # 请求超时时间60秒
        },
    },
    # 财务数据
    "financial": {
        "finance": {
            "transport": "streamable_http",
            "url": "http://39.108.114.122:8000/finance/mcp/",
            "headers": {
                "Authorization": "Bearer abcdyyyhbabcd",
                "Content-Type": "application/json",
            },
            "timeout": 60.0,  # 请求超时时间60秒
        },
        "fund": {
            "transport": "streamable_http",
            "url": "http://39.108.114.122:8000/fund/mcp/",
            "headers": {
                "Authorization": "Bearer abcdyyyhbabcd",
                "Content-Type": "application/json",
            },
            "timeout": 60.0,  # 请求超时时间60秒
        },
    },
    # 宏观数据源
    "macro_data": {
        "macro_china": {
            "transport": "streamable_http",
            "url": "http://39.108.114.122:8000/macro_china/mcp/",
            "headers": {
                "Authorization": "Bearer abcdyyyhbabcd",
                "Content-Type": "application/json",
            },
            "timeout": 60.0,  # 请求超时时间60秒
        },
        "macro_international": {
            "transport": "streamable_http",
            "url": "http://39.108.114.122:8000/macro_international/mcp/",
            "headers": {
                "Authorization": "Bearer abcdyyyhbabcd",
                "Content-Type": "application/json",
            },
            "timeout": 60.0,  # 请求超时时间60秒
        },
        "stock_index": {
            "transport": "streamable_http",
            "url": "http://39.108.114.122:8000/stock_index/mcp/",
            "headers": {
                "Authorization": "Bearer abcdyyyhbabcd",
                "Content-Type": "application/json",
            },
            "timeout": 60.0,  # 请求超时时间60秒
        },
        # 新闻mcp配置
        "jin10_news": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8100/mcp/",
            "timeout": 60.0,  # 请求超时时间60秒
        }
    }
}
