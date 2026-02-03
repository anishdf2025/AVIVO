from langchain_community.embeddings import OllamaEmbeddings
from ..core.config import Config
from ..core.logger import logger


class EmbeddingService:
    """Wrapper for LangChain OllamaEmbeddings - no custom logic"""
    
    def __init__(self):
        self.model = Config.EMBEDDING_MODEL
        self.base_url = Config.EMBEDDING_URL.replace('/api/embeddings', '')
        
        # Create LangChain embeddings instance
        self.embeddings = OllamaEmbeddings(
            model=self.model,
            base_url=self.base_url
        )
        
        logger.info(f"🧠 Embedding service initialized with model: {self.model}")
        logger.info(f"  - URL: {self.base_url}")
    
    def get_embeddings_model(self):
        """Return LangChain embeddings instance"""
        return self.embeddings
