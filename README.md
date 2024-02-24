# Dynamic Video Watermark

This is a simple python script to add a watermark to a video. The watermark animation can be customized by `Animation` subclass.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py --video-path="assets/input.mp4" --output-path="assets/output.mp4" --watermark-path="assets/watermark.png" --animation-class="HorizontalSlide" --animation-config="anim_configs.json"
```
