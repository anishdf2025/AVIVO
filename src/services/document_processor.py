import re
from typing import List, Dict
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..core.config import Config
from ..core.logger import logger


class DocumentProcessor:
    """Process documents for RAG using LangChain text splitters"""
    
    def __init__(self):
        self.chunk_size = Config.RAG_CHUNK_SIZE
        self.chunk_overlap = Config.RAG_CHUNK_OVERLAP
        
        # Initialize LangChain text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks using LangChain
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        try:
            # Clean text
            text = self.clean_text(text)
            
            # Use LangChain's text splitter
            chunks = self.text_splitter.split_text(text)
            
            logger.info(f"Split text into {len(chunks)} chunks using LangChain")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            return []
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        return text.strip()
    
    def process_file(self, file_path: Path) -> List[str]:
        """
        Process a file and return chunks
        
        Args:
            file_path: Path to file
            
        Returns:
            List of text chunks
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            chunks = self.chunk_text(text)
            logger.info(f"Processed file: {file_path.name} into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return []
    
    def extract_metadata(self, file_path: Path) -> Dict:
        """Extract metadata from file"""
        return {
            'filename': file_path.name,
            'file_size': file_path.stat().st_size,
            'file_type': file_path.suffix,
            'file_path': str(file_path)
        }
