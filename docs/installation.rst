Installation
============

Prerequisites
-------------

* Python 3.9 or higher
* FFmpeg (required for audio processing)

Installing FFmpeg
^^^^^^^^^^^^^^^^^

**macOS:**

.. code-block:: bash

   brew install ffmpeg

**Ubuntu/Debian:**

.. code-block:: bash

   sudo apt update
   sudo apt install ffmpeg

**Windows:**

.. code-block:: bash

   # Using Chocolatey
   choco install ffmpeg

   # Using Scoop
   scoop install ffmpeg

Installation Methods
--------------------

From PyPI (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pip install locivox

From Source
^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/mudaye/locivox.git
   cd locivox
   pip install -e .

Development Installation
^^^^^^^^^^^^^^^^^^^^^^^^

For contributing to Locivox:

.. code-block:: bash

   git clone https://github.com/mudaye/locivox.git
   cd locivox
   pip install -e ".[dev]"

This installs additional development tools like pytest, black, and mypy.

Verify Installation
-------------------

Check that Locivox is installed correctly:

.. code-block:: bash

   locivox --help

You should see the help message with available options.

Optional Dependencies
---------------------

GUI Support
^^^^^^^^^^^

For the desktop GUI (Phase 4+):

.. code-block:: bash

   pip install locivox[gui]

Advanced Features
^^^^^^^^^^^^^^^^^

For speaker diarization and VAD:

.. code-block:: bash

   pip install locivox[advanced]

All Optional Features
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pip install locivox[gui,advanced]

Troubleshooting
---------------

FFmpeg Not Found
^^^^^^^^^^^^^^^^

If you get "FFmpeg not found" errors:

1. Verify FFmpeg is installed: ``ffmpeg -version``
2. Ensure FFmpeg is in your PATH
3. Restart your terminal after installation

Permission Errors
^^^^^^^^^^^^^^^^^

If you encounter permission errors on Linux/macOS:

.. code-block:: bash

   pip install --user locivox

Import Errors
^^^^^^^^^^^^^

If you get import errors, ensure your virtual environment is activated:

.. code-block:: bash

   # Create venv
   python -m venv venv

   # Activate (macOS/Linux)
   source venv/bin/activate

   # Activate (Windows)
   venv\Scripts\activate

   # Install
   pip install locivox
