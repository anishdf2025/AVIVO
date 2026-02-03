from pathlib import Path
from typing import List, Optional
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader
)
from langchain.docstore.document import Document
from ..core.config import Config
from ..core.logger import logger


class DocumentLoaderService:
    """Service for loading individual documents using LangChain loaders"""
    
    def __init__(self):
        self.supported_extensions = {
            '.txt': TextLoader,
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.doc': Docx2txtLoader,
            '.xlsx': UnstructuredExcelLoader,
            '.xls': UnstructuredExcelLoader,
            '.pptx': UnstructuredPowerPointLoader,
            '.ppt': UnstructuredPowerPointLoader,
        }
        logger.info(f"DocumentLoaderService initialized with formats: {list(self.supported_extensions.keys())}")
    
    def load_document(self, file_path: Path) -> List[Document]:
        """Load a single document using appropriate LangChain loader"""
        try:
            file_path = Path(file_path)
            extension = file_path.suffix.lower()
            
            logger.info(f"Loading document from file: {file_path.name}")
            logger.info(f"🔍 Attempting to load file: {file_path} with extension: {extension}")
            
            if extension not in self.supported_extensions:
                logger.warning(f"Unsupported file type: {extension}")
                return []
            
            loader_class = self.supported_extensions[extension]
            logger.info(f"📖 Using loader: {loader_class.__name__}")
            
            logger.info(f"⏳ Loading documents from {file_path.name}...")
            loader = loader_class(str(file_path))
            documents = loader.load()
            
            logger.info(f"✅ Loaded {len(documents)} raw document(s)")
            
            for i, doc in enumerate(documents):
                logger.info(f"📄 Document {i}: {len(doc.page_content)} characters")
                doc.metadata.update({
                    'source': str(file_path),
                    'filename': file_path.name,
                    'file_type': extension,
                    'file_size': file_path.stat().st_size,
                    'page': i
                })
            
            logger.info(f"✅ Successfully loaded {len(documents)} documents from {file_path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}", exc_info=True)
            return []
    
    def load_from_text(self, text: str, metadata: Optional[dict] = None) -> Document:
        """
        Create a Document from raw text
        
        Args:
            text: Raw text content
            metadata: Optional metadata dict
            
        Returns:
            LangChain Document object
        """
        doc_metadata = metadata or {}
        doc_metadata['source'] = 'text_input'
        
        return Document(
            page_content=text,
            metadata=doc_metadata
        )
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return list(self.supported_extensions.keys())
