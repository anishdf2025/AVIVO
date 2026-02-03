from pathlib import Path
from typing import List, Optional, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from ..core.config import Config
from ..core.logger import logger


class VectorStore:
    """Pure LangChain FAISS vector store - semantic search only"""
    
    def __init__(self):
        self.db_path = Config.VECTOR_DB_PATH / "faiss_index"
        self.chunk_size = Config.RAG_CHUNK_SIZE
        self.chunk_overlap = Config.RAG_CHUNK_OVERLAP
        
        # LangChain embeddings
        self.embeddings = OllamaEmbeddings(
            model=Config.EMBEDDING_MODEL,
            base_url=Config.EMBEDDING_URL.replace('/api/embeddings', '')
        )
        
        # LangChain text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
        
        # LangChain FAISS vector store
        self.vectorstore: Optional[FAISS] = None
        
        logger.info(f"🗄️ VectorStore initialized:")
        logger.info(f"  - DB Path: {self.db_path}")
        logger.info(f"  - Chunk Size: {self.chunk_size}")
        logger.info(f"  - Chunk Overlap: {self.chunk_overlap}")
        
        # Load existing index
        self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index using LangChain"""
        index_path = self.db_path / "index.faiss"
        
        if index_path.exists():
            try:
                self.vectorstore = FAISS.load_local(
                    str(self.db_path),
                    self.embeddings
                )
                doc_count = len(self.vectorstore.docstore._dict)
                logger.info(f"Loaded FAISS vector store with {doc_count} documents")
            except Exception as e:
                logger.error(f"Error loading FAISS index: {str(e)}")
                self.vectorstore = None
        else:
            logger.info("No existing FAISS vector store found, starting fresh")
    
    def _save_index(self):
        """Save FAISS index using LangChain"""
        try:
            self.db_path.mkdir(parents=True, exist_ok=True)
            self.vectorstore.save_local(str(self.db_path))
            doc_count = len(self.vectorstore.docstore._dict)
            logger.info(f"Saved FAISS vector store with {doc_count} documents")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents using LangChain - automatic chunking and indexing"""
        try:
            logger.info(f"📥 Adding {len(documents)} documents to vector store")
            
            # LangChain split_documents
            logger.info("🔪 Chunking documents using LangChain...")
            chunks = self.text_splitter.split_documents(documents)
            
            logger.info(f"✅ Split {len(documents)} documents into {len(chunks)} chunks")
            
            if len(chunks) == 0:
                logger.warning("No chunks generated")
                return False
            
            # LangChain FAISS
            if self.vectorstore is None:
                logger.info("🆕 Creating new FAISS vector store...")
                self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
                logger.info("✅ FAISS vector store created successfully")
            else:
                logger.info("📌 Adding to existing FAISS vector store...")
                self.vectorstore.add_documents(chunks)
                logger.info("✅ Documents added to existing vector store")
            
            doc_count = len(self.vectorstore.docstore._dict)
            logger.info(f"📊 Vector store now contains {doc_count} total documents")
            
            # Save
            logger.info("💾 Saving vector store to disk...")
            self._save_index()
            logger.info("✅ Vector store saved successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}", exc_info=True)
            return False
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 5,
        score_threshold: float = 0.0  # Default to 0.0 for no filtering
    ) -> List[Dict[str, Any]]:
        """
        Pure semantic search using LangChain FAISS
        
        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum similarity score (0-1, default 0.0 for no filtering)
            
        Returns:
            List of results with content, metadata, and similarity scores
        """
        try:
            if self.vectorstore is None or len(self.vectorstore.docstore._dict) == 0:
                logger.warning("No documents in vector store")
                return []
            
            logger.info(f"🔮 Searching for: '{query[:50]}...'")
            
            # Use similarity_search_with_score for better control
            docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # Convert L2 distances to similarity scores
            import math
            results = []
            for doc, distance in docs_with_scores:
                # Convert distance to similarity (inverse relationship)
                similarity_score = math.exp(-distance)
                
                # Apply threshold if specified (but default is 0.0, so all pass)
                if similarity_score >= score_threshold:
                    results.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'similarity_score': float(similarity_score),
                        'distance': float(distance)
                    })
            
            # Sort by similarity score (highest first)
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            logger.info(f"Found {len(results)} documents (score_threshold={score_threshold})")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}", exc_info=True)
            return []
    
    def clear(self) -> bool:
        """Clear the vector store"""
        try:
            self.vectorstore = None
            
            import shutil
            if self.db_path.exists():
                shutil.rmtree(self.db_path)
            
            logger.info("Vector store cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        if self.vectorstore is None:
            return {
                'total_documents': 0,
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap,
            }
        
        return {
            'total_documents': len(self.vectorstore.docstore._dict),
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
        }
