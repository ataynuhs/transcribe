import time
import os
import subprocess
import argparse
from faster_whisper import WhisperModel

# A list of standard media formats the script will look for when scanning folders
SUPPORTED_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.wav', '.mp3', '.m4a', '.flac'}

def get_files_to_process(input_paths):
    """Scans the provided paths and builds a flat list of all valid media files."""
    files = []
    for path in input_paths:
        # If it's a specific file, add it directly
        if os.path.isfile(path):
            files.append(path)
        # If it's a folder, scan inside it for supported media files
        elif os.path.isdir(path):
            print(f"📁 Scanning folder: '{path}'")
            for filename in os.listdir(path):
                ext = os.path.splitext(filename)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    files.append(os.path.join(path, filename))
        else:
            print(f"⚠️ Warning: '{path}' is not a valid file or directory. Skipping.")
    
    return files

def process_media_to_text(media_path, model, verbose=False):
    """Extracts audio and transcribes it using an ALREADY loaded Whisper model."""
    
    # Generate the new output names
    base_path = os.path.splitext(media_path)[0]
    temp_wav_path = f"{base_path}_temp_audio.wav"
    output_txt_path = f"{base_path}_transcript.txt" # Updated naming convention!

    print(f"\n==================================================")
    print(f"▶️ Processing: '{os.path.basename(media_path)}'")
    print(f"==================================================")

    # ==========================================
    # STEP 1: AUDIO EXTRACTION (FFmpeg)
    # ==========================================
    print("⏳ Extracting optimal audio track via FFmpeg...")
    ffmpeg_command = [
        "ffmpeg", "-y", "-i", media_path, "-vn",
        "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", temp_wav_path
    ]

    stdout_dest = None if verbose else subprocess.DEVNULL
    stderr_dest = None if verbose else subprocess.DEVNULL

    try:
        subprocess.run(ffmpeg_command, stdout=stdout_dest, stderr=stderr_dest, check=True)
    except subprocess.CalledProcessError:
        print(f"❌ Error: FFmpeg failed to process '{media_path}'. Skipping to next file.")
        return

    # ==========================================
    # STEP 2: TRANSCRIPTION (Whisper)
    # ==========================================
    print("🎙️ Transcribing on RTX 5070 Ti...")
    start_time = time.time()
    
    segments, info = model.transcribe(temp_wav_path, beam_size=5)
    
    if verbose:
        print(f"✨ Detected language: '{info.language}'")
        print("--- Transcription Start ---")
    
    with open(output_txt_path, "w", encoding="utf-8") as txt_file:
        for segment in segments:
            line = f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n"
            if verbose:
                print(line, end="")
            txt_file.write(line)
            
    execution_time = time.time() - start_time
    if verbose:
        print("\n--- Transcription End ---")

    # ==========================================
    # STEP 3: CLEANUP
    # ==========================================
    if os.path.exists(temp_wav_path):
        os.remove(temp_wav_path)

    print(f"✅ Finished in {execution_time:.2f} seconds.")
    print(f"💾 Saved to: {output_txt_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch transcribe video/audio files in folders using Whisper.")
    
    # We use nargs='+' to tell Python it can accept 1, 2, or 100 paths here!
    parser.add_argument("input_paths", nargs="+", type=str, help="File path(s) OR folder path(s) to process.")
    parser.add_argument("--verbose", action="store_true", help="Show line-by-line transcription.")
    parser.add_argument("--model", type=str, default="base", help="Whisper model size (base, small, medium, large-v3)")

    args = parser.parse_args()

    # 1. Gather all files first
    files_to_process = get_files_to_process(args.input_paths)
    
    if not files_to_process:
        print("❌ No compatible media files found. Exiting.")
        exit()

    print(f"📋 Found {len(files_to_process)} file(s) to transcribe.")

    # 2. Load the AI Model ONCE
    print(f"\n🧠 Loading Whisper '{args.model}' model onto RTX 5070 Ti...")
    print("   (This only happens once for the whole batch)")
    shared_model = WhisperModel(args.model, device="cuda", compute_type="float16")

    # 3. Loop through every file and transcribe
    total_start_time = time.time()
    for media_file in files_to_process:
        process_media_to_text(media_file, shared_model, verbose=args.verbose)

    # Final summary
    total_time = time.time() - total_start_time
    print(f"\n🎉 BATCH COMPLETE! Processed {len(files_to_process)} file(s) in {total_time:.2f} seconds.")