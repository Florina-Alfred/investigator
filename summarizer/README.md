# YouTube Audio Transcriber & Summarizer

Easily turn any YouTube video into a transcript and a quick summary! This tool downloads audio from YouTube, transcribes it with Whisper, and summarizes the result using Ollama models.

```
[YouTube Video] --> [Download Audio with yt-dlp] --> [Transcribe with Whisper] --> [Summarize with Ollama] --> [Markdown Output]
```

## How to Use
```sh
python main.py --url "<youtube_url>" --quality 192 --model gemma3 --device cuda
```

- `--url`: The YouTube video you want to process
- `--quality`: Audio quality (default: 192)
- `--model`: Ollama model for summary (default: gemma3)
- `--device`: Use `cuda` for GPU or `cpu` for CPU (auto-detects by default)

## Requirements
- Python 3.8+
- `yt-dlp`, `openai-whisper`, `ollama`, `torch`
- (Optional) NVIDIA GPU for faster transcription

## License
MIT License
