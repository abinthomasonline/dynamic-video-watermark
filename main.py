import argparse
import importlib
import json
import os
from tqdm import tqdm
import cv2
import ffmpeg


def main(video_path, output_path, watermark_path, animation_class, animation_config):
    """Add watermark to the video and save the result to the output path."""
    input_video = cv2.VideoCapture(video_path)
    video_width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = input_video.get(cv2.CAP_PROP_FPS)
    output_path_no_audio = output_path.split(".")[0] + "_no_audio.mp4"
    output_video = cv2.VideoWriter(output_path_no_audio, cv2.VideoWriter_fourcc(*'mp4v'), fps, (video_width, video_height))
    
    # Animation Script
    with open(animation_config, "r") as f:
        animation_config = json.load(f)[animation_class]
    animation_class = getattr(importlib.import_module("anim"), animation_class)
    animation = animation_class(watermark_path, fps, video_width, video_height)
    animation.prepare(**animation_config)
    
    # Create the watermarked video (without audio)
    progress_bar = tqdm(total=input_video.get(int(cv2.CAP_PROP_FRAME_COUNT)), desc=f'Watermarking {video_path}')
    frame_count = 0
    while True:
        ret, frame = input_video.read()
        if not ret:
            break
        frame_count += 1
        updated_frame = animation.stamp(frame=frame, frame_count=frame_count)
        output_video.write(updated_frame)
        progress_bar.update(1)

    input_video.release()
    output_video.release()

    # Add the audio to the output video
    input_video = ffmpeg.probe(video_path, select_streams="a")
    if not input_video["streams"]:
        os.rename(output_path_no_audio, output_path)
        return
    input_video = ffmpeg.input(video_path)
    output_video = ffmpeg.input(output_path_no_audio)
    (
        ffmpeg
        .concat(output_video, input_video, v=1, a=1)
        .output(output_path)
        .global_args('-loglevel', 'quiet', '-stats')
        .run(overwrite_output=True)
    )
    os.remove(output_path_no_audio)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple argument parser")
    parser.add_argument("--video-path", type=str, default="assets/input.mp4", help="Path to the input video file")
    parser.add_argument("--output-path", type=str, default="assets/output.mp4", help="Path to the output video file")
    parser.add_argument("--watermark-path", type=str, default="assets/watermark.png", help="Path to the watermark image file")
    parser.add_argument("--animation-class", type=str, default="HorizontalSlide", help="The animation class to use")
    parser.add_argument("--animation-config", type=str, default="anim_configs.json", help="The configuration for the animation class")
    args = parser.parse_args()
    main(args.video_path, args.output_path, args.watermark_path, args.animation_class, args.animation_config)
