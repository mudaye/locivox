Usage Guide
===========

Basic Usage
-----------

Interactive Recording
^^^^^^^^^^^^^^^^^^^^^

The simplest way to use Locivox:

.. code-block:: bash

   locivox

This starts an interactive session where you can:

1. Select your microphone device
2. Press ENTER to start recording
3. Speak into your microphone
4. Press ENTER to stop recording
5. View transcription in console
6. Find output file in ``output/`` directory

Transcribe Audio Files
^^^^^^^^^^^^^^^^^^^^^^

Transcribe existing audio files:

.. code-block:: bash

   # Single file
   locivox --file audio.wav

   # Different formats supported
   locivox --file recording.mp3
   locivox --file podcast.flac
   locivox --file interview.m4a

Command Line Options
--------------------

Model Selection
^^^^^^^^^^^^^^^

Choose different Whisper model sizes:

.. code-block:: bash

   # Tiny model (fastest, lowest quality)
   locivox --model tiny

   # Base model (good balance, default)
   locivox --model base

   # Small model (better quality)
   locivox --model small

   # Medium model (great quality, slower)
   locivox --model medium

   # Large model (best quality, slowest)
   locivox --model large

Model Performance Guide:

* **tiny**: ~10x faster than real-time on CPU
* **base**: ~5x faster than real-time (recommended)
* **small**: ~3x faster than real-time
* **medium**: ~1x real-time
* **large**: ~0.5x real-time (may struggle on CPU)

Language Options
^^^^^^^^^^^^^^^^

Specify the language or enable auto-detection:

.. code-block:: bash

   # English (default)
   locivox --language en

   # Spanish
   locivox --language es

   # French
   locivox --language fr

   # Auto-detect language
   locivox --language auto

Output Formats
^^^^^^^^^^^^^^

Choose output format:

.. code-block:: bash

   # Plain text (default)
   locivox --output-format txt

   # JSON with segments and timestamps
   locivox --output-format json

   # SRT subtitle format
   locivox --output-format srt

Custom Configuration
^^^^^^^^^^^^^^^^^^^^

Use a custom config file:

.. code-block:: bash

   locivox --config my_config.yaml

Combining Options
^^^^^^^^^^^^^^^^^

All options can be combined:

.. code-block:: bash

   locivox --file interview.mp3 \
           --model small \
           --language es \
           --output-format srt \
           --config custom.yaml

Configuration File
------------------

Edit ``config.yaml`` to customize default behavior:

.. code-block:: yaml

   model:
     engine: "faster-whisper"
     size: "base"
     device: "cpu"
     language: "en"

   audio:
     sample_rate: 16000
     channels: 1
     chunk_duration: 5

   output:
     directory: "./output"
     format: "txt"
     timestamp: true

See :doc:`configuration` for full details.

Examples
--------

Transcribe Meeting Recording
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   locivox --file meeting.mp4 \
           --model small \
           --output-format srt

This creates timestamped subtitles you can add to the video.

Transcribe Podcast Episode
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   locivox --file podcast_ep42.mp3 \
           --model medium \
           --output-format json

JSON output includes segments with timestamps for easy parsing.

Quick Voice Note
^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Just run and speak
   locivox

   # Output automatically saved with timestamp
   # e.g., output/transcript_20260213_143022.txt

Multi-language Interview
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   locivox --file interview.wav \
           --language auto \
           --output-format json

Auto-detects the spoken language.

Tips & Tricks
-------------

Better Audio Quality
^^^^^^^^^^^^^^^^^^^^

* Speak clearly and at a moderate pace
* Reduce background noise
* Use a good quality microphone
* Position microphone 6-12 inches from mouth

Faster Transcription
^^^^^^^^^^^^^^^^^^^^

* Use ``faster-whisper`` engine (default)
* Choose smaller model (``tiny`` or ``base``)
* Use CPU-optimized builds
* Reduce ``chunk_duration`` in config

Handling Long Audio
^^^^^^^^^^^^^^^^^^^

For recordings longer than 1 hour:

1. Increase ``max_duration`` in config
2. Use ``base`` or ``small`` model
3. Consider splitting file into chunks

Working with Multiple Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Batch process with a shell script:

.. code-block:: bash

   #!/bin/bash
   for file in *.mp3; do
       locivox --file "$file" --model base
   done

Output Files
------------

Default Location
^^^^^^^^^^^^^^^^

Transcripts are saved to ``./output/`` by default.

Filename Format
^^^^^^^^^^^^^^^

With timestamp (default):

.. code-block:: text

   transcript_20260213_143022.txt

Without timestamp:

.. code-block:: text

   transcript.txt

File Contents
^^^^^^^^^^^^^

**TXT format:**

.. code-block:: text

   This is the transcribed text from your audio recording.

**JSON format:**

.. code-block:: json

   {
     "text": "Full transcription...",
     "segments": [
       {
         "start": 0.0,
         "end": 2.5,
         "text": "First segment"
       }
     ],
     "language": "en"
   }

**SRT format:**

.. code-block:: text

   1
   00:00:00,000 --> 00:00:02,500
   First segment

   2
   00:00:02,500 --> 00:00:05,000
   Second segment

Next Steps
----------

* See :doc:`configuration` for advanced settings
* Check :doc:`troubleshooting` for common issues
* Read :doc:`api/modules` for programmatic usage
