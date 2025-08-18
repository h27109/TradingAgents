from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import List
from langchain_core.tools import tool
import logging
from .mcp_config import jin10_mcp_config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class McpServer:
    def __init__(self):
        self.jin10_mcp_config = jin10_mcp_config

    async def init_all_client(self):
        """初始化Jin10 MCP客户端"""
        logger.info("开始初始化Jin10 MCP客户端...")
        
        try:
            # 初始化客户端
            self.jin10_client = MultiServerMCPClient(self.jin10_mcp_config)
            
            logger.info("Jin10 MCP客户端初始化完成")
        except Exception as e:
            logger.error(f"Jin10 MCP客户端初始化失败: {type(e).__name__}: {e}")
            raise RuntimeError(f"Jin10 MCP客户端初始化失败: {type(e).__name__}: {e}") from e