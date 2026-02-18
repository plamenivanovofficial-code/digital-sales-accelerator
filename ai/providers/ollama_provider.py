#!/usr/bin/env python3
"""
Ollama Provider - Wrapper за локален Ollama LLM (FIXED VERSION)

Changes:
- Added force_check parameter to is_available()
- Increased timeout from 2s to 5s
- Added retry counter before caching False
- Better error logging
"""

import logging
import requests
import json
from typing import Dict, Optional
from pathlib import Path
import base64


class OllamaProvider:
    """Ollama local LLM provider"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "llama3.1:8b"
    ):
        """
        Initialize Ollama provider
        
        Args:
            base_url: Ollama server URL
            model_name: Model to use
        """
        
        self.logger = logging.getLogger(__name__)
        self.base_url = base_url
        self.model_name = model_name
        self._available = None
        self._check_count = 0  # Track failed checks
    
    def is_available(self, force_check: bool = False) -> bool:
        """
        Check if Ollama server is running
        
        Args:
            force_check: Force new check even if cached
            
        Returns:
            True if available, False otherwise
        """
        
        # Return cached result if exists and not forced
        if not force_check and self._available is not None:
            return self._available
        
        try:
            # Increased timeout from 2s to 5s
            response = requests.get(
                f"{self.base_url}/api/tags", 
                timeout=5
            )
            
            if response.status_code == 200:
                self._available = True
                self._check_count = 0  # Reset counter on success
                self.logger.info(f"✓ Ollama server available at {self.base_url}")
                return True
            else:
                raise Exception(f"HTTP {response.status_code}")
        
        except Exception as e:
            self.logger.warning(f"Ollama availability check failed: {e}")
            self._check_count += 1
            
            # Only cache False after multiple failures
            # This prevents permanent "offline" status from temporary issues
            if self._check_count >= 3:
                self.logger.error(
                    f"Ollama unavailable after {self._check_count} checks, "
                    f"marking as offline"
                )
                self._available = False
            
            return False
    
    def analyze_image(self, image_path: str, additional_context: str = "") -> Dict:
        """
        Analyze image with Ollama
        
        Note: Most Ollama models don't support vision.
        We'll use filename + context instead.
        
        Args:
            image_path: Path to image
            additional_context: Additional web context
            
        Returns:
            Dict with category, description, price, tags
        """
        
        # Extract filename info
        path = Path(image_path)
        filename = path.stem
        extension = path.suffix.lower()
        
        # Create enhanced prompt
        prompt = f"""Analyze this digital asset based on available information:

Filename: {filename}
Type: {extension}
{f"Market Context: {additional_context}" if additional_context else ""}

Provide a professional assessment as a digital asset evaluator:
1. Category (choose most specific: jewelry, digital art, 3D model, template, stock photo, icon pack, design file, etc.)
2. Description (concise summary of what this likely is based on the filename and context)
3. Estimated Market Price (USD, realistic number based on category and quality indicators)
4. Keywords (5-7 comma-separated tags for marketplace listing)
5. Quality Rating (1-10 scale)

Respond ONLY with valid JSON in this exact format:
{{
    "category": "category_name",
    "description": "brief description",
    "price": 100,
    "tags": "tag1, tag2, tag3, tag4, tag5",
    "quality_rating": 8
}}

Be realistic with pricing. Digital templates: $5-50, premium designs: $20-200, specialized software/models: $50-500."""
        
        # Call Ollama with better error handling
        try:
            response_text = self.chat(prompt)
            result = self._parse_response(response_text)
            
            # Validate result
            if not self._validate_result(result):
                raise ValueError("Invalid response structure")
            
            self.logger.info(f"✓ Ollama analysis: {result.get('category')} - ${result.get('price')}")
            return result
        
        except Exception as e:
            self.logger.error(f"Ollama analysis error: {e}")
            
            # Return fallback result
            return {
                'category': 'unknown',
                'description': f"Analysis failed for {filename}",
                'price': 0,
                'tags': 'digital, asset',
                'quality_rating': 5
            }
    
    def chat(self, prompt: str, timeout: int = 30) -> str:
        """
        Chat with Ollama
        
        Args:
            prompt: Text prompt
            timeout: Request timeout in seconds
            
        Returns:
            Response text
        """
        
        # Check availability with force_check to get fresh status
        if not self.is_available(force_check=True):
            raise Exception(
                f"Ollama server not available at {self.base_url}. "
                f"Make sure Ollama is running: 'ollama serve'"
            )
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }
                },
                timeout=timeout
            )
            
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get('response', '')
            
            if not response_text:
                raise Exception("Empty response from Ollama")
            
            return response_text
        
        except requests.exceptions.Timeout:
            raise Exception(f"Ollama request timeout after {timeout}s")
        
        except requests.exceptions.ConnectionError:
            # Mark as unavailable on connection error
            self._available = False
            raise Exception(f"Cannot connect to Ollama at {self.base_url}")
        
        except Exception as e:
            raise Exception(f"Ollama chat error: {e}")
    
    def _parse_response(self, text: str) -> Dict:
        """
        Parse JSON response from Ollama
        
        Handles:
        - Markdown code blocks
        - Extra text before/after JSON
        - Malformed JSON
        """
        
        import re
        
        # Remove markdown code blocks if present
        text = text.strip()
        if '```' in text:
            # Try to extract JSON from code block
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if match:
                text = match.group(1)
        
        # Try to find JSON object in text
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            text = json_match.group(0)
        
        # Parse JSON
        try:
            result = json.loads(text)
            
            # Ensure all required fields exist with defaults
            defaults = {
                'category': 'unknown',
                'description': 'No description',
                'price': 0,
                'tags': '',
                'quality_rating': 5
            }
            
            for key, default in defaults.items():
                if key not in result:
                    result[key] = default
            
            # Normalize price to number
            if isinstance(result.get('price'), str):
                # Remove $ and convert to number
                price_str = result['price'].replace('$', '').replace(',', '').strip()
                try:
                    result['price'] = float(price_str)
                except:
                    result['price'] = 0
            
            # Ensure quality_rating is 1-10
            if 'quality_rating' in result:
                try:
                    rating = int(result['quality_rating'])
                    result['quality_rating'] = max(1, min(10, rating))
                except:
                    result['quality_rating'] = 5
            
            return result
        
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error: {e}\nText was: {text[:200]}")
            
            # Fallback: try to extract info from natural language
            return {
                'category': 'unknown',
                'description': text[:200] if text else 'Parse failed',
                'price': 0,
                'tags': '',
                'quality_rating': 5
            }
    
    def _validate_result(self, result: Dict) -> bool:
        """Validate that result has required fields"""
        required = ['category', 'description', 'price', 'tags']
        return all(k in result for k in required)
    
    def get_models(self) -> list:
        """Get list of available models"""
        if not self.is_available():
            return []
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            return [m['name'] for m in data.get('models', [])]
        except Exception as e:
            self.logger.error(f"Failed to get models: {e}")
            return []
    
    def __repr__(self):
        status = "available" if self._available else "offline"
        return f"<OllamaProvider: {self.base_url} ({status}), model={self.model_name}>"
