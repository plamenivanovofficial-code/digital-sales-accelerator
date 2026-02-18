"""
AI Router Wrapper for OMEGA v4 Titanium
Provides seamless integration between OMEGA and AI Router
"""

import os
import sys
from typing import Dict, Optional, Tuple
from pathlib import Path

# Import AI Router
from ai import AIRouter, AIProvider

import config


class OmegaAIRouter:
    """
    Wrapper class for AI Router integration in OMEGA
    
    Handles:
    - Initialization with OMEGA config
    - Fallback management
    - Statistics tracking
    - File type detection and routing
    """
    
    def __init__(self):
        """Initialize AI Router with OMEGA configuration"""
        
        # Get Gemini API key from config
        api_key = getattr(config, 'GEMINI_API_KEY', None)
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in config")
        
        # Initialize AI Router
        self.router = AIRouter(
            gemini_api_key=api_key,
            enable_web_fallback=getattr(config, 'ENABLE_WEB_FALLBACK', True),
            max_web_calls_per_run=getattr(config, 'MAX_WEB_CALLS_PER_BATCH', 50),
            log_level=getattr(config, 'AI_ROUTER_LOG_LEVEL', 'INFO')
        )
        
        print("✅ AI Router initialized successfully")
        print(f"   {self.router}")
    
    def analyze_file(self, file_path: str) -> Tuple[Dict, str]:
        """
        Analyze ANY type of file with AI
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (result_dict, provider_name)
        """
        
        try:
            result, provider = self.router.analyze_any_file(
                file_path=file_path,
                fallback_description=os.path.basename(file_path)
            )
            
            return result, provider.value
            
        except Exception as e:
            print(f"⚠️  AI Router error: {e}")
            
            return {
                'category': 'Unknown',
                'description': f"File: {os.path.basename(file_path)}",
                'price': 0,
                'saleable': 0,
                'tags': '',
                'quality_rating': 5
            }, 'generic'
    
    def analyze_image(self, image_path: str) -> Tuple[Dict, str]:
        """
        Legacy method for backward compatibility
        """
        
        try:
            result, provider = self.router.analyze_asset(
                image_path=image_path,
                fallback_description=os.path.basename(image_path)
            )
            
            return result, provider.value
            
        except Exception as e:
            print(f"⚠️  Image analysis error: {e}")
            
            return {
                'category': 'Unknown',
                'description': f"Image: {os.path.basename(image_path)}",
                'price': 0,
                'saleable': 0,
                'tags': '',
                'quality_rating': 5
            }, 'generic'
    
    def get_stats(self) -> Dict:
        """Get AI Router statistics"""
        return self.router.get_stats()
    
    def reset_web_counter(self):
        """Reset web call counter for new batch"""
        self.router.reset_web_call_counter()
    
    def __repr__(self):
        return f"<OmegaAIRouter: {self.router}>"


# Global singleton instance
_ai_router_instance = None


def get_ai_router() -> OmegaAIRouter:
    """
    Get or create AI Router singleton instance
    
    Usage:
        from ai_router_wrapper import get_ai_router
        
        router = get_ai_router()
        result, provider = router.analyze_file("/path/to/file.jpg")
    """
    
    global _ai_router_instance
    
    if _ai_router_instance is None:
        _ai_router_instance = OmegaAIRouter()
    
    return _ai_router_instance
