from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import List
from langchain_core.tools import tool
import logging
from .mcp_config import market_mcp_config, social_mcp_config, news_mcp_config, financial_mcp_config, amap_config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class McpServer:
    def __init__(self):
        self.market_mcp_config = market_mcp_config
        self.social_mcp_config = social_mcp_config
        self.news_mcp_config = news_mcp_config
        self.financial_mcp_config = financial_mcp_config

    async def init_all_client(self):
        """初始化所有MCP客户端"""
        logger.info("开始初始化MCP客户端...")
        
        try:
            # 初始化客户端
            self.market_client = MultiServerMCPClient(self.market_mcp_config)
            self.social_client = MultiServerMCPClient(self.social_mcp_config)
            self.news_client = MultiServerMCPClient(self.news_mcp_config)
            self.financial_client = MultiServerMCPClient(self.financial_mcp_config)
            
            logger.info("MCP客户端初始化完成")
        except Exception as e:
            logger.error(f"MCP客户端初始化失败: {type(e).__name__}: {e}")
            raise RuntimeError(f"Tushare MCP客户端初始化失败: {type(e).__name__}: {e}") from e