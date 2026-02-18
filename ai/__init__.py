"""
OMEGA AI Router Module

Production-grade AI system with intelligent failover:
- Gemini (primary) → fast and high quality
- Ollama (fallback) → always works, no limits
- Web enrichment → better results

Usage:
    from ai import AIRouter
    
    router = AIRouter(gemini_api_key="YOUR_KEY")
    result, provider = router.analyze_any_file("/path/to/file.jpg")
"""

from .ai_router import AIRouter, AIProvider

__version__ = "1.0.0"

__all__ = [
    'AIRouter',
    'AIProvider'
]
