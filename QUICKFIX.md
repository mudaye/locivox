# 🚑 Quick Fix: pkg_resources Error

## Immediate Solution

Your virtual environment is created, but missing `setuptools`. Here's the fix:

### Step 1: Activate Your Virtual Environment

```cmd
cd locivox
venv\Scripts\activate
```

You should see `(venv)` appear in your prompt.

### Step 2: Install setuptools

```cmd
pip install --upgrade pip setuptools wheel
```

### Step 3: Install Requirements

```cmd
pip install -r requirements.txt
```

This will take 2-3 minutes to download and install all dependencies.

### Step 4: Test It

```cmd
python src/cli.py
```

---

## What Happened?

Python 3.12+ no longer includes `setuptools` by default. The updated `setup.bat` now handles this automatically, but you can also fix it manually as shown above.

---

## Verify Setup

Run this to check everything is working:

```cmd
python -c "import whisper; import sounddevice; print('✓ All dependencies installed!')"
```

If you see `✓ All dependencies installed!`, you're good to go! 🎉

---

## Still Having Issues?

Check `TROUBLESHOOTING.md` for more solutions.
