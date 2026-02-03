import requests
import base64
from PIL import Image
import io
from typing import Optional
from pathlib import Path
from ..core.config import Config
from ..core.logger import logger
from .cache_service import CacheService


class VisionService:
    """Service for handling vision model interactions"""
    
    def __init__(self):
        self.ollama_url = Config.OLLAMA_URL
        self.model = Config.OLLAMA_MODEL
        self.image_quality = Config.IMAGE_QUALITY
        self.timeout = Config.OLLAMA_TIMEOUT
        self.cache = CacheService()
    
    def encode_image(self, image_path: str) -> str:
        """
        Encode image to base64 string
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string of the image
        """
        try:
            img = Image.open(image_path).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=self.image_quality)
            encoded = base64.b64encode(buf.getvalue()).decode()
            logger.info(f"Image encoded successfully: {image_path}")
            return encoded
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {str(e)}")
            raise
    
    def describe_image(self, image_path: str, prompt: Optional[str] = None) -> str:
        """
        Get description of image from vision model (with caching)
        
        Args:
            image_path: Path to the image file
            prompt: Custom prompt for the model
            
        Returns:
            Description of the image
        """
        try:
            # Read image data for hashing
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Generate hash for caching
            image_hash = self.cache.generate_image_hash(image_data)
            
            # Check cache first
            cached_description = self.cache.get_cached_description(image_hash)
            if cached_description:
                logger.info(f"Returning cached description for {image_path}")
                return cached_description
            
            # If not cached, process with AI model
            img_b64 = self.encode_image(image_path)
            
            payload = {
                "model": self.model,
                "prompt": prompt or "Describe this image concisely and precisely in under 500 words",
                "images": [img_b64],
                "stream": False
            }
            
            logger.info(f"Sending request to Ollama API for {image_path} (timeout: {self.timeout}s)")
            response = requests.post(
                self.ollama_url, 
                json=payload, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            description = result.get("response", "")
            
            # Cache the result
            self.cache.set_cached_description(image_hash, description)
            
            logger.info(f"Successfully got description for {image_path}")
            return description
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out after {self.timeout} seconds")
            raise Exception(f"Request timed out. The model is taking too long to respond.")
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise Exception(f"Failed to connect to Ollama API: {str(e)}")
        except Exception as e:
            logger.error(f"Error describing image: {str(e)}")
            raise
