# YouTube Audio Guard 🌌

A simple tool to adjust your video/audio loudness to meet YouTube's -14 LUFS standard.

## Features
- **Loudness Analysis**: Check your Integrated LUFS and True Peak values.
- **Auto-Optimization**: Automatically adjust your audio to -14 LUFS while preventing clipping.
- **Two-Pass Processing**: Uses industry-standard `loudnorm` filter for professional results.
- **GUI Interface**: Easy-to-use window for quick adjustments.

## Prerequisites
- Python 3.x
- [FFmpeg](https://ffmpeg.org/) installed and added to your PATH.

## How to use (Developer)
1. Clone the repository.
2. Run `python main_gui.py`.

## Building .exe
Use PyInstaller to build a standalone executable:
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "YouTubeAudioGuard" main_gui.py
```
