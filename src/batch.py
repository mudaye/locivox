"""
Batch processing module for Locivox Phase 3
Handles transcription of multiple files with progress tracking
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import soundfile as sf
import numpy as np
from tqdm import tqdm

from src.transcriber import TranscriberFactory
from src.vocabulary import VocabularyManager
from src.utils import load_config, generate_output_filename


class BatchProcessor:
    """Batch transcription processor"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize batch processor"""
        self.logger = logging.getLogger('locivox.batch')
        self.config = load_config(config_path)
        
        # Components
        self.transcriber = None
        self.vocabulary = VocabularyManager(self.config)
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_duration': 0.0,
            'total_words': 0,
            'errors': []
        }
        
        self.logger.info("Batch processor initialized")
    
    def process_directory(self, 
                         input_dir: str,
                         output_dir: Optional[str] = None,
                         extensions: Optional[List[str]] = None,
                         recursive: bool = False,
                         overwrite: bool = False) -> Dict:
        """
        Process all audio files in a directory
        
        Args:
            input_dir: Directory containing audio files
            output_dir: Output directory (default: config output directory)
            extensions: List of file extensions to process (default: common audio)
            recursive: Process subdirectories recursively
            overwrite: Overwrite existing transcriptions
            
        Returns:
            Dictionary with processing statistics
        """
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_dir}")
        
        # Default extensions
        if extensions is None:
            extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.opus']
        
        # Find audio files
        audio_files = self._find_audio_files(input_path, extensions, recursive)
        
        if not audio_files:
            self.logger.warning(f"No audio files found in {input_dir}")
            return self.stats
        
        self.stats['total_files'] = len(audio_files)
        self.logger.info(f"Found {len(audio_files)} audio files")
        
        # Set output directory
        if output_dir is None:
            output_dir = self.config['output']['directory']
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize transcriber (once for all files)
        self.logger.info("Loading transcription model...")
        self.transcriber = TranscriberFactory.create_transcriber(self.config)
        
        # Process files with progress bar
        print(f"\n🎤 Processing {len(audio_files)} files...\n")
        
        for audio_file in tqdm(audio_files, desc="Transcribing", unit="file"):
            try:
                self._process_file(audio_file, output_dir, overwrite)
            except Exception as e:
                self.logger.error(f"Error processing {audio_file}: {e}")
                self.stats['failed'] += 1
                self.stats['errors'].append({
                    'file': str(audio_file),
                    'error': str(e)
                })
        
        return self.stats
    
    def process_files(self,
                     file_paths: List[str],
                     output_dir: Optional[str] = None,
                     overwrite: bool = False) -> Dict:
        """
        Process specific list of files
        
        Args:
            file_paths: List of audio file paths
            output_dir: Output directory
            overwrite: Overwrite existing transcriptions
            
        Returns:
            Processing statistics
        """
        # Validate files
        valid_files = []
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists() and path.is_file():
                valid_files.append(path)
            else:
                self.logger.warning(f"File not found: {file_path}")
                self.stats['skipped'] += 1
        
        if not valid_files:
            self.logger.error("No valid files to process")
            return self.stats
        
        self.stats['total_files'] = len(valid_files)
        
        # Set output directory
        if output_dir is None:
            output_dir = self.config['output']['directory']
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize transcriber
        self.logger.info("Loading transcription model...")
        self.transcriber = TranscriberFactory.create_transcriber(self.config)
        
        # Process files
        print(f"\n🎤 Processing {len(valid_files)} files...\n")
        
        for audio_file in tqdm(valid_files, desc="Transcribing", unit="file"):
            try:
                self._process_file(audio_file, output_dir, overwrite)
            except Exception as e:
                self.logger.error(f"Error processing {audio_file}: {e}")
                self.stats['failed'] += 1
                self.stats['errors'].append({
                    'file': str(audio_file),
                    'error': str(e)
                })
        
        return self.stats
    
    def _find_audio_files(self, directory: Path, extensions: List[str], recursive: bool) -> List[Path]:
        """Find all audio files in directory"""
        audio_files = []
        
        if recursive:
            # Recursive search
            for ext in extensions:
                audio_files.extend(directory.rglob(f'*{ext}'))
        else:
            # Non-recursive search
            for ext in extensions:
                audio_files.extend(directory.glob(f'*{ext}'))
        
        return sorted(audio_files)
    
    def _process_file(self, audio_file: Path, output_dir: str, overwrite: bool) -> None:
        """Process a single audio file"""
        # Generate output filename
        output_file = self._generate_output_path(audio_file, output_dir)
        
        # Check if already exists
        if output_file.exists() and not overwrite:
            self.logger.debug(f"Skipping existing file: {output_file}")
            self.stats['skipped'] += 1
            return
        
        # Load audio
        audio_data, sample_rate = sf.read(str(audio_file))
        
        # Resample if needed
        if sample_rate != 16000:
            import librosa
            audio_data = librosa.resample(
                audio_data,
                orig_sr=sample_rate,
                target_sr=16000
            )
        
        # Convert to mono if needed
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        # Ensure float32
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
        
        # Calculate duration
        duration = len(audio_data) / 16000
        
        # Transcribe
        result = self.transcriber.transcribe(audio_data)
        
        # Apply vocabulary
        text = result.get('text', '').strip()
        if text:
            text = self.vocabulary.apply_vocabulary(text)
        
        # Save output
        output_format = self.config['output']['format']
        
        if output_format == 'txt':
            self._save_txt(text, output_file)
        elif output_format == 'json':
            result['text'] = text  # Update with vocabulary-corrected text
            self._save_json(result, output_file)
        elif output_format == 'srt':
            self._save_srt(result, output_file)
        else:
            self._save_txt(text, output_file)
        
        # Update statistics
        self.stats['successful'] += 1
        self.stats['total_duration'] += duration
        self.stats['total_words'] += len(text.split()) if text else 0
    
    def _generate_output_path(self, input_file: Path, output_dir: str) -> Path:
        """Generate output file path"""
        output_format = self.config['output']['format']
        
        # Use input filename, change extension
        output_filename = input_file.stem + f'.{output_format}'
        
        return Path(output_dir) / output_filename
    
    def _save_txt(self, text: str, output_file: Path) -> None:
        """Save as plain text"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
            f.write('\n')
    
    def _save_json(self, result: dict, output_file: Path) -> None:
        """Save as JSON"""
        import json
        
        output_file = output_file.with_suffix('.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    def _save_srt(self, result: dict, output_file: Path) -> None:
        """Save as SRT subtitles"""
        output_file = output_file.with_suffix('.srt')
        
        segments = result.get('segments', [])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                start = segment.get('start', 0)
                end = segment.get('end', 0)
                text = segment.get('text', '').strip()
                
                # Format timestamps
                start_time = self._format_srt_time(start)
                end_time = self._format_srt_time(end)
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format seconds as SRT timestamp"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def print_summary(self) -> None:
        """Print processing summary"""
        print("\n" + "=" * 60)
        print("BATCH PROCESSING SUMMARY")
        print("=" * 60)
        print(f"Total files: {self.stats['total_files']}")
        print(f"Successful: {self.stats['successful']} ✅")
        print(f"Failed: {self.stats['failed']} ❌")
        print(f"Skipped: {self.stats['skipped']} ⏭️")
        print(f"Total duration: {self.stats['total_duration']:.1f}s")
        print(f"Total words: {self.stats['total_words']:,}")
        
        if self.stats['successful'] > 0:
            avg_duration = self.stats['total_duration'] / self.stats['successful']
            print(f"Average file duration: {avg_duration:.1f}s")
        
        if self.stats['errors']:
            print(f"\nErrors:")
            for error in self.stats['errors']:
                print(f"  ❌ {error['file']}: {error['error']}")
        
        print("=" * 60)
    
    def save_report(self, report_file: str) -> None:
        """Save processing report to file"""
        import json
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.stats,
            'config': {
                'model': self.config['model']['size'],
                'engine': self.config['model']['engine'],
                'vocabulary_enabled': self.config.get('vocabulary', {}).get('enabled', False)
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Report saved to {report_file}")
