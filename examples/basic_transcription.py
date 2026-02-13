#!/usr/bin/env python3
"""
Basic Transcription Example

This example shows the simplest way to use Locivox programmatically.
"""

import sys
sys.path.insert(0, '..')

from src.utils import load_config
from src.audio_capture import AudioCapture
from src.transcriber import TranscriberFactory


def main():
    # Load configuration
    config = load_config('config.yaml')
    
    # Initialize components
    audio_capture = AudioCapture(config)
    transcriber = TranscriberFactory.create_transcriber(config)
    
    print("🎤 Locivox Basic Example")
    print("=" * 50)
    
    # List available audio devices
    audio_capture.list_devices()
    
    # Get user input
    device_input = input("\nSelect device (press Enter for default): ").strip()
    device = int(device_input) if device_input else None
    
    # Start recording
    print("\nPress ENTER to start recording...")
    input()
    
    audio_capture.start_recording(device=device)
    print("🔴 Recording... Press ENTER to stop")
    
    input()
    
    # Stop recording
    audio_data = audio_capture.stop_recording()
    print(f"✅ Recorded {len(audio_data)} samples")
    
    # Transcribe
    print("\n🤖 Transcribing...")
    result = transcriber.transcribe(audio_data)
    
    # Display result
    print("\n" + "=" * 50)
    print("TRANSCRIPTION:")
    print("=" * 50)
    print(result['text'])
    print("=" * 50)
    
    if 'language' in result:
        print(f"\n🌍 Detected language: {result['language']}")
    
    # Save to file
    output_file = 'output/basic_example.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result['text'])
    
    print(f"💾 Saved to: {output_file}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
