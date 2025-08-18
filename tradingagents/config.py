"""
TradingAgents 配置管理模块
使用环境变量进行配置管理
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    """配置管理类"""
    
    def __init__(self):
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """从环境变量加载配置"""
        return {
            # 项目路径配置
            "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
            "results_dir": os.getenv("RESULTS_DIR", "./results"),
            "data_dir": os.getenv("DATA_DIR", "/Users/yluo/Documents/Code/ScAI/FR1-data"),
            "data_cache_dir": os.path.join(
                os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
                "dataflows/data_cache",
            ),
            
            # LLM 提供商设置
            "llm_provider": os.getenv("LLM_PROVIDER", "openai").lower(),
            "llm_api_url": os.getenv("LLM_API_URL", "https://api.openai.com/v1"),
            "llm_api_key": os.getenv("LLM_API_KEY", ""),
            "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
            
            # 模型设置
            "deep_think_llm": os.getenv("LLM_DEEP_MODEL", "deepseek-reasoner"),
            "quick_think_llm": os.getenv("LLM_QUICK_MODEL", "deepseek-chat"),
            "backend_url": os.getenv("LLM_API_URL", "https://api.deepseek.com/v1"),
            
            # 嵌入模型设置
            "embedding_model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            "embedding_backend_url": os.getenv("EMBEDDING_BACKEND_URL", "https://api.openai.com/v1"),
            "embedding_api_key": os.getenv("EMBEDDING_API_KEY", ""),
            
            # 外部服务 API 密钥
            "tavily_api_key": os.getenv("TAVILY_API_KEY", ""),
            "finnhub_api_key": os.getenv("FINNHUB_API_KEY", ""),
            "reddit_client_id": os.getenv("REDDIT_CLIENT_ID", ""),
            "reddit_client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
            "reddit_user_agent": os.getenv("REDDIT_USER_AGENT", ""),
            
            # 辩论和讨论设置
            "max_debate_rounds": int(os.getenv("MAX_DEBATE_ROUNDS", "1")),
            "max_risk_discuss_rounds": int(os.getenv("MAX_RISK_DISCUSS_ROUNDS", "1")),
            "max_recur_limit": int(os.getenv("MAX_RECUR_LIMIT", "100")),
            
            # 工具设置
            "online_tools": os.getenv("ONLINE_TOOLS", "false").lower() == "true",
            "use_stock_api": os.getenv("USE_STOCK_API", "true").lower() == "true",
            
            # 调试和性能设置
            "debug_mode": os.getenv("DEBUG_MODE", "false").lower() == "true",
            "agent_timeout": int(os.getenv("AGENT_TIMEOUT", "300")),
            "default_analysis_depth": int(os.getenv("DEFAULT_ANALYSIS_DEPTH", "3")),
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self._config[key] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """批量更新配置"""
        self._config.update(config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """返回完整配置字典"""
        return self._config.copy()
    
    def validate(self) -> bool:
        """验证配置完整性"""
        required_keys = [
            "llm_api_key",
            "embedding_api_key",
        ]
        
        missing_keys = []
        for key in required_keys:
            if not self.get(key):
                missing_keys.append(key)
        
        if missing_keys:
            print(f"警告: 缺少必要的配置项: {missing_keys}")
            return False
        
        return True
    
    def print_config(self) -> None:
        """打印当前配置（隐藏敏感信息）"""
        print("当前配置:")
        for key, value in self._config.items():
            if "key" in key.lower() or "secret" in key.lower():
                # 隐藏敏感信息
                if value:
                    masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
                    print(f"  {key}: {masked_value}")
                else:
                    print(f"  {key}: (未设置)")
            else:
                print(f"  {key}: {value}")

# 全局配置实例
_config_instance = None

def get_config() -> Config:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

def set_config(config_dict: Dict[str, Any]) -> None:
    """设置全局配置"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    _config_instance.update(config_dict)

def load_env_config() -> Dict[str, Any]:
    """加载环境变量配置并返回字典"""
    config = get_config()
    return config.to_dict()

# 向后兼容的默认配置
DEFAULT_CONFIG = load_env_config() 