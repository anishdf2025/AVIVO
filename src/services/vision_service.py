import requests
import base64
from PIL import Image
import io
from typing import Optional
from ..core.config import Config
from ..core.logger import logger


class VisionService:
    """Service for handling vision model interactions"""
    
    def __init__(self):
        self.ollama_url = Config.OLLAMA_URL
        self.model = Config.OLLAMA_MODEL
        self.image_quality = Config.IMAGE_QUALITY
    
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
        Get description of image from vision model
        
        Args:
            image_path: Path to the image file
            prompt: Custom prompt for the model
            
        Returns:
            Description of the image
        """
        try:
            img_b64 = self.encode_image(image_path)
            
            payload = {
                "model": self.model,
                "prompt": prompt or "Describe this image very precisely and in detail",
                "images": [img_b64],
                "stream": False
            }
            
            logger.info(f"Sending request to Ollama API for {image_path}")
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            description = result.get("response", "")
            
            logger.info(f"Successfully got description for {image_path}")
            return description
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise Exception(f"Failed to connect to Ollama API: {str(e)}")
        except Exception as e:
            logger.error(f"Error describing image: {str(e)}")
            raise
