from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain.docstore.document import Document
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from .vector_store import VectorStore
from .document_loader import DocumentLoaderService
from .cache_service import CacheService
from ..core.config import Config
from ..core.logger import logger


class RAGService:
    """Pure LangChain RAG service"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.doc_loader = DocumentLoaderService()
        self.cache_service = CacheService()
        
        # LangChain Ollama LLM
        self.llm = Ollama(
            model=Config.RAG_LLM_MODEL,
            base_url=Config.RAG_LLM_URL.replace('/api/generate', ''),
            temperature=0.1
        )
        
        self.top_k = Config.RAG_TOP_K
        self.similarity_threshold = Config.RAG_SIMILARITY_THRESHOLD
        
        # LangChain prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""Use the following context to answer the question. If you cannot answer based on the context, say "I don't have enough information."

Context:
{context}

Question: {question}

Answer:"""
        )
        
        logger.info(f"Redis cache connected: {Config.REDIS_HOST}:{Config.REDIS_PORT}")
        logger.info(f"RAG service initialized with LLM: {Config.RAG_LLM_MODEL}")
    
    def add_document(self, text: str, metadata: Optional[Dict] = None) -> bool:
        """Add text document using LangChain Document - no manual chunking"""
        try:
            logger.info("Adding text document to RAG")
            
            # Create LangChain Document - chunking handled by VectorStore
            doc = Document(
                page_content=text,
                metadata=metadata or {'source': 'text_input'}
            )
            
            # Add to vector store (chunking happens inside)
            success = self.vector_store.add_documents([doc])
            
            if success:
                logger.info("Text document added successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding text document: {str(e)}")
            return False
    
    def add_document_from_file(self, file_path: Path, metadata: Optional[Dict] = None) -> bool:
        """Add document from file using LangChain loaders - no manual chunking"""
        try:
            logger.info(f"Loading document from file: {file_path}")
            
            # Use LangChain document loaders
            documents = self.doc_loader.load_document(file_path)
            
            if not documents:
                logger.error("No documents loaded from file")
                return False
            
            # Update metadata
            for doc in documents:
                if metadata:
                    doc.metadata.update(metadata)
            
            logger.info(f"Loaded {len(documents)} document(s) from {file_path.name}")
            
            # Add to vector store (chunking happens inside)
            success = self.vector_store.add_documents(documents)
            
            if success:
                logger.info(f"Added documents from {file_path.name} to knowledge base")
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding document from file: {str(e)}", exc_info=True)
            return False
    
    def query(
        self, 
        question: str, 
        top_k: Optional[int] = None,
        include_sources: bool = False
    ) -> Dict[str, Any]:
        """Query using pure LangChain FAISS semantic search - always returns top-k"""
        try:
            logger.info(f"Querying RAG: {question[:50]}...")
            
            k = top_k or self.top_k
            
            # Check cache
            cache_key = f"rag:{question[:50]}"
            cached_result = self.cache_service.get_cached_rag_response(cache_key)
            
            if cached_result:
                logger.info(f"✅ Cache HIT for RAG query: {cache_key[:30]}...")
                return cached_result
            
            logger.info(f"❌ Cache MISS for RAG query: {cache_key[:30]}...")
            
            # Pure FAISS semantic search (NO use_hybrid parameter)
            search_results = self.vector_store.similarity_search(
                query=question,
                k=k,
                score_threshold=0.0  # Always return top-k results
            )
            
            logger.info(f"Found {len(search_results)} documents")
            
            # Generate answer
            if not search_results:
                answer = "I don't have enough information to answer this question. Please upload relevant documents first."
                result = {'answer': answer}
            else:
                logger.info(f"Generating RAG response...")
                
                # Build context with distances for debugging
                context = "\n\n".join([
                    f"[Document {i+1} - Distance: {doc.get('distance', 0):.3f}]\n{doc['content']}" 
                    for i, doc in enumerate(search_results)
                ])
                
                # LangChain prompt formatting
                prompt = self.prompt_template.format(
                    context=context,
                    question=question
                )
                
                # LangChain LLM invoke
                answer = self.llm.invoke(prompt)
                
                result = {
                    'answer': answer,
                    'num_sources': len(search_results)
                }
                
                if include_sources:
                    result['sources'] = [
                        {
                            'content': doc['content'][:200] + '...',
                            'metadata': doc['metadata'],
                            'similarity_score': doc.get('similarity_score', 0),
                            'distance': doc.get('distance', 0)
                        }
                        for doc in search_results
                    ]
                
                # Cache the result
                self.cache_service.set_cached_rag_response(cache_key, result)
                logger.info(f"💾 Cached RAG response for query: {cache_key[:30]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"RAG query error: {str(e)}", exc_info=True)
            return {
                'answer': f"An error occurred while processing your question: {str(e)}",
                'error': True
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG statistics"""
        return {
            'llm_model': Config.RAG_LLM_MODEL,
            'embedding_model': Config.EMBEDDING_MODEL,
            'vector_store': self.vector_store.get_stats(),
            'top_k': self.top_k,
            'similarity_threshold': self.similarity_threshold,
        }
