#!/usr/bin/env python3
"""
File Analyzer - Dispatcher for different file types

Този файл само решава кой analyzer да използва.
Не прави нищо друго.
"""

from pathlib import Path
from typing import Dict, Tuple, Optional
import logging

# Import specific analyzers
from ..analyzers.document_analyzer import DocumentAnalyzer
from ..analyzers.spreadsheet_analyzer import SpreadsheetAnalyzer
from ..analyzers.media_analyzer import MediaAnalyzer
from ..analyzers.generic_analyzer import GenericAnalyzer


class FileAnalyzer:
    """
    Smart dispatcher за различни файлови типове
    
    Използване:
        analyzer = FileAnalyzer()
        file_type, metadata = analyzer.detect_file_type("/path/to/file.pdf")
    """
    
    # File type mappings
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
    DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt', '.md', '.rtf', '.odt'}
    SPREADSHEET_EXTENSIONS = {'.xlsx', '.xls', '.csv', '.tsv', '.ods'}
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.wma', '.aac'}
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    ARCHIVE_EXTENSIONS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize analyzers
        self.doc_analyzer = DocumentAnalyzer()
        self.sheet_analyzer = SpreadsheetAnalyzer()
        self.media_analyzer = MediaAnalyzer()
        self.generic_analyzer = GenericAnalyzer()
    
    def detect_file_type(self, file_path: str) -> Tuple[str, Dict]:
        """
        Detect file type and extract basic metadata
        
        Returns:
            (file_type, metadata_dict)
            
        file_type може да е:
            'image', 'document', 'spreadsheet', 'audio', 
            'video', 'archive', 'unknown'
        """
        
        path = Path(file_path)
        ext = path.suffix.lower()
        
        metadata = {
            'name': path.name,
            'extension': ext,
            'size': path.stat().st_size if path.exists() else 0
        }
        
        # Detect type
        if ext in self.IMAGE_EXTENSIONS:
            return 'image', metadata
        elif ext in self.DOCUMENT_EXTENSIONS:
            return 'document', metadata
        elif ext in self.SPREADSHEET_EXTENSIONS:
            return 'spreadsheet', metadata
        elif ext in self.AUDIO_EXTENSIONS:
            return 'audio', metadata
        elif ext in self.VIDEO_EXTENSIONS:
            return 'video', metadata
        elif ext in self.ARCHIVE_EXTENSIONS:
            return 'archive', metadata
        else:
            return 'unknown', metadata
    
    def can_extract_text(self, file_path: str) -> bool:
        """Check if we can extract text from this file"""
        
        file_type, _ = self.detect_file_type(file_path)
        return file_type in ['document', 'spreadsheet']
    
    def extract_content(self, file_path: str) -> Optional[str]:
        """
        Extract text/content from file if possible
        
        Returns:
            Text content or None
        """
        
        file_type, metadata = self.detect_file_type(file_path)
        
        try:
            if file_type == 'document':
                return self.doc_analyzer.extract_text(file_path)
            
            elif file_type == 'spreadsheet':
                return self.sheet_analyzer.extract_summary(file_path)
            
            elif file_type in ['audio', 'video']:
                return self.media_analyzer.extract_metadata_text(file_path)
            
            else:
                return None
        
        except Exception as e:
            self.logger.warning(f"Content extraction failed for {file_path}: {e}")
            return None
    
    def get_analyzer_for_type(self, file_type: str):
        """Get appropriate analyzer instance"""
        
        if file_type == 'document':
            return self.doc_analyzer
        elif file_type == 'spreadsheet':
            return self.sheet_analyzer
        elif file_type in ['audio', 'video']:
            return self.media_analyzer
        else:
            return self.generic_analyzer
