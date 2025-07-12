import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from pprint import pprint as pp

config = {
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

class TushareMCP:
    def __init__(self, mcp_server: dict):
        self._client = MultiServerMCPClient(mcp_server)

    async def get_tools(self):
        return await self._client.get_tools()

async def get_tools():
    tushare_mcp = TushareMCP(config["mcp_server"])
    return await tushare_mcp.get_tools()

if __name__ == "__main__":
    tools = asyncio.run(get_tools())
    pp(tools)