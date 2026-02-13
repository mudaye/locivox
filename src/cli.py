"""
Locivox CLI - Main command-line interface
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import (
    load_config, 
    setup_logging, 
    generate_output_filename,
    print_banner,
    print_status
)
from src.audio_capture import AudioCapture
from src.transcriber import TranscriberFactory


class LocivoxCLI:
    """Main CLI application"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.logger = setup_logging(self.config)
        self.audio_capture = AudioCapture(self.config)
        self.transcriber = TranscriberFactory.create_transcriber(self.config)
    
    def run_interactive(self) -> None:
        """Run interactive recording session"""
        print_banner()
        
        # Show available devices
        self.audio_capture.list_devices()
        
        # Get device selection
        device_input = input("Select input device (press Enter for default): ").strip()
        device = int(device_input) if device_input else None
        
        print_status("Press ENTER to start recording...", "info")
        input()
        
        try:
            # Start recording
            self.audio_capture.start_recording(device=device)
            print_status("Recording started! Press ENTER to stop...", "success")
            
            # Wait for user to stop
            input()
            
            # Stop recording
            audio_data = self.audio_capture.stop_recording()
            
            if len(audio_data) == 0:
                print_status("No audio recorded. Exiting.", "warning")
                return
            
            # Save audio file (optional)
            audio_filename = generate_output_filename(
                self.config, 
                prefix="recording"
            ).replace('.txt', '.wav')
            self.audio_capture.save_audio(audio_data, audio_filename)
            
            # Transcribe
            print_status("Transcribing audio...", "info")
            result = self.transcriber.transcribe(audio_data)
            
            # Display results
            print("\n" + "=" * 60)
            print("TRANSCRIPTION:")
            print("=" * 60)
            print(result['text'])
            print("=" * 60)
            
            if 'language' in result:
                print(f"\nDetected Language: {result['language']}")
            
            # Save to file
            output_filename = generate_output_filename(self.config)
            self.save_transcription(result, output_filename)
            print_status(f"Transcription saved to: {output_filename}", "success")
            
        except KeyboardInterrupt:
            print_status("\n\nRecording interrupted by user.", "warning")
            self.audio_capture.stop_recording()
        except Exception as e:
            self.logger.error(f"Error during recording: {e}", exc_info=True)
            print_status(f"Error: {e}", "error")
    
    def transcribe_file(self, audio_file: str) -> None:
        """Transcribe an existing audio file"""
        print_banner()
        print_status(f"Loading audio file: {audio_file}", "info")
        
        try:
            import soundfile as sf
            
            # Load audio file
            audio_data, sample_rate = sf.read(audio_file)
            
            # Resample if needed (Whisper expects 16kHz)
            expected_rate = self.config['audio']['sample_rate']
            if sample_rate != expected_rate:
                print_status(f"Resampling from {sample_rate}Hz to {expected_rate}Hz", "info")
                try:
                    import librosa
                    audio_data = librosa.resample(
                        audio_data, 
                        orig_sr=sample_rate, 
                        target_sr=expected_rate
                    )
                except ImportError:
                    print_status("Warning: librosa not available. Skipping resample.", "warning")
                    print_status("Audio may not transcribe optimally. Install with: pip install librosa", "info")
            
            # Transcribe
            print_status("Transcribing audio...", "info")
            result = self.transcriber.transcribe(audio_data)
            
            # Display results
            print("\n" + "=" * 60)
            print("TRANSCRIPTION:")
            print("=" * 60)
            print(result['text'])
            print("=" * 60)
            
            # Save to file
            output_filename = generate_output_filename(self.config)
            self.save_transcription(result, output_filename)
            print_status(f"Transcription saved to: {output_filename}", "success")
            
        except Exception as e:
            self.logger.error(f"Error transcribing file: {e}", exc_info=True)
            print_status(f"Error: {e}", "error")
    
    def save_transcription(self, result: dict, filepath: str) -> None:
        """Save transcription to file"""
        output_format = self.config.get('output', {}).get('format', 'txt')
        
        if output_format == 'txt':
            self._save_as_txt(result, filepath)
        elif output_format == 'json':
            self._save_as_json(result, filepath)
        elif output_format == 'srt':
            self._save_as_srt(result, filepath)
        else:
            self._save_as_txt(result, filepath)
    
    def _save_as_txt(self, result: dict, filepath: str) -> None:
        """Save as plain text"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result['text'])
            f.write('\n')
    
    def _save_as_json(self, result: dict, filepath: str) -> None:
        """Save as JSON with segments"""
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    def _save_as_srt(self, result: dict, filepath: str) -> None:
        """Save as SRT subtitle format"""
        if 'segments' not in result:
            self._save_as_txt(result, filepath)
            return
        
        from src.utils import format_timestamp
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments'], 1):
                start = format_timestamp(segment['start']).replace('.', ',')
                end = format_timestamp(segment['end']).replace('.', ',')
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment['text']}\n\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Locivox - Local Voice Transcription System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config', 
        type=str, 
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--file', 
        type=str,
        help='Transcribe an existing audio file'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='Override model size from config'
    )
    
    parser.add_argument(
        '--language',
        type=str,
        help='Override language from config (e.g., en, es, fr, or auto)'
    )
    
    parser.add_argument(
        '--output-format',
        type=str,
        choices=['txt', 'json', 'srt'],
        help='Override output format from config'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize CLI
        cli = LocivoxCLI(config_path=args.config)
        
        # Override config with CLI arguments
        if args.model:
            cli.config['model']['size'] = args.model
            # Reload transcriber with new config
            cli.transcriber = TranscriberFactory.create_transcriber(cli.config)
        
        if args.language:
            cli.config['model']['language'] = args.language
        
        if args.output_format:
            cli.config['output']['format'] = args.output_format
        
        # Run appropriate mode
        if args.file:
            cli.transcribe_file(args.file)
        else:
            cli.run_interactive()
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
