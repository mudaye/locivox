"""
Folder watching module for Locivox Phase 3
Monitors directory and auto-transcribes new audio files
"""

import logging
import os
import time
from pathlib import Path
from typing import Set, List, Optional
from datetime import datetime
import soundfile as sf
import numpy as np

from src.transcriber import TranscriberFactory
from src.vocabulary import VocabularyManager
from src.utils import load_config


class FolderWatcher:
    """Watch folder and auto-transcribe new audio files"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize folder watcher"""
        self.logger = logging.getLogger('locivox.watcher')
        self.config = load_config(config_path)
        
        # Components
        self.transcriber = None
        self.vocabulary = VocabularyManager(self.config)
        
        # Watcher state
        self.is_watching = False
        self.processed_files: Set[str] = set()
        
        # Statistics
        self.stats = {
            'files_processed': 0,
            'files_failed': 0,
            'total_duration': 0.0,
            'started_at': None
        }
        
        self.logger.info("Folder watcher initialized")
    
    def watch(self,
              watch_dir: str,
              output_dir: Optional[str] = None,
              extensions: Optional[List[str]] = None,
              poll_interval: float = 2.0,
              process_existing: bool = False) -> None:
        """
        Start watching directory for new audio files
        
        Args:
            watch_dir: Directory to watch
            output_dir: Output directory for transcriptions
            extensions: File extensions to watch (default: common audio)
            poll_interval: Seconds between directory scans
            process_existing: Process files that exist at start
        """
        watch_path = Path(watch_dir)
        
        if not watch_path.exists():
            raise FileNotFoundError(f"Watch directory not found: {watch_dir}")
        
        # Default extensions
        if extensions is None:
            extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.opus']
        
        # Set output directory
        if output_dir is None:
            output_dir = self.config['output']['directory']
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize transcriber
        self.logger.info("Loading transcription model...")
        self.transcriber = TranscriberFactory.create_transcriber(self.config)
        
        # Get existing files
        existing_files = self._scan_directory(watch_path, extensions)
        
        if process_existing:
            self.logger.info(f"Processing {len(existing_files)} existing files...")
            for file_path in existing_files:
                self._process_file(file_path, output_dir)
        else:
            # Mark as already processed (skip)
            self.processed_files.update(str(f) for f in existing_files)
            self.logger.info(f"Skipping {len(existing_files)} existing files")
        
        # Start watching
        self.is_watching = True
        self.stats['started_at'] = datetime.now()
        
        print("\n" + "=" * 60)
        print("👀 FOLDER WATCHER - Auto-Transcription Active")
        print("=" * 60)
        print(f"Watching: {watch_path}")
        print(f"Output: {output_dir}")
        print(f"Extensions: {', '.join(extensions)}")
        print(f"Poll interval: {poll_interval}s")
        print("\nWaiting for new audio files... (Press Ctrl+C to stop)")
        print("=" * 60)
        print()
        
        try:
            while self.is_watching:
                # Scan for new files
                current_files = self._scan_directory(watch_path, extensions)
                
                # Find new files
                current_paths = {str(f) for f in current_files}
                new_files = current_paths - self.processed_files
                
                # Process new files
                for file_path_str in new_files:
                    file_path = Path(file_path_str)
                    
                    # Wait a moment to ensure file is fully written
                    time.sleep(0.5)
                    
                    # Check file still exists and is not being written
                    if not self._is_file_ready(file_path):
                        continue
                    
                    # Process file
                    print(f"\n🎤 New file detected: {file_path.name}")
                    self._process_file(file_path, output_dir)
                    self.processed_files.add(file_path_str)
                
                # Sleep before next scan
                time.sleep(poll_interval)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping folder watcher...")
            self.stop()
    
    def stop(self) -> None:
        """Stop watching"""
        self.is_watching = False
        self.print_summary()
    
    def _scan_directory(self, directory: Path, extensions: List[str]) -> List[Path]:
        """Scan directory for audio files"""
        audio_files = []
        
        for ext in extensions:
            audio_files.extend(directory.glob(f'*{ext}'))
        
        return sorted(audio_files)
    
    def _is_file_ready(self, file_path: Path) -> bool:
        """
        Check if file is fully written and ready to process
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is ready
        """
        if not file_path.exists():
            return False
        
        try:
            # Try to get file size twice
            size1 = file_path.stat().st_size
            time.sleep(0.2)
            size2 = file_path.stat().st_size
            
            # File is ready if size hasn't changed
            return size1 == size2 and size1 > 0
        
        except Exception as e:
            self.logger.debug(f"File not ready: {e}")
            return False
    
    def _process_file(self, audio_file: Path, output_dir: str) -> None:
        """Process a single audio file"""
        try:
            start_time = time.time()
            
            # Generate output filename
            output_file = self._generate_output_path(audio_file, output_dir)
            
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
            
            print(f"   Transcribing ({duration:.1f}s)...")
            
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
                result['text'] = text
                self._save_json(result, output_file)
            elif output_format == 'srt':
                self._save_srt(result, output_file)
            else:
                self._save_txt(text, output_file)
            
            elapsed = time.time() - start_time
            speed = duration / elapsed if elapsed > 0 else 0
            
            # Update statistics
            self.stats['files_processed'] += 1
            self.stats['total_duration'] += duration
            
            # Print result
            print(f"   ✅ Transcribed in {elapsed:.1f}s ({speed:.1f}x speed)")
            print(f"   💾 Saved to: {output_file.name}")
            if text:
                preview = text[:100] + "..." if len(text) > 100 else text
                print(f"   📝 Preview: {preview}")
        
        except Exception as e:
            self.logger.error(f"Error processing {audio_file}: {e}", exc_info=True)
            self.stats['files_failed'] += 1
            print(f"   ❌ Error: {e}")
    
    def _generate_output_path(self, input_file: Path, output_dir: str) -> Path:
        """Generate output file path"""
        output_format = self.config['output']['format']
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
        """Print watching summary"""
        if self.stats['started_at']:
            duration = (datetime.now() - self.stats['started_at']).total_seconds()
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            
            print("\n" + "=" * 60)
            print("FOLDER WATCHER SUMMARY")
            print("=" * 60)
            print(f"Watch duration: {hours}h {minutes}m")
            print(f"Files processed: {self.stats['files_processed']} ✅")
            print(f"Files failed: {self.stats['files_failed']} ❌")
            print(f"Total audio: {self.stats['total_duration']:.1f}s")
            print("=" * 60)


def main():
    """CLI entry point for folder watcher"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Locivox Folder Watcher - Auto-transcribe new audio files'
    )
    parser.add_argument(
        'watch_dir',
        help='Directory to watch for new audio files'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Output directory (default: from config.yaml)'
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Configuration file path'
    )
    parser.add_argument(
        '--model',
        help='Override model size (tiny, base, small, medium, large)'
    )
    parser.add_argument(
        '--device',
        choices=['cpu', 'cuda'],
        help='Override device (cpu or cuda)'
    )
    parser.add_argument(
        '--format',
        choices=['txt', 'json', 'srt'],
        help='Override output format'
    )
    parser.add_argument(
        '--vocab',
        help='Path to custom vocabulary file'
    )
    parser.add_argument(
        '--enable-vocab',
        action='store_true',
        help='Enable vocabulary (uses config or --vocab file)'
    )
    parser.add_argument(
        '--extensions',
        nargs='+',
        help='File extensions to watch (e.g., .wav .mp3)'
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=2.0,
        help='Poll interval in seconds (default: 2.0)'
    )
    parser.add_argument(
        '--process-existing',
        action='store_true',
        help='Process files that exist at startup'
    )
    
    args = parser.parse_args()
    
    try:
        watcher = FolderWatcher(args.config)
        
        # Override config with CLI arguments
        if args.model:
            watcher.config['model']['size'] = args.model
        
        if args.device:
            watcher.config['model']['device'] = args.device
        
        if args.format:
            watcher.config['output']['format'] = args.format
        
        if args.vocab:
            watcher.config['vocabulary']['file'] = args.vocab
            watcher.config['vocabulary']['enabled'] = True
        
        if args.enable_vocab:
            watcher.config['vocabulary']['enabled'] = True
        
        # Reload vocabulary with updated config
        from src.vocabulary import VocabularyManager
        watcher.vocabulary = VocabularyManager(watcher.config)
        watcher.watch(
            watch_dir=args.watch_dir,
            output_dir=args.output,
            extensions=args.extensions,
            poll_interval=args.interval,
            process_existing=args.process_existing
        )
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
