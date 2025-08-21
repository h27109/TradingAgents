import logging
from langchain_mcp_adapters.client import MultiServerMCPClient

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class McpServers:
    def __init__(self, mcp_config: dict):
        self.market_mcp_config = mcp_config["market"]
        self.news_mcp_config = mcp_config["news"]
        self.financial_mcp_config = mcp_config["financial"]
        self.macro_data_mcp_config = mcp_config["macro_data"]
        self.clients = {}

    async def init_all_client(self):
        """初始化所有MCP客户端"""
        logger.info("开始初始化MCP客户端...")
        
        try:
            # 初始化客户端
            self.clients["market"] = MultiServerMCPClient(self.market_mcp_config)
            self.clients["news"] = MultiServerMCPClient(self.news_mcp_config)
            self.clients["financial"] = MultiServerMCPClient(self.financial_mcp_config)
            self.clients["macro_data"] = MultiServerMCPClient(self.macro_data_mcp_config)
            
            logger.info("MCP客户端初始化完成")
        except Exception as e:
            logger.error(f"MCP客户端初始化失败: {type(e).__name__}: {e}")
            raise RuntimeError(f"MCP客户端初始化失败: {type(e).__name__}: {e}") from e
    
    def get_client(self, category: str):
        """获取指定类别的MCP客户端"""
        if category not in self.clients:
            raise ValueError(f"MCP客户端不存在: {category}")
        return self.clients[category]
    