import chromadb
from chromadb.config import Settings
from openai import AsyncOpenAI
import asyncio
import logging

logger = logging.getLogger(__name__)

class FinancialSituationMemory:
    def __init__(self, name, config):
        self.embedding = config.get("embedding_model")
        self.client = AsyncOpenAI(base_url=config.get("embedding_backend_url"), api_key=config.get("embedding_api_key"))
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        self.situation_collection = self.chroma_client.create_collection(name=name)

    async def get_embedding(self, text):
        """Get OpenAI embedding for a text"""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding, input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"获取嵌入向量失败: {e}")
            return []

    async def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""
        try:
            situations = []
            advice = []
            ids = []
            embeddings = []

            offset = self.situation_collection.count()

            # 并发获取所有嵌入向量
            embedding_tasks = []
            for i, (situation, recommendation) in enumerate(situations_and_advice):
                situations.append(situation)
                advice.append(recommendation)
                ids.append(str(offset + i))
                embedding_tasks.append(self.get_embedding(situation))

            # 等待所有嵌入向量计算完成
            embeddings = await asyncio.gather(*embedding_tasks)

            # 过滤掉空的嵌入向量
            valid_data = []
            for i, embedding in enumerate(embeddings):
                if embedding:
                    valid_data.append({
                        'document': situations[i],
                        'metadata': {"recommendation": advice[i]},
                        'embedding': embedding,
                        'id': ids[i]
                    })

            if valid_data:
                # 批量添加到 ChromaDB
                self.situation_collection.add(
                    documents=[item['document'] for item in valid_data],
                    metadatas=[item['metadata'] for item in valid_data],
                    embeddings=[item['embedding'] for item in valid_data],
                    ids=[item['id'] for item in valid_data],
                )
                logger.info(f"成功添加 {len(valid_data)} 个情境到内存")
            else:
                logger.warning("没有有效的嵌入向量，跳过添加")

        except Exception as e:
            logger.error(f"添加情境失败: {e}")

    async def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using OpenAI embeddings"""
        try:
            query_embedding = await self.get_embedding(current_situation)
            
            if not query_embedding:
                logger.warning("无法获取查询嵌入向量")
                return []

            results = self.situation_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_matches,
                include=["metadatas", "documents", "distances"],
            )

            matched_results = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    matched_results.append({
                        "matched_situation": results["documents"][0][i],
                        "recommendation": results["metadatas"][0][i]["recommendation"],
                        "similarity_score": 1 - results["distances"][0][i],
                    })

            return matched_results

        except Exception as e:
            logger.error(f"检索记忆失败: {e}")
            return []

    def get_memory_stats(self):
        """获取内存统计信息"""
        try:
            count = self.situation_collection.count()
            return {
                "total_situations": count,
                "collection_name": self.situation_collection.name
            }
        except Exception as e:
            logger.error(f"获取内存统计失败: {e}")
            return {"total_situations": 0, "collection_name": "unknown"}


if __name__ == "__main__":
    # Example usage
    matcher = FinancialSituationMemory()

    # Example data
    example_data = [
        (
            "High inflation rate with rising interest rates and declining consumer spending",
            "Consider defensive sectors like consumer staples and utilities. Review fixed-income portfolio duration.",
        ),
        (
            "Tech sector showing high volatility with increasing institutional selling pressure",
            "Reduce exposure to high-growth tech stocks. Look for value opportunities in established tech companies with strong cash flows.",
        ),
        (
            "Strong dollar affecting emerging markets with increasing forex volatility",
            "Hedge currency exposure in international positions. Consider reducing allocation to emerging market debt.",
        ),
        (
            "Market showing signs of sector rotation with rising yields",
            "Rebalance portfolio to maintain target allocations. Consider increasing exposure to sectors benefiting from higher rates.",
        ),
    ]

    # Add the example situations and recommendations
    asyncio.run(matcher.add_situations(example_data))

    # Example query
    current_situation = """
    Market showing increased volatility in tech sector, with institutional investors 
    reducing positions and rising interest rates affecting growth stock valuations
    """

    try:
        recommendations = asyncio.run(matcher.get_memories(current_situation, n_matches=2))

        for i, rec in enumerate(recommendations, 1):
            print(f"\nMatch {i}:")
            print(f"Similarity Score: {rec['similarity_score']:.2f}")
            print(f"Matched Situation: {rec['matched_situation']}")
            print(f"Recommendation: {rec['recommendation']}")

    except Exception as e:
        print(f"Error during recommendation: {str(e)}")
