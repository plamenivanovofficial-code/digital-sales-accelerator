#!/usr/bin/env python3
"""
AI Router - Intelligent AI provider routing with failover (FIXED VERSION)

Changes:
- Force re-check of Ollama availability on fallback
- Better error logging
- Progressive retry strategy
- Improved fallback chain
"""

import logging
import time
from enum import Enum
from typing import Dict, Tuple, Optional
from pathlib import Path

# File analyzer
from .helpers.file_analyzer import FileAnalyzer


class AIProvider(Enum):
    """Available AI providers"""
    GEMINI = "gemini"
    OLLAMA = "ollama"
    OLLAMA_WEB = "ollama+web"
    GENERIC = "generic"  # Fallback analyzer


class AIRouter:
    """
    Intelligent AI router with automatic failover
    
    Usage:
        router = AIRouter(gemini_api_key="YOUR_KEY")
        result, provider = router.analyze_any_file("/path/to/file.jpg")
    """
    
    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        enable_web_fallback: bool = True,
        max_web_calls_per_run: int = 50,
        log_level: str = "INFO"
    ):
        """
        Initialize AI Router
        
        Args:
            gemini_api_key: Gemini API key (optional)
            enable_web_fallback: Enable web search fallback
            max_web_calls_per_run: Max web searches per batch
            log_level: Logging level
        """
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.enable_web_fallback = enable_web_fallback
        self.max_web_calls_per_run = max_web_calls_per_run
        self.web_call_counter = 0
        
        # Initialize file analyzer
        self.file_analyzer = FileAnalyzer()
        
        # Initialize providers
        self.gemini_provider = None
        self.ollama_provider = None
        self.web_retriever = None
        
        # Try to initialize Gemini
        if gemini_api_key:
            try:
                from .providers.gemini_provider import GeminiProvider
                self.gemini_provider = GeminiProvider(gemini_api_key)
                self.logger.info("✓ Gemini provider initialized")
            except Exception as e:
                self.logger.warning(f"Gemini provider failed: {e}")
        
        # Try to initialize Ollama
        try:
            from .providers.ollama_provider import OllamaProvider
            self.ollama_provider = OllamaProvider()
            
            # Do initial check
            if self.ollama_provider.is_available():
                self.logger.info(f"✓ Ollama provider initialized and available")
            else:
                self.logger.warning(f"Ollama provider initialized but not available (will retry on demand)")
        
        except Exception as e:
            self.logger.warning(f"Ollama provider not available: {e}")
        
        # Try to initialize web retriever
        if enable_web_fallback:
            try:
                from .helpers.web_retriever import WebRetriever
                self.web_retriever = WebRetriever()
                self.logger.info("✓ Web retriever initialized")
            except Exception as e:
                self.logger.warning(f"Web retriever not available: {e}")
        
        # Statistics
        self.stats = {
            'gemini_calls': 0,
            'gemini_successes': 0,
            'gemini_rate_limits': 0,
            'gemini_safety_blocks': 0,
            'ollama_calls': 0,
            'ollama_successes': 0,
            'total_fallbacks': 0,
            'web_searches': 0,
            'generic_fallbacks': 0  # Track when we fall back to generic analyzer
        }
    
    def __str__(self):
        available = []
        if self.gemini_provider and self.gemini_provider.is_available():
            available.append("Gemini")
        if self.ollama_provider and self.ollama_provider.is_available():
            available.append("Ollama")
        if self.web_retriever:
            available.append("Web")
        
        return f"AIRouter(providers: {', '.join(available) if available else 'None'})"
    
    def analyze_any_file(self, file_path: str, fallback_description: str = "") -> Tuple[Dict, AIProvider]:
        """
        Analyze ANY file type with appropriate strategy
        
        Args:
            file_path: Path to file
            fallback_description: Fallback description if AI fails
            
        Returns:
            (result_dict, provider_used)
        """
        
        # Detect file type
        file_type, metadata = self.file_analyzer.detect_file_type(file_path)
        
        self.logger.info(f"Analyzing {file_type}: {metadata['name']}")
        
        # IMAGES - use vision analysis
        if file_type == 'image':
            return self.analyze_asset(file_path, fallback_description)
        
        # DOCUMENTS, SPREADSHEETS - extract text + AI
        elif file_type in ['document', 'spreadsheet']:
            return self._analyze_text_based_file(file_path, file_type, metadata)
        
        # MEDIA - metadata + filename analysis
        elif file_type in ['audio', 'video']:
            return self._analyze_media_file(file_path, metadata)
        
        # OTHER - smart filename analysis
        else:
            return self._analyze_generic_file(file_path, metadata)
    
    def analyze_asset(self, image_path: str, fallback_description: str = "") -> Tuple[Dict, AIProvider]:
        """
        Analyze image asset (existing method for compatibility)
        
        Try Gemini first, fallback to Ollama+Web, then generic
        """
        
        # Try Gemini first
        if self.gemini_provider and self.gemini_provider.is_available():
            try:
                self.stats['gemini_calls'] += 1
                self.logger.info(f"Attempting Gemini analysis...")
                
                result = self.gemini_provider.analyze_image(image_path)
                
                self.stats['gemini_successes'] += 1
                self.logger.info(f"✓ Gemini analysis succeeded")
                
                return result, AIProvider.GEMINI
            
            except Exception as e:
                error_str = str(e).lower()
                
                if '429' in error_str or 'rate limit' in error_str:
                    self.stats['gemini_rate_limits'] += 1
                    self.logger.warning(f"⚠️ Gemini rate limited, falling back to Ollama...")
                
                elif 'safety' in error_str or 'blocked' in error_str:
                    self.stats['gemini_safety_blocks'] += 1
                    self.logger.warning(f"⚠️ Gemini safety block, falling back to Ollama...")
                
                else:
                    self.logger.warning(f"⚠️ Gemini error: {e}, falling back...")
        
        else:
            self.logger.info("Gemini not available, trying Ollama...")
        
        # Fallback to Ollama
        return self._fallback_analysis(image_path, fallback_description)
    
    def _analyze_text_based_file(self, file_path, file_type, metadata):
        """Analyze documents/spreadsheets"""
        
        # Extract content
        content = self.file_analyzer.extract_content(file_path)
        
        if not content:
            # Fallback to generic
            return self._analyze_generic_file(file_path, metadata)
        
        # Create prompt
        prompt = f"""Analyze this {file_type}:

File: {metadata['name']}
Content preview:
{content[:3000]}

Provide JSON with:
- category (e.g., "document", "invoice", "contract", "spreadsheet", "data", etc.)
- description (brief summary of content)
- price (estimated value 0-10000, use 0 if not applicable)
- tags (comma separated keywords)

Respond ONLY with valid JSON, no other text."""
        
        # Try AI
        try:
            response, provider = self._try_gemini_then_ollama(prompt)
            result = self._parse_ai_response(response)
            return result, provider
        
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return self._analyze_generic_file(file_path, metadata)
    
    def _analyze_media_file(self, file_path, metadata):
        """Analyze audio/video"""
        
        content = self.file_analyzer.extract_content(file_path)
        
        if not content:
            return self._analyze_generic_file(file_path, metadata)
        
        prompt = f"""Analyze this media file:

{content}

Provide JSON with:
- category (e.g., "music", "podcast", "video", "movie", etc.)
- description (what is it about)
- price (estimated value 0-1000)
- tags (comma separated)

Respond ONLY with valid JSON."""
        
        try:
            response, provider = self._try_gemini_then_ollama(prompt)
            result = self._parse_ai_response(response)
            return result, provider
        except:
            return self._analyze_generic_file(file_path, metadata)
    
    def _analyze_generic_file(self, file_path, metadata):
        """Fallback to filename analysis"""
        
        self.stats['generic_fallbacks'] += 1
        
        analyzer = self.file_analyzer.generic_analyzer
        result = analyzer.analyze_from_filename(file_path)
        
        self.logger.info(f"Using generic filename analysis")
        
        return result, AIProvider.GENERIC
    
    def _fallback_analysis(self, image_path: str, fallback_description: str) -> Tuple[Dict, AIProvider]:
        """
        Fallback to Ollama + optional Web
        
        FIXED: Force re-check Ollama availability before giving up
        """
        
        self.stats['total_fallbacks'] += 1
        
        # Use Ollama if available (FORCE RE-CHECK)
        if self.ollama_provider:
            self.logger.info("Checking Ollama availability...")
            
            # CRITICAL FIX: Force re-check instead of using cached status
            if self.ollama_provider.is_available(force_check=True):
                try:
                    self.stats['ollama_calls'] += 1
                    self.logger.info("✓ Ollama available, attempting analysis...")
                    
                    # Get web context if enabled
                    web_context = ""
                    if self.enable_web_fallback and self.web_call_counter < self.max_web_calls_per_run:
                        self.logger.info("Fetching web context...")
                        web_context = self._get_web_context(fallback_description)
                    
                    # Analyze with Ollama
                    result = self.ollama_provider.analyze_image(
                        image_path,
                        additional_context=web_context
                    )
                    
                    self.stats['ollama_successes'] += 1
                    
                    provider = AIProvider.OLLAMA_WEB if web_context else AIProvider.OLLAMA
                    self.logger.info(f"✓ Ollama analysis succeeded ({provider.value})")
                    
                    return result, provider
                
                except Exception as e:
                    self.logger.error(f"❌ Ollama analysis failed: {e}")
            
            else:
                self.logger.warning("Ollama not available after re-check")
        
        else:
            self.logger.warning("Ollama provider not initialized")
        
        # Last resort: generic analysis
        self.logger.warning("All AI providers failed, using generic filename analysis")
        
        path = Path(image_path)
        metadata = {
            'name': path.name,
            'extension': path.suffix.lower(),
            'size': path.stat().st_size if path.exists() else 0
        }
        
        return self._analyze_generic_file(image_path, metadata)
    
    def _try_gemini_then_ollama(self, prompt: str) -> Tuple[str, AIProvider]:
        """
        Helper: try Gemini, fallback to Ollama
        
        FIXED: Force Ollama re-check on fallback
        """
        
        # Try Gemini
        if self.gemini_provider and self.gemini_provider.is_available():
            try:
                self.stats['gemini_calls'] += 1
                response = self.gemini_provider.chat(prompt)
                self.stats['gemini_successes'] += 1
                return response, AIProvider.GEMINI
            except Exception as e:
                self.logger.warning(f"Gemini chat failed: {e}")
        
        # Fallback Ollama (with force_check)
        if self.ollama_provider and self.ollama_provider.is_available(force_check=True):
            self.stats['ollama_calls'] += 1
            response = self.ollama_provider.chat(prompt)
            self.stats['ollama_successes'] += 1
            return response, AIProvider.OLLAMA
        
        raise Exception("No AI provider available")
    
    def _get_web_context(self, query: str) -> str:
        """Get web context for query"""
        
        if not self.web_retriever or not query:
            return ""
        
        try:
            self.web_call_counter += 1
            self.stats['web_searches'] += 1
            
            context = self.web_retriever.search(query)
            self.logger.info(f"Web search completed for: {query[:50]}...")
            return context
        
        except Exception as e:
            self.logger.warning(f"Web search failed: {e}")
            return ""
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response to extract JSON"""
        
        import json
        import re
        
        # Try direct JSON parse
        try:
            return json.loads(response)
        except:
            pass
        
        # Try to extract JSON from markdown
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # Try to find any JSON object
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        # Fallback: create minimal response
        return {
            'category': 'unknown',
            'description': response[:200],
            'price': 0,
            'tags': ''
        }
    
    def chat(self, prompt: str) -> Tuple[str, AIProvider]:
        """
        Chat with AI (text-only)
        
        Returns:
            (response_text, provider_used)
        """
        
        try:
            response, provider = self._try_gemini_then_ollama(prompt)
            return response, provider
        except Exception as e:
            return f"Error: {e}", AIProvider.GENERIC
    
    def reset(self):
        """
        Reset router state
        
        Call this before starting a new scan batch to:
        - Clear provider availability cache
        - Reset web call counter
        - Reset statistics
        """
        
        self.logger.info("Resetting AI Router state...")
        
        # Reset web counter
        self.web_call_counter = 0
        
        # Force re-check of providers
        if self.ollama_provider:
            self.ollama_provider._available = None
            self.ollama_provider._check_count = 0
        
        if self.gemini_provider:
            # Gemini provider might have its own cache
            pass
        
        # Reset stats
        self.stats = {
            'gemini_calls': 0,
            'gemini_successes': 0,
            'gemini_rate_limits': 0,
            'gemini_safety_blocks': 0,
            'ollama_calls': 0,
            'ollama_successes': 0,
            'total_fallbacks': 0,
            'web_searches': 0,
            'generic_fallbacks': 0
        }
        
        self.logger.info("✓ Router reset complete")
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        stats = self.stats.copy()
        
        # Add provider status
        stats['providers'] = {
            'gemini': self.gemini_provider.is_available() if self.gemini_provider else False,
            'ollama': self.ollama_provider.is_available() if self.ollama_provider else False,
            'web': self.web_retriever is not None
        }
        
        return stats
    
    def reset_web_call_counter(self):
        """Reset web call counter (use between batches)"""
        self.web_call_counter = 0
        self.logger.info("Web call counter reset")
