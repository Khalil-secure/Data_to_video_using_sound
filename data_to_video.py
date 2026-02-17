#!/usr/bin/env python3
"""
Data to Video Converter
Converts any file into a series of RGB pixels and generates video frames.
Each pixel stores 3 bytes of data (R, G, B channels).
"""

import os
import math
import numpy as np
from PIL import Image
import argparse
from pathlib import Path


class DataToVideoConverter:
    def __init__(self, width=1920, height=1080):
        """
        Initialize converter with frame dimensions.
        
        Args:
            width: Frame width in pixels (default: 1920)
            height: Frame height in pixels (default: 1080)
        """
        self.width = width
        self.height = height
        self.bytes_per_frame = width * height * 3  # 3 bytes per pixel (RGB)
        
    def file_to_frames(self, input_file, output_dir):
        """
        Convert a file to video frames where each pixel represents 3 bytes of data.
        
        Args:
            input_file: Path to input file
            output_dir: Directory to save frames
        """
        # Read file data
        with open(input_file, 'rb') as f:
            data = f.read()
        
        file_size = len(data)
        print(f"File size: {file_size:,} bytes")
        
        # Calculate number of frames needed
        num_frames = math.ceil(file_size / self.bytes_per_frame)
        print(f"Bytes per frame: {self.bytes_per_frame:,}")
        print(f"Number of frames needed: {num_frames}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Store metadata
        metadata = {
            'original_filename': os.path.basename(input_file),
            'original_size': file_size,
            'width': self.width,
            'height': self.height,
            'num_frames': num_frames
        }
        
        # Save metadata
        metadata_file = os.path.join(output_dir, 'metadata.txt')
        with open(metadata_file, 'w') as f:
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")
        
        print(f"\nGenerating frames...")
        
        # Generate frames
        for frame_idx in range(num_frames):
            # Calculate data slice for this frame
            start_idx = frame_idx * self.bytes_per_frame
            end_idx = min(start_idx + self.bytes_per_frame, file_size)
            frame_data = data[start_idx:end_idx]
            
            # Pad last frame if necessary
            if len(frame_data) < self.bytes_per_frame:
                # Pad with zeros
                frame_data = frame_data + b'\x00' * (self.bytes_per_frame - len(frame_data))
            
            # Convert bytes to RGB array
            # Each 3 consecutive bytes become one RGB pixel
            pixels = np.frombuffer(frame_data, dtype=np.uint8)
            
            # Reshape to (height, width, 3) for RGB image
            frame_array = pixels.reshape((self.height, self.width, 3))
            
            # Create image
            img = Image.fromarray(frame_array, mode='RGB')
            
            # Save frame
            frame_filename = os.path.join(output_dir, f'frame_{frame_idx:06d}.png')
            img.save(frame_filename)
            
            if (frame_idx + 1) % 10 == 0 or frame_idx == num_frames - 1:
                print(f"  Generated frame {frame_idx + 1}/{num_frames}")
        
        print(f"\n✓ Frames saved to: {output_dir}")
        return num_frames
    
    def frames_to_file(self, frames_dir, output_file):
        """
        Reconstruct original file from video frames.
        
        Args:
            frames_dir: Directory containing frames
            output_file: Path to save reconstructed file
        """
        # Read metadata
        metadata_file = os.path.join(frames_dir, 'metadata.txt')
        metadata = {}
        
        with open(metadata_file, 'r') as f:
            for line in f:
                key, value = line.strip().split(': ', 1)
                metadata[key] = value
        
        original_size = int(metadata['original_size'])
        num_frames = int(metadata['num_frames'])
        
        print(f"Reconstructing file...")
        print(f"Original size: {original_size:,} bytes")
        print(f"Number of frames: {num_frames}")
        
        # Collect all data
        all_data = bytearray()
        
        for frame_idx in range(num_frames):
            frame_filename = os.path.join(frames_dir, f'frame_{frame_idx:06d}.png')
            
            # Load image
            img = Image.open(frame_filename)
            frame_array = np.array(img)
            
            # Flatten to bytes
            frame_bytes = frame_array.tobytes()
            all_data.extend(frame_bytes)
            
            if (frame_idx + 1) % 10 == 0 or frame_idx == num_frames - 1:
                print(f"  Processed frame {frame_idx + 1}/{num_frames}")
        
        # Trim to original size (remove padding)
        all_data = all_data[:original_size]
        
        # Write to file
        with open(output_file, 'wb') as f:
            f.write(all_data)
        
        print(f"\n✓ File reconstructed: {output_file}")
        print(f"  Size: {len(all_data):,} bytes")
    
    def create_video(self, frames_dir, output_video, fps=30):
        """
        Create video from frames using ffmpeg (if available).
        
        Args:
            frames_dir: Directory containing frames
            output_video: Output video filename
            fps: Frames per second
        """
        try:
            import subprocess
            
            # Check if ffmpeg is available
            result = subprocess.run(['ffmpeg', '-version'], 
                                   capture_output=True, 
                                   text=True)
            
            if result.returncode != 0:
                print("ffmpeg not found. Install it to create video files.")
                return False
            
            # Create video from frames
            input_pattern = os.path.join(frames_dir, 'frame_%06d.png')
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output file
                '-framerate', str(fps),
                '-i', input_pattern,
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-crf', '0',  # Lossless
                output_video
            ]
            
            print(f"\nCreating video with ffmpeg...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Video created: {output_video}")
                return True
            else:
                print(f"Error creating video: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Convert any file to/from video frames using RGB pixel encoding'
    )
    parser.add_argument('mode', choices=['encode', 'decode'], 
                       help='encode: file to frames, decode: frames to file')
    parser.add_argument('input', help='Input file or frames directory')
    parser.add_argument('output', help='Output directory (encode) or file (decode)')
    parser.add_argument('--width', type=int, default=1920, 
                       help='Frame width (default: 1920)')
    parser.add_argument('--height', type=int, default=1080, 
                       help='Frame height (default: 1080)')
    parser.add_argument('--fps', type=int, default=30, 
                       help='Frames per second for video (default: 30)')
    parser.add_argument('--video', help='Create video file (requires ffmpeg)')
    
    args = parser.parse_args()
    
    converter = DataToVideoConverter(width=args.width, height=args.height)
    
    if args.mode == 'encode':
        # Convert file to frames
        if not os.path.isfile(args.input):
            print(f"Error: Input file not found: {args.input}")
            return
        
        num_frames = converter.file_to_frames(args.input, args.output)
        
        # Optionally create video
        if args.video:
            converter.create_video(args.output, args.video, fps=args.fps)
            
    elif args.mode == 'decode':
        # Convert frames back to file
        if not os.path.isdir(args.input):
            print(f"Error: Frames directory not found: {args.input}")
            return
        
        converter.frames_to_file(args.input, args.output)


if __name__ == '__main__':
    main()
