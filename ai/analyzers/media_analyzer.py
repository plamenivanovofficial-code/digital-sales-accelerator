#!/usr/bin/env python3
"""
Media Analyzer - Audio, Video
"""

import logging
from pathlib import Path
from typing import Optional, Dict


class MediaAnalyzer:
    """Analyze audio/video files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_metadata_text(self, file_path: str) -> Optional[str]:
        """
        Extract metadata as text
        
        For audio: title, artist, album, duration
        For video: duration, resolution, codec
        """
        
        ext = Path(file_path).suffix.lower()
        
        audio_exts = {'.mp3', '.wav', '.m4a', '.flac'}
        video_exts = {'.mp4', '.avi', '.mov', '.mkv'}
        
        if ext in audio_exts:
            return self._extract_audio_metadata(file_path)
        elif ext in video_exts:
            return self._extract_video_metadata(file_path)
        else:
            return None
    
    def _extract_audio_metadata(self, file_path: str) -> Optional[str]:
        """Extract audio metadata"""
        
        try:
            from mutagen import File
            
            audio = File(file_path)
            
            if not audio:
                return f"Audio file: {Path(file_path).name}"
            
            metadata = {
                'title': audio.get('title', [Path(file_path).stem])[0],
                'artist': audio.get('artist', ['Unknown'])[0],
                'album': audio.get('album', ['Unknown'])[0],
                'duration': int(audio.info.length) if hasattr(audio, 'info') else 0
            }
            
            text = f"""Audio: {Path(file_path).name}
Title: {metadata['title']}
Artist: {metadata['artist']}
Album: {metadata['album']}
Duration: {metadata['duration']} seconds
"""
            
            return text
        
        except ImportError:
            self.logger.warning("mutagen not installed, skipping audio metadata")
            return f"Audio file: {Path(file_path).name}"
        
        except Exception as e:
            self.logger.error(f"Audio metadata error: {e}")
            return f"Audio file: {Path(file_path).name}"
    
    def _extract_video_metadata(self, file_path: str) -> Optional[str]:
        """Extract video metadata"""
        
        # За видео можем да добавим ffprobe или друг tool
        # Засега само име
        return f"Video file: {Path(file_path).name}"
