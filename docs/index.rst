Locivox Documentation
=====================

**Local Voice Transcription System** - Privacy-first, model-agnostic speech-to-text

Locivox is an open-source STT system designed to run entirely on your machine with no cloud dependencies. Start with Whisper, expand to any model.

.. image:: https://img.shields.io/pypi/v/locivox.svg
   :target: https://pypi.org/project/locivox/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/locivox.svg
   :target: https://pypi.org/project/locivox/
   :alt: Python versions

.. image:: https://img.shields.io/github/license/mudaye/locivox.svg
   :target: https://github.com/mudaye/locivox/blob/main/LICENSE
   :alt: License

Features
--------

* 🎤 **Real-time microphone capture** with configurable settings
* 🤖 **Multiple STT engines**: Faster-Whisper and OpenAI-Whisper
* 💻 **CPU-optimized** for laptops without GPU
* 🔧 **Model-agnostic architecture** - easily add new engines
* 📝 **Multiple output formats**: TXT, JSON, SRT subtitles
* 🌍 **Automatic language detection** or manual selection
* 🔒 **Privacy-first** - all processing happens locally
* ⚙️ **Self-contained** virtual environment - no global dependencies

Quick Start
-----------

Installation
^^^^^^^^^^^^

.. code-block:: bash

   pip install locivox

Or from source:

.. code-block:: bash

   git clone https://github.com/mudaye/locivox.git
   cd locivox
   pip install -e .

Basic Usage
^^^^^^^^^^^

.. code-block:: bash

   # Interactive recording
   locivox

   # Transcribe a file
   locivox --file audio.wav

   # Use different model
   locivox --model small

   # Specify language
   locivox --language es

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   usage
   configuration
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/modules
   api/audio_capture
   api/transcriber
   api/utils

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog
   roadmap

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
