"""
AI Engine Wrapper - Uses AI Router when available
Falls back to original ai_engine if AI Router not configured
"""

import os
from typing import Dict, Optional, Tuple
import config

# Try to import AI Router
try:
    from ai_router_wrapper import get_ai_router
    AI_ROUTER_AVAILABLE = True
except ImportError:
    AI_ROUTER_AVAILABLE = False
    print("⚠️  AI Router not available - using original ai_engine")

# Import original ai_engine as fallback
import ai_engine as original_ai_engine


def analyze_asset(image_path: str, file_info: Optional[Dict] = None) -> Dict:
    """
    Analyze asset with AI Router if available, otherwise use original ai_engine
    
    Args:
        image_path: Path to image file
        file_info: Optional file metadata
        
    Returns:
        Dict with AI analysis results
    """
    
    # Check if AI Router is enabled
    use_router = (
        AI_ROUTER_AVAILABLE and 
        getattr(config, 'ENABLE_AI_ROUTER', False) and
        config.GEMINI_API_KEY
    )
    
    if use_router:
        try:
            # Use AI Router
            router = get_ai_router()
            result, provider = router.analyze_file(image_path)
            
            # Add provider info
            result['ai_provider'] = provider
            
            print(f"   ✓ AI Router used: {provider}")
            return result
            
        except Exception as e:
            print(f"   ⚠️  AI Router failed: {e}")
            print(f"   → Falling back to original ai_engine")
            # Fall through to original engine
    
    # Use original ai_engine
    try:
        result = original_ai_engine.analyze_asset_with_vision(image_path)
        result['ai_provider'] = 'gemini-direct'
        return result
    except Exception as e:
        print(f"   ✗ AI analysis failed: {e}")
        return {
            'category': 'Unknown',
            'description': f"Error analyzing file: {os.path.basename(image_path)}",
            'price': 0,
            'saleable': 0,
            'tags': '',
            'quality_rating': 0,
            'ai_provider': 'error'
        }


def chat(prompt: str, context: Optional[str] = None) -> str:
    """
    Chat with AI (text-only, no images)
    
    Args:
        prompt: User prompt
        context: Optional context
        
    Returns:
        AI response text
    """
    
    # For chat, always use original ai_engine as AI Router is for file analysis
    try:
        return original_ai_engine.chat_with_ai(prompt, context=context)
    except Exception as e:
        return f"AI Error: {str(e)}"


# Re-export everything else from original ai_engine
analyze_asset_with_vision = original_ai_engine.analyze_asset_with_vision
chat_with_ai = original_ai_engine.chat_with_ai
extract_json = original_ai_engine.extract_json
