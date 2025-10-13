import yt_dlp
import re
import time
import torch
import os
import ollama
import whisper
import argparse


def load_prompt(path):
    """Load and return the prompt template from the given path."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading prompt from {path}: {e}")
        return ""


def get_final_filename(info):
    if not isinstance(info, dict):
        return None
    if "requested_downloads" in info and info["requested_downloads"]:
        return info["requested_downloads"][0].get("filepath")
    if "_filename" in info:
        return info["_filename"]
    title = info.get("title", "audio")
    for ext in (".mp3", ".webm", ".m4a"):
        candidate = f"{title}{ext}"
        if os.path.exists(candidate):
            return candidate
    return f"{title}.mp3"


def replace_symbols_with_underscore(name: str):
    return re.sub(r"[^a-zA-Z0-9]", "_", name)


def download_audio(url, quality):
    def progress_hook(d):
        if d.get("status") == "downloading":
            percent = d.get("_percent_str", "").strip()
            print(f"\rDownloading: {percent}", end="", flush=True)
        elif d.get("status") == "finished":
            print("\rDownload complete.           ")

    yt_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }
        ],
        "nocheckcertificate": True,
        "outtmpl": "%(title)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [progress_hook],
        "logger": None,
    }
    with yt_dlp.YoutubeDL(yt_opts) as ydl:
        try:
            info = ydl.extract_info(url)
        except Exception as e:
            print(f"Error extracting info: {e}")
            return None, None
    return info, get_final_filename(info)


def transcribe_audio(audio_path, model_name="base", device=None):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(model_name, device=device)
    result = model.transcribe(audio_path)
    text = result["text"]
    return str(text) if not isinstance(text, str) else text


def write_transcription(txt_filename, video_info, url, text):
    if not isinstance(video_info, dict):
        video_info = {}
    info_labels = [
        ("Title", video_info.get("title", "")),
        ("Uploader", video_info.get("uploader", "")),
        ("Duration", video_info.get("duration_string", video_info.get("duration", ""))),
        ("URL", url),
    ]
    max_label_len = max(len(label) for label, _ in info_labels)
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write("# Video Information\n\n")
        for label, value in info_labels:
            f.write(f"**{label.ljust(max_label_len)}** : {value}  \n")
        f.write("\n---\n\n")
        f.write("## Transcription\n\n")
        f.write(text)


def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube audio, transcribe it, and save the result with video info."
    )
    parser.add_argument(
        "-d",
        "--device",
        type=str,
        default=None,
        help="Device for Whisper transcription: 'cuda' for GPU, 'cpu' for CPU. Default: auto-detect.",
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        # default="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        required=True,
        help="YouTube video URL to download",
    )
    parser.add_argument(
        "-b",
        "--backup",
        action="store_true",
        help="Save a copy of the transcript for later use in the local disk.",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=str,
        default="192",
        help="Audio quality in kbps. Possible values: 320, 256, 192, 160, 128, 96, 64, 32 (default: 192)",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        # default="llama3.2",
        default="hf.co/unsloth/gpt-oss-20b-GGUF:latest",
        # default="hf.co/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF:latest",
        help="Ollama model to use for summarization (default: gpt-oss:20b)",
    )
    args = parser.parse_args()

    video_info, audio_path = download_audio(args.url, args.quality)
    if not audio_path or not os.path.exists(audio_path):
        print("Audio file not found. Exiting.")
        return
    # Ensure summary_saves directory exists
    save_dir = "summary_saves"
    os.makedirs(save_dir, exist_ok=True)

    md_filename = os.path.join(
        save_dir, os.path.splitext(os.path.basename(audio_path))[0] + ".md"
    )
    text = transcribe_audio(audio_path, model_name="base", device=args.device)
    if args.backup:
        write_transcription(md_filename, video_info, args.url, text)
    os.remove(audio_path)
    print(f"Transcription saved to {md_filename} and audio file deleted.")

    # Summarize using ollama
    print(f"Generating summary with Ollama - {args.model}...")
    start_time = time.perf_counter()
    prompt_template = load_prompt("prompts/video_summary.md")
    prompt = prompt_template.replace("{transcript}", text)

    message = {
        "role": "user",
        "content": prompt,
    }
    if args.model[:7] == "gpt-oss":
        levels = ["low", "medium", "high"]
        print(f".....using {levels[2]} for thinking")
        response = ollama.chat(model=args.model, messages=[message], think=levels[2])
    else:
        response = ollama.chat(model=args.model, messages=[message], think=False)
    summary_clean = response["message"]["content"]
    print("\n---\nSUMMARY (model: {}):\n".format(args.model))
    print(summary_clean)

    summary_filename = (
        os.path.splitext(md_filename)[0]
        + f"_summary_{replace_symbols_with_underscore(args.model)}.md"
    )
    summary_content = f"# Summary ({args.model})\n\n" + summary_clean
    print(f"\n\t\t--->Time taken for summary: {time.perf_counter() - start_time:.2f} seconds<---")
    # copy_content_to_clipboard(summary_content)
    if args.backup:
        print(f"\n\nSummary saved to {summary_filename}")
        with open(summary_filename, "w", encoding="utf-8") as f:
            f.write(summary_content)


if __name__ == "__main__":
    main()
