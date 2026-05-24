🎙️ Local Whisper AI Transcription Setup Guide
===========================================================

This guide details how to configure a Windows PC to run a fully offline,
accelerated transcription pipeline using the faster-whisper engine, referencing
your pre-existing transcribe_audio.py script.


1. System Hardware Identification
---------------------------------

Before installing any AI libraries, verify your system's hardware to ensure
you download the correct compute packages. Open a PowerShell window and run
these commands:

Check CPU:
```powershell
(Get-CimInstance Win32_Processor).Name
```
*(Note: If you are using the older Command Prompt, you can use `wmic cpu get name`)*

Check GPU (NVIDIA):
```bash
nvidia-smi
```

*(If this command fails, you either do not have an NVIDIA GPU, or you need to
install the latest NVIDIA drivers).*


2. Base Installation & Prerequisites
------------------------------------

### Step A: Python

If you have Python installed:
- Ensure it is at least version 3.10+.
- Python 3.13 via the Microsoft Store is highly recommended for Windows.

If you do not have Python:
- Open the Microsoft Store app, search for "Python 3.13", and click Install.


### Step B: FFmpeg (Audio Extraction)

FFmpeg is required to slice and format audio before passing it to the AI.

Run this command in an Administrator PowerShell to install it silently:

```powershell
winget install Gyan.FFmpeg --silent
```

Close and reopen your terminal to refresh the system path.


### Step C: AI Model Cache Location

When the script runs for the first time, it will automatically download the
requested AI models from Hugging Face. They are permanently cached in a
hidden folder on your user drive:

```
C:\Users\<YourUsername>\.cache\huggingface\hub\
```


3. Hardware Configuration (GPU vs. CPU)
----------------------------------------

The faster-whisper engine is incredibly flexible and will run on both
dedicated GPUs and standard CPUs. You just need to install the correct
memory routing libraries.

#### For NVIDIA RTX GPUs (e.g., RTX 5070 Ti)

If `nvidia-smi` successfully displayed your GPU, install the CUDA-enabled
version of PyTorch so the workload routes to your VRAM.

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

**Script Note:** Ensure your model initialization uses `device="cuda"` and
`compute_type="float16"`.

#### For Systems Without a GPU (CPU-Only)

faster-whisper works wonderfully on standard processors using a highly
optimized engine called CTranslate2. Install the standard CPU tensor libraries:

```bash
pip install torch torchvision torchaudio
```

**Script Note:** You must change your script's initialization parameters to
`device="cpu"` and `compute_type="int8"` to prevent memory errors.


4. Install the Whisper Engine
------------------------------

Once your hardware routing (PyTorch) is configured, install the core
transcription library:

```bash
pip install faster-whisper
```


5. Global Batch Shortcut Setup
------------------------------

To run your script from anywhere without typing long file paths, set up a
global batch wrapper.

#### Locate Your Python Script

Ensure your pre-existing `transcribe_audio.py` file is saved in a permanent
directory (e.g., `C:\Scripts\transcribe_audio.py`).

#### Create the Batch File

In that exact same folder, create a new text file named `transcribe.bat`.

#### Link the Files

Open `transcribe.bat` in Notepad, paste the following line, and save it:

```dos
@python "C:\Scripts\transcribe_audio.py" %*
```

#### Update System Path

1. Press the Windows Key, type `env`, and select "Edit the system environment variables".
2. Click "Environment Variables".
3. Select `Path` under User variables, and click "Edit".
4. Click "New", type `C:\Scripts`, and click "OK".
5. Restart your terminal.


6. Usage Examples
-----------------

You can now open a terminal in any folder on your computer and execute the
pipeline using the `transcribe` command.

#### Process a Single File (Default Settings)

```bash
transcribe "D:\Videos\HowToDoRocketScienceWithoutRocket.mkv"
```

#### Process an Entire Folder of Videos

```bash
transcribe "D:\Coursework\DIY_Gazebo"
```

#### Use a Larger Model for Higher Accuracy

```bash
transcribe "D:\Videos\ASwimTable.mkv" --model medium
```

*(Options include: base, small, medium, large-v3, large-v3-turbo)*

#### Show Real-Time Processing (Verbose Mode)

```bash
transcribe "D:\Videos\HowToDoRocketScienceWithoutRocket.mkv" --model medium --verbose
```

