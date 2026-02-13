# Locivox Documentation

This directory contains the Sphinx documentation for Locivox.

## Building the Documentation

### Install Dependencies

```bash
pip install -r requirements-dev.txt
```

This installs Sphinx and related tools.

### Build HTML Documentation

```bash
cd docs
make html
```

The built documentation will be in `_build/html/`. Open `_build/html/index.html` in your browser.

### Live Preview

For live reloading while editing:

```bash
pip install sphinx-autobuild
make livehtml
```

Then open http://127.0.0.1:8000 in your browser.

### Clean Build

Remove built files:

```bash
make clean
```

## Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration
├── index.rst            # Main documentation page
├── installation.rst     # Installation guide
├── usage.rst            # Usage guide
├── configuration.rst    # Configuration reference (to be added)
├── troubleshooting.rst  # Troubleshooting guide (to be added)
├── api/                 # API reference (auto-generated)
├── Makefile             # Build commands
└── README.md            # This file
```

## Writing Documentation

### reStructuredText Basics

Sphinx uses reStructuredText (.rst) format:

```rst
Section Heading
===============

Subsection
----------

**Bold text**
*Italic text*
``Code text``

.. code-block:: python

   def example():
       return "Hello"

- Bullet point
- Another point
```

### Adding New Pages

1. Create a new `.rst` file in `docs/`
2. Add it to the `toctree` in `index.rst`:

```rst
.. toctree::
   :maxdepth: 2

   installation
   usage
   your_new_page
```

### API Documentation

API docs are auto-generated from docstrings:

```python
def transcribe(audio_data: np.ndarray) -> dict:
    """Transcribe audio data to text.
    
    Args:
        audio_data: NumPy array of audio samples
        
    Returns:
        Dictionary with transcription results
    """
```

## Publishing Documentation

### GitHub Pages

1. Build docs: `make html`
2. Push `_build/html/` to `gh-pages` branch
3. Enable GitHub Pages in repository settings

### ReadTheDocs

1. Connect repository to ReadTheDocs
2. Configuration is in `conf.py`
3. Docs build automatically on push

## Contributing

See the main [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.
