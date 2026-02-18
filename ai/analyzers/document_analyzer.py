#!/usr/bin/env python3
"""
Document Analyzer - PDF, DOCX, TXT
"""

import logging
from pathlib import Path
from typing import Optional


class DocumentAnalyzer:
    """Analyze text documents"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text(self, file_path: str, max_chars: int = 5000) -> Optional[str]:
        """
        Extract text from document
        
        Supports:
        - TXT, MD
        - DOCX
        - PDF (ако има PyPDF2)
        """
        
        ext = Path(file_path).suffix.lower()
        
        try:
            # Plain text
            if ext in ['.txt', '.md']:
                return self._extract_plain_text(file_path, max_chars)
            
            # DOCX
            elif ext == '.docx':
                return self._extract_docx_text(file_path, max_chars)
            
            # PDF
            elif ext == '.pdf':
                return self._extract_pdf_text(file_path, max_chars)
            
            else:
                self.logger.warning(f"Unsupported document type: {ext}")
                return None
        
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return None
    
    def _extract_plain_text(self, file_path: str, max_chars: int) -> str:
        """Extract from TXT/MD files"""
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()[:max_chars]
    
    def _extract_docx_text(self, file_path: str, max_chars: int) -> Optional[str]:
        """Extract from DOCX files"""
        
        try:
            # Try python-docx first
            from docx import Document
            
            doc = Document(file_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
            return text[:max_chars]
        
        except ImportError:
            self.logger.warning("python-docx not installed, skipping DOCX")
            return None
        
        except Exception as e:
            self.logger.error(f"DOCX extraction error: {e}")
            return None
    
    def _extract_pdf_text(self, file_path: str, max_chars: int) -> Optional[str]:
        """Extract from PDF files"""
        
        try:
            import PyPDF2
            
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                # First 3 pages
                num_pages = min(3, len(reader.pages))
                
                for i in range(num_pages):
                    text += reader.pages[i].extract_text()
            
            return text[:max_chars]
        
        except ImportError:
            self.logger.warning("PyPDF2 not installed, skipping PDF")
            return None
        
        except Exception as e:
            self.logger.error(f"PDF extraction error: {e}")
            return None
