"""
Batch processing CLI for Locivox
Usage: python -m src.cli_batch [directory or files]
"""

import sys
import argparse
from src.batch import BatchProcessor


def main():
    """Main entry point for batch processing"""
    parser = argparse.ArgumentParser(
        description='Locivox Batch Processing - Transcribe multiple audio files'
    )
    parser.add_argument(
        'input',
        nargs='+',
        help='Input directory or audio files'
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
        '--recursive',
        '-r',
        action='store_true',
        help='Process subdirectories recursively'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing transcriptions'
    )
    parser.add_argument(
        '--extensions',
        nargs='+',
        help='File extensions to process (e.g., .wav .mp3)'
    )
    parser.add_argument(
        '--report',
        help='Save processing report to file'
    )
    
    args = parser.parse_args()
    
    try:
        processor = BatchProcessor(args.config)
        
        # Override config with CLI arguments
        if args.model:
            processor.config['model']['size'] = args.model
        
        if args.device:
            processor.config['model']['device'] = args.device
        
        if args.format:
            processor.config['output']['format'] = args.format
        
        if args.vocab:
            processor.config['vocabulary']['file'] = args.vocab
            processor.config['vocabulary']['enabled'] = True
        
        if args.enable_vocab:
            processor.config['vocabulary']['enabled'] = True
        
        # Reload vocabulary with updated config
        from src.vocabulary import VocabularyManager
        processor.vocabulary = VocabularyManager(processor.config)
        
        # Determine if input is directory or files
        import os
        from pathlib import Path
        
        input_path = Path(args.input[0])
        
        if len(args.input) == 1 and input_path.is_dir():
            # Process directory
            stats = processor.process_directory(
                input_dir=str(input_path),
                output_dir=args.output,
                extensions=args.extensions,
                recursive=args.recursive,
                overwrite=args.overwrite
            )
        else:
            # Process specific files
            stats = processor.process_files(
                file_paths=args.input,
                output_dir=args.output,
                overwrite=args.overwrite
            )
        
        # Print summary
        processor.print_summary()
        
        # Save report if requested
        if args.report:
            processor.save_report(args.report)
            print(f"\n📊 Report saved to: {args.report}")
        
        # Exit with error code if any failed
        if stats['failed'] > 0:
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
