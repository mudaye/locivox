"""
Streaming CLI for real-time transcription
Usage: locivox stream
"""

import logging
import os
import sys
import time
from datetime import datetime
import sounddevice as sd
import numpy as np

from src.streaming import StreamingTranscriber
from src.utils import load_config, setup_logging, print_banner, print_status


class StreamingCLI:
    """CLI for real-time streaming transcription"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize streaming CLI"""
        self.config = load_config(config_path)
        self.logger = setup_logging(self.config)
        
        # Enable streaming in config
        if 'streaming' not in self.config:
            self.config['streaming'] = {}
        self.config['streaming']['enabled'] = True
        
        # Audio settings
        self.sample_rate = self.config['audio']['sample_rate']
        self.channels = self.config['audio']['channels']
        
        # Output
        self.output_file = None
        self.all_text = []
        
        # Streaming transcriber
        self.transcriber = None
        
        # Audio stream
        self.audio_stream = None
        self.is_streaming = False
    
    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio input stream"""
        if status:
            self.logger.warning(f"Audio stream status: {status}")
        
        # Convert to mono if needed
        if self.channels == 1 and len(indata.shape) > 1:
            audio_data = indata[:, 0]
        else:
            audio_data = indata.flatten()
        
        # Send to transcriber
        if self.transcriber:
            self.transcriber.add_audio(audio_data.copy())
    
    def transcription_callback(self, text: str, is_final: bool):
        """Callback for transcription results"""
        # Print to console with timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "[FINAL]" if is_final else "[  >>  ]"
        
        print(f"{timestamp} {prefix} {text}")
        sys.stdout.flush()
        
        # Store for file output
        self.all_text.append(text)
    
    def list_devices(self):
        """List available audio devices"""
        print("\nAvailable Audio Input Devices:")
        print("=" * 60)
        
        devices = sd.query_devices()
        default_input = sd.default.device[0]
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                is_default = " [DEFAULT]" if i == default_input else ""
                print(f"{i}: {device['name']}{is_default}")
                print(f"   Channels: {device['max_input_channels']}, "
                      f"Sample Rate: {device['default_samplerate']} Hz")
        
        print("=" * 60)
    
    def start_streaming(self, device: int = None):
        """Start streaming transcription"""
        print_banner()
        print_status("Starting Real-time Streaming Transcription", "info")
        
        # List devices
        self.list_devices()
        
        # Select device
        if device is None:
            device_input = input("\nSelect device (press Enter for default): ").strip()
            device = int(device_input) if device_input else None
        
        print()
        print_status(f"Initializing transcriber (model: {self.config['model']['size']})...", "info")
        
        # Create transcriber
        self.transcriber = StreamingTranscriber(
            self.config,
            callback=self.transcription_callback
        )
        
        # Start background processing
        self.transcriber.start()
        
        print_status("Transcriber ready", "success")
        
        # Open audio stream
        print_status(f"Opening audio stream (device: {device or 'default'})...", "info")
        
        try:
            self.audio_stream = sd.InputStream(
                device=device,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self.audio_callback,
                blocksize=int(self.sample_rate * 0.1)  # 100ms blocks
            )
            
            self.audio_stream.start()
            self.is_streaming = True
            
            print_status("Audio stream started", "success")
            print()
            print("=" * 60)
            print("🎤 STREAMING - Speak into your microphone")
            print("   Press Ctrl+C to stop")
            print("=" * 60)
            print()
            
            # Keep running until interrupted
            while self.is_streaming:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n")
            print_status("Stopping...", "info")
            self.stop_streaming()
            sys.exit(0)
        except Exception as e:
            print_status(f"Stream error: {e}", "error")
            self.stop_streaming()
            sys.exit(1)
    
    def stop_streaming(self):
        """Stop streaming transcription"""
        self.is_streaming = False
        
        # Stop audio stream first (prevents new data)
        if self.audio_stream:
            try:
                self.audio_stream.stop()
                self.audio_stream.close()
                self.audio_stream = None
                print_status("Audio stream stopped", "info")
            except Exception as e:
                print_status(f"Error stopping audio stream: {e}", "warning")
        
        # Stop transcriber (thread will die naturally since it's daemon)
        if self.transcriber:
            try:
                self.transcriber.stop()
                print_status("Transcriber stopped", "info")
            except Exception as e:
                print_status(f"Error stopping transcriber: {e}", "warning")
        
        # Save output
        self.save_output()
        
        # Show stats
        self.show_stats()
    
    def save_output(self):
        """Save transcription to file"""
        if not self.all_text:
            print_status("No transcription to save", "warning")
            return
        
        try:
            # Generate filename
            output_dir = self.config['output']['directory']
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/stream_{timestamp}.txt"
            
            # Create directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Write file
            full_text = ' '.join(self.all_text)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(full_text)
                f.write('\n')
            
            print()
            print_status(f"Transcription saved: {filename}", "success")
            print_status(f"Total words: {len(full_text.split())}", "info")
        except Exception as e:
            print_status(f"Error saving output: {e}", "error")
    
    def show_stats(self):
        """Show streaming statistics"""
        try:
            if self.transcriber:
                stats = self.transcriber.get_stats()
                
                print()
                print("=" * 60)
                print("STREAMING STATISTICS")
                print("=" * 60)
                print(f"Transcriptions: {stats['num_transcriptions']}")
                print(f"Total words: {stats['total_words']}")
                print(f"Total characters: {stats['total_chars']}")
                print("=" * 60)
        except Exception as e:
            print_status(f"Error showing stats: {e}", "warning")


def main():
    """Main entry point for streaming CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Locivox Real-time Streaming Transcription'
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--device',
        type=int,
        help='Audio input device index'
    )
    parser.add_argument(
        '--model',
        help='Override model size (tiny, base, small, medium, large)'
    )
    
    args = parser.parse_args()
    
    try:
        cli = StreamingCLI(args.config)
        
        # Override model if specified
        if args.model:
            cli.config['model']['size'] = args.model
        
        cli.start_streaming(device=args.device)
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
