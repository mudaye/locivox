#!/usr/bin/env python3
"""
Custom Model Example

This example shows how to:
- Use different models programmatically
- Compare model performance
- Switch between engines (faster-whisper vs openai-whisper)
"""

import sys
import time
sys.path.insert(0, '..')

import numpy as np
import soundfile as sf

from src.transcriber import TranscriberFactory


def create_custom_config(model_size: str, engine: str = 'faster-whisper') -> dict:
    """Create a custom configuration"""
    return {
        'model': {
            'engine': engine,
            'size': model_size,
            'device': 'cpu',
            'compute_type': 'int8',
            'language': 'en'
        },
        'audio': {
            'sample_rate': 16000,
            'channels': 1
        },
        'output': {
            'directory': './output',
            'format': 'txt'
        },
        'logging': {
            'level': 'WARNING',  # Reduce noise for benchmarking
            'console': False
        }
    }


def benchmark_model(model_size: str, audio_file: str, engine: str = 'faster-whisper'):
    """Benchmark a specific model"""
    print(f"\n{'='*60}")
    print(f"Testing: {engine} / {model_size}")
    print(f"{'='*60}")
    
    # Load audio
    audio_data, sample_rate = sf.read(audio_file)
    if sample_rate != 16000:
        import librosa
        audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
    
    duration = len(audio_data) / 16000
    print(f"Audio duration: {duration:.2f}s")
    
    # Create transcriber
    config = create_custom_config(model_size, engine)
    
    try:
        print("Loading model...")
        load_start = time.time()
        transcriber = TranscriberFactory.create_transcriber(config)
        load_time = time.time() - load_start
        print(f"✓ Model loaded in {load_time:.2f}s")
        
        # Transcribe
        print("Transcribing...")
        transcribe_start = time.time()
        result = transcriber.transcribe(audio_data)
        transcribe_time = time.time() - transcribe_start
        
        # Results
        speed_factor = duration / transcribe_time
        print(f"✓ Transcribed in {transcribe_time:.2f}s")
        print(f"✓ Speed: {speed_factor:.2f}x real-time")
        print(f"✓ Text length: {len(result['text'])} chars")
        print(f"✓ Word count: {len(result['text'].split())} words")
        
        if 'language' in result:
            print(f"✓ Language: {result['language']}")
        
        return {
            'model': model_size,
            'engine': engine,
            'load_time': load_time,
            'transcribe_time': transcribe_time,
            'speed_factor': speed_factor,
            'text': result['text'],
            'success': True
        }
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return {
            'model': model_size,
            'engine': engine,
            'success': False,
            'error': str(e)
        }


def compare_models(audio_file: str):
    """Compare multiple model sizes"""
    print("\n🎤 Locivox Model Comparison")
    print("=" * 60)
    
    models = ['tiny', 'base', 'small']
    results = []
    
    for model in models:
        result = benchmark_model(model, audio_file)
        results.append(result)
        time.sleep(1)  # Brief pause between models
    
    # Summary
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    
    successful = [r for r in results if r['success']]
    
    if not successful:
        print("❌ No models completed successfully")
        return
    
    print(f"\n{'Model':<10} {'Load Time':<12} {'Trans Time':<12} {'Speed':<10}")
    print("-" * 60)
    
    for r in successful:
        print(f"{r['model']:<10} {r['load_time']:>8.2f}s    "
              f"{r['transcribe_time']:>8.2f}s    {r['speed_factor']:>6.2f}x")
    
    # Find fastest
    fastest = min(successful, key=lambda x: x['transcribe_time'])
    print(f"\n🏆 Fastest: {fastest['model']} ({fastest['speed_factor']:.2f}x real-time)")
    
    # Check if transcriptions match
    texts = [r['text'] for r in successful]
    if len(set(texts)) == 1:
        print("✓ All models produced identical transcriptions")
    else:
        print("⚠ Models produced different transcriptions")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Compare different Whisper models'
    )
    parser.add_argument(
        'audio_file',
        help='Audio file to transcribe'
    )
    parser.add_argument(
        '--model',
        help='Specific model to test (default: compare all)'
    )
    parser.add_argument(
        '--engine',
        default='faster-whisper',
        choices=['faster-whisper', 'openai-whisper'],
        help='STT engine to use'
    )
    
    args = parser.parse_args()
    
    if args.model:
        # Test single model
        result = benchmark_model(args.model, args.audio_file, args.engine)
        
        if result['success']:
            print("\n" + "=" * 60)
            print("TRANSCRIPTION:")
            print("=" * 60)
            print(result['text'])
    else:
        # Compare models
        compare_models(args.audio_file)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted")
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
