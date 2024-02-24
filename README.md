# Dynamic Video Watermark

This is a simple python script to add a watermark to a video. The watermark animation can be customized by `Animation` subclass. The animation configuration can be passed as a json file.

The code contains one example of `Animation` subclass, `HorizontalSlide`. The animation configuration for `HorizontalSlide` is in `anim_configs.json`.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py --video-path="assets/input.mp4" --output-path="assets/output.mp4" --watermark-path="assets/watermark.png" --animation-class="HorizontalSlide" --animation-config="anim_configs.json"
```
