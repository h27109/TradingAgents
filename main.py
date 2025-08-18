import asyncio
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.config import get_config
from dotenv import load_dotenv

load_dotenv(override=True)

async def main():
    # Create a custom config
    config = get_config().to_dict()
    config["llm_provider"] = "google"  # Use a different model
    config["backend_url"] = "https://generativelanguage.googleapis.com/v1"  # Use a different backend
    config["deep_think_llm"] = "gemini-2.0-flash"  # Use a different model
    config["quick_think_llm"] = "gemini-2.0-flash"  # Use a different model
    config["max_debate_rounds"] = 1  # Increase debate rounds
    config["online_tools"] = True  # Increase debate rounds

    # Initialize with custom config
    ta = TradingAgentsGraph(debug=True, config=config)
    
    # 异步初始化
    await ta.async_init()

    # forward propagate with streaming output
    _, decision = await ta.propagate("NVDA", "2024-05-10", stream_output=True)
    print(f"\n最终决策: {decision}")

    # Memorize mistakes and reflect
    # await ta.reflect_and_remember(1000) # parameter is the position returns

if __name__ == "__main__":
    asyncio.run(main())
