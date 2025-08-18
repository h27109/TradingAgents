# TradingAgents Web版本 - 配置说明

## LLM配置
Web版本会自动从项目的config.py配置系统读取LLM设置，包括：
- LLM提供商 (llm_provider)
- API URL (backend_url)
- 快速思考模型 (quick_think_llm)
- 深度思考模型 (deep_think_llm)
- 嵌入模型 (embedding_model)
- 嵌入API URL (embedding_backend_url)

## 启动方法
uvicorn web.main:app --host 0.0.0.0 --port 8000 --reload

## 访问地址
http://localhost:8000
