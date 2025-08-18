# 新闻mcp配置
news_mcp_config = {
    "weibo": {
    "transport": "streamable_http",
    "url": "http://39.108.114.122:4200/mcp/",
    "timeout": 60.0,  # 请求超时时间60秒
    }
    ,
    "macro_china": {
    "transport": "streamable_http",
    "url": "http://39.108.114.122:8000/macro_china/mcp/",
    "headers": {
        "Authorization": "Bearer abcdyyyhbabcd",
        "Content-Type": "application/json"
        },
    "timeout": 60.0,  # 请求超时时间60秒
    }
    ,
    "macro_international": {
    "transport": "streamable_http",
    "url": "http://39.108.114.122:8000/macro_international/mcp/",
    "headers": {
        "Authorization": "Bearer abcdyyyhbabcd",
        "Content-Type": "application/json"
        },
    "timeout": 60.0,  # 请求超时时间60秒
    }
}

# 社媒mcp配置
social_mcp_config = {
    "weibo": {
    "transport": "streamable_http",
    "url": "http://39.108.114.122:4200/mcp/",
    "timeout": 60.0,  # 请求超时时间60秒
    }
}

# market mcp配置
market_mcp_config = {
    "stock": {
    "transport": "streamable_http",
    "url": "http://39.108.114.122:8000/stock/mcp/",
    "headers": {
        "Authorization": "Bearer abcdyyyhbabcd",
        "Content-Type": "application/json"
        },
    "timeout": 60.0,  # 请求超时时间60秒
    },
    "stock_index": {
    "transport": "streamable_http",
    "url": "http://39.108.114.122:8000/stock_index/mcp/",
    "headers": {
        "Authorization": "Bearer abcdyyyhbabcd",
        "Content-Type": "application/json"
        },
    "timeout": 60.0,  # 请求超时时间60秒
    }
}

# 财务mcp配置
financial_mcp_config = {
    "finance": {
    "transport": "streamable_http",
    "url": "http://39.108.114.122:8000/finance/mcp/",
    "headers": {
        "Authorization": "Bearer abcdyyyhbabcd",
        "Content-Type": "application/json"
        },
    "timeout": 60.0,  # 请求超时时间60秒
    }
    ,
    "fund": {
    "transport": "streamable_http",
    "url": "http://39.108.114.122:8000/fund/mcp/",
    "headers": {
        "Authorization": "Bearer abcdyyyhbabcd",
        "Content-Type": "application/json"
        },
    "timeout": 60.0,  # 请求超时时间60秒
    }
    
}

amap_config = {
    "amap": {
    "transport": "sse",
    "url": "https://mcp.amap.com/sse?key=55a5d19a0569d9329b26b43756a52b3c"
    }
}