#!/usr/bin/env python3
"""
Batch Processing Example

This example shows how to transcribe multiple audio files in a directory.
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, '..')

import soundfile as sf
from tqdm import tqdm

from src.utils import load_config, print_status
from src.transcriber import TranscriberFactory


def transcribe_file(transcriber, audio_file: Path, output_dir: Path) -> dict:
    """Transcribe a single audio file"""
    try:
        # Load audio
        audio_data, sample_rate = sf.read(audio_file)
        
        # Resample if needed (Whisper expects 16kHz)
        if sample_rate != 16000:
            import librosa
            audio_data = librosa.resample(
                audio_data,
                orig_sr=sample_rate,
                target_sr=16000
            )
        
        # Transcribe
        result = transcriber.transcribe(audio_data)
        
        # Save output
        output_file = output_dir / f"{audio_file.stem}_transcript.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        
        return {
            'file': audio_file.name,
            'status': 'success',
            'output': output_file,
            'words': len(result['text'].split())
        }
        
    except Exception as e:
        return {
            'file': audio_file.name,
            'status': 'failed',
            'error': str(e)
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Batch transcribe audio files'
    )
    parser.add_argument(
        'input_dir',
        help='Directory containing audio files'
    )
    parser.add_argument(
        '--output-dir',
        default='output/batch',
        help='Output directory (default: output/batch)'
    )
    parser.add_argument(
        '--model',
        default='base',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='Model size (default: base)'
    )
    parser.add_argument(
        '--extensions',
        default='wav,mp3,flac,m4a,ogg',
        help='Comma-separated file extensions (default: wav,mp3,flac,m4a,ogg)'
    )
    
    args = parser.parse_args()
    
    # Setup
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find audio files
    extensions = args.extensions.split(',')
    audio_files = []
    for ext in extensions:
        audio_files.extend(input_dir.glob(f'*.{ext}'))
    
    if not audio_files:
        print(f"❌ No audio files found in {input_dir}")
        print(f"   Looking for: {', '.join(extensions)}")
        sys.exit(1)
    
    print(f"🎤 Locivox Batch Processing")
    print(f"📁 Input: {input_dir}")
    print(f"💾 Output: {output_dir}")
    print(f"📊 Files found: {len(audio_files)}")
    print(f"🤖 Model: {args.model}")
    print("=" * 60)
    
    # Load transcriber
    config = load_config('../config.yaml')
    config['model']['size'] = args.model
    transcriber = TranscriberFactory.create_transcriber(config)
    
    # Process files
    results = []
    for audio_file in tqdm(audio_files, desc="Transcribing"):
        result = transcribe_file(transcriber, audio_file, output_dir)
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        total_words = sum(r['words'] for r in successful)
        print(f"📝 Total words transcribed: {total_words:,}")
    
    if failed:
        print("\nFailed files:")
        for result in failed:
            print(f"  • {result['file']}: {result['error']}")
    
    # Save detailed report
    report_file = output_dir / 'batch_report.txt'
    with open(report_file, 'w') as f:
        f.write("BATCH TRANSCRIPTION REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total files: {len(audio_files)}\n")
        f.write(f"Successful: {len(successful)}\n")
        f.write(f"Failed: {len(failed)}\n\n")
        
        if successful:
            f.write("Successful transcriptions:\n")
            for result in successful:
                f.write(f"  ✓ {result['file']} -> {result['output']}\n")
        
        if failed:
            f.write("\nFailed transcriptions:\n")
            for result in failed:
                f.write(f"  ✗ {result['file']}: {result['error']}\n")
    
    print(f"\n📊 Detailed report: {report_file}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
