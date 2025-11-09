import whisper
import os
import json
import time
from pathlib import Path
from tqdm import tqdm  # Make sure tqdm is installed: pip install tqdm

def transcribe_videos():
    """Transcribe all videos using Whisper (CPU optimized with progress bar and timing)"""

    print("🔄 Loading Whisper model (base)...")
    model = whisper.load_model("small", device="cpu")  # Use "small" or "medium" for better accuracy

    video_files = list(Path("videos").glob("*.wav"))
    total_files = len(video_files)
    all_transcripts = []

    if total_files == 0:
        print("⚠️ No .wav files found in 'videos/'")
        return []

    print(f"📁 Found {total_files} .wav files in 'videos/'")
    start_total = time.time()

    for idx, video_file in enumerate(tqdm(video_files, desc="📝 Transcribing", unit="file"), 1):
        print(f"\n🎙️ [{idx}/{total_files}] {video_file.name}")
        start_time = time.time()

        result = model.transcribe(
            str(video_file),
            task="transcribe",
            fp16=False  # Required for CPU
        )

        duration = time.time() - start_time
        print(f"⏱️ Done in {duration:.2f} seconds")

        transcript_data = {
            "file": video_file.name,
            "text": result["text"],
            "segments": result["segments"]
        }

        # Save individual transcript
        transcript_file = f"transcripts/{video_file.stem}.json"
        os.makedirs("transcripts", exist_ok=True)
        with open(transcript_file, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)

        all_transcripts.append(transcript_data)
        print(f"💾 Saved: {transcript_file}")

    # Save combined transcript
    with open("transcripts/combined.json", 'w', encoding='utf-8') as f:
        json.dump(all_transcripts, f, ensure_ascii=False, indent=2)

    total_duration = time.time() - start_total
    print(f"\n✅ All transcriptions completed in {total_duration:.2f} seconds")
    return all_transcripts

if __name__ == "__main__":
    transcribe_videos()