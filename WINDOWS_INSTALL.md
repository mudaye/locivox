# 🪟 Windows Installation Guide (No Compiler Needed)

## The Problem

Some packages try to build from source, requiring Visual Studio C++ compilers. This causes the `build_meta.py` error.

## ✅ Solution: Step-by-Step

### Step 1: Clean Start

```cmd
cd locivox

:: Deactivate if active
deactivate

:: Remove old venv
rmdir /s /q venv

:: Create fresh venv
python -m venv venv

:: Activate
venv\Scripts\activate
```

### Step 2: Install Core Tools

```cmd
python -m pip install --upgrade pip setuptools wheel
```

### Step 3: Install PyTorch (CPU) First

```cmd
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Step 4: Install Other Dependencies

```cmd
pip install faster-whisper openai-whisper sounddevice numpy soundfile pyyaml colorama tqdm
```

### Step 5: Verify Installation

```cmd
python -c "import whisper; import faster_whisper; import sounddevice; print('✓ Success!')"
```

---

## Alternative: Use requirements-windows.txt

If you downloaded the fixed requirements file:

```cmd
pip install -r requirements-windows.txt
```

---

## What Changed?

- ✅ Removed `scipy` (not essential, often requires compilation)
- ✅ Removed `python-dotenv` (not needed for Phase 1)
- ✅ Explicit PyTorch CPU index (ensures pre-built wheels)
- ✅ Updated numpy to 1.26.0 (better Windows wheel support)

---

## Still Seeing Build Errors?

### Option A: Skip Problematic Package

If a specific package fails:
```cmd
pip install --only-binary :all: package-name
```

### Option B: Install Without Dependencies

```cmd
pip install --no-deps package-name
```

### Option C: Use Conda Instead

```cmd
conda create -n locivox python=3.11
conda activate locivox
conda install pytorch torchaudio cpuonly -c pytorch
pip install faster-whisper openai-whisper sounddevice
```

---

## Test Your Setup

```cmd
python src/cli.py
```

You should see the device selection screen!
