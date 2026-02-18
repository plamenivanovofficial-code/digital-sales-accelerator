#!/usr/bin/env python3
"""
Generic Analyzer - За всичко останало
"""

import logging
from pathlib import Path
from typing import Dict


class GenericAnalyzer:
    """
    Fallback analyzer за неподдържани файлове
    
    Използва:
    - Име на файла
    - Разширение
    - Размер
    - Дата
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_from_filename(self, file_path: str) -> Dict:
        """
        Smart analysis based on filename patterns
        
        Примери:
        - "antique_vase_1920.jpg" → category: antiques, era: 1920s
        - "gold_ring_14k.png" → category: jewelry, material: gold
        """
        
        path = Path(file_path)
        name_lower = path.stem.lower()
        
        # Keyword detection
        category = self._detect_category(name_lower)
        price = self._estimate_price_from_name(name_lower)
        tags = self._extract_tags_from_name(name_lower)
        
        return {
            'category': category,
            'description': f"File: {path.name}",
            'price': price,
            'tags': tags
        }
    
    def _detect_category(self, name: str) -> str:
        """Detect category from filename"""
        
        keywords = {
            'jewelry': ['ring', 'necklace', 'bracelet', 'earring', 'gold', 'silver'],
            'antiques': ['antique', 'vintage', 'old', 'ancient', 'historic'],
            'art': ['painting', 'art', 'canvas', 'drawing', 'sculpture'],
            'collectibles': ['coin', 'stamp', 'card', 'comic', 'toy'],
            'furniture': ['chair', 'table', 'desk', 'cabinet', 'sofa'],
        }
        
        for category, words in keywords.items():
            if any(word in name for word in words):
                return category
        
        return 'general'
    
    def _estimate_price_from_name(self, name: str) -> float:
        """Estimate price from filename keywords"""
        
        # Простичък heuristic
        if 'gold' in name or 'diamond' in name:
            return 500.0
        elif 'silver' in name or 'antique' in name:
            return 200.0
        elif 'vintage' in name:
            return 100.0
        else:
            return 50.0
    
    def _extract_tags_from_name(self, name: str) -> str:
        """Extract tags from filename"""
        
        # Split by underscores/dashes and use as tags
        parts = name.replace('-', '_').split('_')
        
        # Filter out numbers and short words
        tags = [p for p in parts if len(p) > 2 and not p.isdigit()]
        
        return ', '.join(tags[:5])  # Max 5 tags
