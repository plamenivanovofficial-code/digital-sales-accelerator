#!/usr/bin/env python3
"""
Gemini Provider - Wrapper за Google Gemini API
"""

import logging
import google.generativeai as genai
from typing import Dict, Optional
from pathlib import Path
import PIL.Image


class GeminiProvider:
    """Gemini API provider"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """
        Initialize Gemini provider
        
        Args:
            api_key: Gemini API key
            model_name: Model to use
        """
        
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.model_name = model_name
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize model
        try:
            self.model = genai.GenerativeModel(model_name)
            self.logger.info(f"Gemini model initialized: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.model is not None
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze image with Gemini vision
        
        Returns:
            Dict with category, description, price, tags
        """
        
        if not self.model:
            raise Exception("Gemini model not initialized")
        
        # Load image
        try:
            img = PIL.Image.open(image_path)
        except Exception as e:
            raise Exception(f"Failed to load image: {e}")
        
        # Create prompt
        prompt = """Analyze this image and provide a detailed assessment:

1. Category: What type of item is this? (jewelry, antiques, art, collectibles, furniture, etc.)
2. Description: Detailed description of the item
3. Estimated Price: Estimated market value in USD (number only, 0-100000)
4. Tags: Comma-separated relevant tags/keywords

Respond ONLY with valid JSON in this exact format:
{
    "category": "category_name",
    "description": "detailed description",
    "price": 1000,
    "tags": "tag1, tag2, tag3"
}"""
        
        # Call Gemini
        try:
            response = self.model.generate_content([prompt, img])
            
            # Extract JSON from response
            result = self._parse_response(response.text)
            
            return result
        
        except Exception as e:
            # Re-raise with more context
            error_msg = str(e)
            if '429' in error_msg or 'quota' in error_msg.lower():
                raise Exception(f"Gemini rate limit: {error_msg}")
            elif 'safety' in error_msg.lower() or 'blocked' in error_msg.lower():
                raise Exception(f"Gemini safety block: {error_msg}")
            else:
                raise Exception(f"Gemini error: {error_msg}")
    
    def chat(self, prompt: str) -> str:
        """
        Chat with Gemini (text only)
        
        Args:
            prompt: Text prompt
            
        Returns:
            Response text
        """
        
        if not self.model:
            raise Exception("Gemini model not initialized")
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            raise Exception(f"Gemini chat error: {e}")
    
    def _parse_response(self, text: str) -> Dict:
        """Parse JSON response from Gemini"""
        
        import json
        import re
        
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith('```'):
            # Extract content between ``` markers
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if match:
                text = match.group(1)
        
        # Try to parse JSON
        try:
            result = json.loads(text)
            
            # Validate required fields
            if 'category' not in result:
                result['category'] = 'unknown'
            if 'description' not in result:
                result['description'] = 'No description'
            if 'price' not in result:
                result['price'] = 0
            if 'tags' not in result:
                result['tags'] = ''
            
            return result
        
        except json.JSONDecodeError:
            # Fallback: create minimal response
            return {
                'category': 'unknown',
                'description': text[:200],
                'price': 0,
                'tags': ''
            }
