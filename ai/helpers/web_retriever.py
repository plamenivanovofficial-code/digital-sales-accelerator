#!/usr/bin/env python3
"""
Web Retriever - Web search with caching
"""

import logging
import hashlib
import json
import time
from typing import Optional
from pathlib import Path
from datetime import datetime, timedelta


class WebRetriever:
    """Web search with caching"""
    
    def __init__(self, cache_dir: str = ".web_cache", cache_hours: int = 24):
        """
        Initialize web retriever
        
        Args:
            cache_dir: Cache directory
            cache_hours: Cache validity in hours
        """
        
        self.logger = logging.getLogger(__name__)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_hours = cache_hours
        
        # Try to import duckduckgo_search
        try:
            from duckduckgo_search import DDGS
            self.ddgs = DDGS()
            self.available = True
            self.logger.info("Web retriever initialized (DuckDuckGo)")
        except ImportError:
            self.logger.warning("duckduckgo_search not installed, web search disabled")
            self.ddgs = None
            self.available = False
    
    def is_available(self) -> bool:
        """Check if web search is available"""
        return self.available
    
    def search(self, query: str, max_results: int = 3) -> str:
        """
        Search web and return context
        
        Args:
            query: Search query
            max_results: Max results to fetch
            
        Returns:
            Formatted context string
        """
        
        if not self.available:
            return ""
        
        # Check cache first
        cached = self._get_cached(query)
        if cached:
            self.logger.info(f"Using cached results for: {query}")
            return cached
        
        # Perform search
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            
            # Format results
            context = self._format_results(results)
            
            # Cache results
            self._save_cache(query, context)
            
            self.logger.info(f"Web search completed: {query} ({len(results)} results)")
            
            return context
        
        except Exception as e:
            self.logger.error(f"Web search failed: {e}")
            return ""
    
    def _format_results(self, results: list) -> str:
        """Format search results as context"""
        
        if not results:
            return ""
        
        context_parts = ["Web search results:"]
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('body', 'No description')
            
            context_parts.append(f"\n{i}. {title}")
            context_parts.append(f"   {snippet[:200]}")
        
        return '\n'.join(context_parts)
    
    def _get_cache_path(self, query: str) -> Path:
        """Get cache file path for query"""
        
        # Create hash of query
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return self.cache_dir / f"{query_hash}.json"
    
    def _get_cached(self, query: str) -> Optional[str]:
        """Get cached results if available and not expired"""
        
        cache_file = self._get_cache_path(query)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Check expiry
            cached_time = datetime.fromisoformat(data['timestamp'])
            expiry_time = cached_time + timedelta(hours=self.cache_hours)
            
            if datetime.now() > expiry_time:
                # Expired
                cache_file.unlink()
                return None
            
            return data['context']
        
        except Exception as e:
            self.logger.warning(f"Cache read error: {e}")
            return None
    
    def _save_cache(self, query: str, context: str):
        """Save results to cache"""
        
        cache_file = self._get_cache_path(query)
        
        try:
            data = {
                'query': query,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        
        except Exception as e:
            self.logger.warning(f"Cache write error: {e}")
