#!/usr/bin/env python3
"""
Spreadsheet Analyzer - XLSX, CSV
"""

import logging
from pathlib import Path
from typing import Optional


class SpreadsheetAnalyzer:
    """Analyze spreadsheet files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_summary(self, file_path: str, max_rows: int = 10) -> Optional[str]:
        """
        Extract summary from spreadsheet
        
        Returns text summary with:
        - File name
        - Column names
        - Row count
        - Sample data
        """
        
        ext = Path(file_path).suffix.lower()
        
        try:
            import pandas as pd
            
            # Read file
            if ext == '.csv':
                df = pd.read_csv(file_path, nrows=max_rows)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, nrows=max_rows)
            else:
                return None
            
            # Create summary
            summary = f"""Spreadsheet: {Path(file_path).name}
Columns: {', '.join(df.columns.tolist())}
Rows: {len(df)}

Sample data:
{df.head().to_string()}
"""
            
            return summary
        
        except ImportError:
            self.logger.warning("pandas not installed, skipping spreadsheet")
            return None
        
        except Exception as e:
            self.logger.error(f"Spreadsheet extraction error: {e}")
            return None
