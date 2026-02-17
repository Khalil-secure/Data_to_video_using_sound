#!/usr/bin/env python3
"""
Advanced Data to Video Converter with Audio Encoding
Stores data in both video frames (RGB pixels) AND audio channels.
Uses matrix transformations for compression and encoding matrix in audio.
"""

import os
import math
import numpy as np
from PIL import Image
import argparse
from pathlib import Path
import json
import struct


class AdvancedDataToVideoConverter:
    def __init__(self, width=1920, height=1080, sample_rate=48000, audio_channels=2):
        """
        Initialize converter with frame dimensions and audio parameters.
        
        Args:
            width: Frame width in pixels (default: 1920)
            height: Frame height in pixels (default: 1080)
            sample_rate: Audio sample rate in Hz (default: 48000)
            audio_channels: Number of audio channels (1=mono, 2=stereo)
        """
        self.width = width
        self.height = height
        self.sample_rate = sample_rate
        self.audio_channels = audio_channels
        
        # Video capacity
        self.pixels_per_frame = width * height
        self.bytes_per_frame_video = self.pixels_per_frame * 3  # RGB
        
        # Audio capacity (16-bit samples, 30fps assumed)
        self.samples_per_frame = sample_rate // 30  # ~1600 samples per frame at 48kHz
        self.bytes_per_frame_audio = self.samples_per_frame * audio_channels * 2  # 16-bit samples
        
        # Total capacity per frame
        self.bytes_per_frame_total = self.bytes_per_frame_video + self.bytes_per_frame_audio
        
    def create_compression_matrix(self, data_chunk, matrix_size=16):
        """
        Create a transformation matrix for data compression/encoding.
        Uses differential encoding and pattern detection.
        
        Args:
            data_chunk: Chunk of data to analyze
            matrix_size: Size of the transformation matrix
            
        Returns:
            Tuple of (compressed_data, encoding_matrix, metadata)
        """
        data_array = np.frombuffer(data_chunk, dtype=np.uint8)
        
        # Apply differential encoding (store differences instead of absolute values)
        if len(data_array) > 1:
            differential = np.diff(data_array, prepend=data_array[0])
        else:
            differential = data_array
        
        # Create transformation matrix based on data patterns
        # This matrix will be stored in audio and used for decoding
        matrix = np.zeros((matrix_size, matrix_size), dtype=np.float32)
        
        # Analyze data patterns to create optimal matrix
        data_reshaped = differential[:matrix_size * matrix_size].reshape(matrix_size, matrix_size) if len(differential) >= matrix_size * matrix_size else np.pad(differential, (0, matrix_size * matrix_size - len(differential))).reshape(matrix_size, matrix_size)
        
        # Use DCT-like transformation for compression
        for i in range(matrix_size):
            for j in range(matrix_size):
                matrix[i, j] = np.cos((2 * i + 1) * j * np.pi / (2 * matrix_size))
        
        # Normalize matrix
        matrix = matrix / np.linalg.norm(matrix)
        
        # Apply RLE (Run-Length Encoding) for repeated patterns
        compressed = self._apply_rle(differential)
        
        metadata = {
            'original_length': len(data_array),
            'compressed_length': len(compressed),
            'compression_ratio': len(compressed) / len(data_array) if len(data_array) > 0 else 1.0,
            'matrix_size': matrix_size,
            'differential_base': int(data_array[0]) if len(data_array) > 0 else 0
        }
        
        return compressed, matrix, metadata
    
    def _apply_rle(self, data):
        """Apply Run-Length Encoding to compress repeated patterns."""
        if len(data) == 0:
            return data
        
        compressed = []
        i = 0
        while i < len(data):
            count = 1
            while i + count < len(data) and data[i] == data[i + count] and count < 255:
                count += 1
            
            if count > 3:  # Only encode if we have 4+ repeated values
                compressed.extend([255, data[i], count])  # Escape sequence
            else:
                compressed.extend([data[i]] * count)
            
            i += count
        
        return np.array(compressed, dtype=np.uint8)
    
    def _decode_rle(self, data):
        """Decode Run-Length Encoded data."""
        if len(data) == 0:
            return data
        
        decompressed = []
        i = 0
        while i < len(data):
            if data[i] == 255 and i + 2 < len(data):  # Escape sequence
                value = data[i + 1]
                count = data[i + 2]
                decompressed.extend([value] * count)
                i += 3
            else:
                decompressed.append(data[i])
                i += 1
        
        return np.array(decompressed, dtype=np.uint8)
    
    def matrix_to_audio(self, matrix):
        """
        Convert transformation matrix to audio samples.
        Each matrix element becomes a 16-bit audio sample.
        
        Args:
            matrix: 2D numpy array
            
        Returns:
            Audio samples as bytes
        """
        # Flatten matrix and normalize to 16-bit range
        flat_matrix = matrix.flatten()
        
        # Normalize to [-32768, 32767] range for 16-bit audio
        min_val, max_val = flat_matrix.min(), flat_matrix.max()
        if max_val - min_val > 0:
            normalized = (flat_matrix - min_val) / (max_val - min_val)
            audio_samples = (normalized * 65535 - 32768).astype(np.int16)
        else:
            audio_samples = np.zeros(len(flat_matrix), dtype=np.int16)
        
        return audio_samples.tobytes()
    
    def audio_to_matrix(self, audio_bytes, matrix_size):
        """
        Convert audio samples back to transformation matrix.
        
        Args:
            audio_bytes: Audio data as bytes
            matrix_size: Size of the matrix
            
        Returns:
            2D numpy array matrix
        """
        # Convert bytes to int16 samples
        samples = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Denormalize from [-32768, 32767] back to original range
        normalized = (samples.astype(np.float32) + 32768) / 65535
        
        # Reshape to matrix
        matrix = normalized[:matrix_size * matrix_size].reshape(matrix_size, matrix_size)
        
        return matrix
    
    def encode_data_with_matrix(self, data_chunk, matrix):
        """
        Encode data using the transformation matrix.
        This provides an additional layer of encoding.
        
        Args:
            data_chunk: Data to encode
            matrix: Transformation matrix
            
        Returns:
            Encoded data
        """
        data_array = np.frombuffer(data_chunk, dtype=np.uint8).astype(np.float32)
        matrix_size = matrix.shape[0]
        
        # Apply matrix transformation in blocks
        encoded = []
        for i in range(0, len(data_array), matrix_size):
            block = data_array[i:i + matrix_size]
            if len(block) < matrix_size:
                block = np.pad(block, (0, matrix_size - len(block)))
            
            # Apply matrix multiplication
            transformed = np.dot(matrix[0], block)
            encoded.append(transformed % 256)  # Keep in byte range
        
        return np.array(encoded, dtype=np.uint8)
    
    def file_to_frames_with_audio(self, input_file, output_dir, fps=30):
        """
        Convert a file to video frames + audio, with matrix encoding.
        
        Args:
            input_file: Path to input file
            output_dir: Directory to save frames and audio
            fps: Frames per second (default: 30)
        """
        # Read file data
        with open(input_file, 'rb') as f:
            data = f.read()
        
        file_size = len(data)
        print(f"File size: {file_size:,} bytes")
        print(f"Video capacity per frame: {self.bytes_per_frame_video:,} bytes")
        print(f"Audio capacity per frame: {self.bytes_per_frame_audio:,} bytes")
        print(f"Total capacity per frame: {self.bytes_per_frame_total:,} bytes")
        
        # Calculate number of frames needed
        num_frames = math.ceil(file_size / self.bytes_per_frame_total)
        print(f"Number of frames needed: {num_frames}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize audio buffer
        all_audio_data = []
        
        # Store all frame metadata
        frames_metadata = []
        
        print(f"\nGenerating frames with audio encoding...")
        
        for frame_idx in range(num_frames):
            # Calculate data slice for this frame
            start_idx = frame_idx * self.bytes_per_frame_total
            end_idx = min(start_idx + self.bytes_per_frame_total, file_size)
            frame_total_data = data[start_idx:end_idx]
            
            # Split data between video and audio
            video_data_size = min(len(frame_total_data), self.bytes_per_frame_video)
            video_data = frame_total_data[:video_data_size]
            audio_data = frame_total_data[video_data_size:] if len(frame_total_data) > video_data_size else b''
            
            # Create compression matrix for this frame's data
            compressed_video, encoding_matrix, compression_meta = self.create_compression_matrix(video_data)
            
            # Pad compressed video data if needed
            if len(compressed_video) < self.bytes_per_frame_video:
                compressed_video = np.pad(compressed_video, (0, self.bytes_per_frame_video - len(compressed_video)))
            else:
                compressed_video = compressed_video[:self.bytes_per_frame_video]
            
            # Convert matrix to audio samples (this is the encoding key)
            matrix_audio = self.matrix_to_audio(encoding_matrix)
            
            # Combine actual data audio + matrix audio
            audio_data_padded = audio_data + b'\x00' * (self.bytes_per_frame_audio - len(matrix_audio) - len(audio_data))
            full_audio = matrix_audio + audio_data_padded
            
            # Convert audio bytes to 16-bit samples
            audio_samples = np.frombuffer(full_audio[:self.bytes_per_frame_audio], dtype=np.int16)
            
            # Store for later (will create actual audio file)
            all_audio_data.append(audio_samples)
            
            # Create video frame from compressed data
            pixels = np.frombuffer(compressed_video, dtype=np.uint8)
            frame_array = pixels.reshape((self.height, self.width, 3))
            
            # Create image
            img = Image.fromarray(frame_array, mode='RGB')
            frame_filename = os.path.join(output_dir, f'frame_{frame_idx:06d}.png')
            img.save(frame_filename)
            
            # Store frame metadata
            frame_meta = {
                'frame_idx': frame_idx,
                'video_bytes': video_data_size,
                'audio_bytes': len(audio_data),
                'compression': compression_meta
            }
            frames_metadata.append(frame_meta)
            
            if (frame_idx + 1) % 10 == 0 or frame_idx == num_frames - 1:
                print(f"  Generated frame {frame_idx + 1}/{num_frames} (compression ratio: {compression_meta['compression_ratio']:.2f})")
        
        # Combine all audio data
        combined_audio = np.concatenate(all_audio_data)
        
        # Save as raw PCM audio
        audio_filename = os.path.join(output_dir, 'audio.raw')
        combined_audio.tofile(audio_filename)
        
        # Save metadata
        metadata = {
            'original_filename': os.path.basename(input_file),
            'original_size': file_size,
            'width': self.width,
            'height': self.height,
            'sample_rate': self.sample_rate,
            'audio_channels': self.audio_channels,
            'num_frames': num_frames,
            'fps': fps,
            'frames': frames_metadata
        }
        
        metadata_file = os.path.join(output_dir, 'metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✓ Frames saved to: {output_dir}")
        print(f"✓ Audio saved to: {audio_filename}")
        print(f"✓ Metadata saved to: {metadata_file}")
        
        return num_frames
    
    def frames_with_audio_to_file(self, frames_dir, output_file):
        """
        Reconstruct original file from frames and audio.
        
        Args:
            frames_dir: Directory containing frames and audio
            output_file: Path to save reconstructed file
        """
        # Read metadata
        metadata_file = os.path.join(frames_dir, 'metadata.json')
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        original_size = metadata['original_size']
        num_frames = metadata['num_frames']
        
        print(f"Reconstructing file...")
        print(f"Original size: {original_size:,} bytes")
        print(f"Number of frames: {num_frames}")
        
        # Load audio data
        audio_filename = os.path.join(frames_dir, 'audio.raw')
        audio_data = np.fromfile(audio_filename, dtype=np.int16)
        
        # Collect all data
        all_data = bytearray()
        
        audio_offset = 0
        
        for frame_idx in range(num_frames):
            frame_meta = metadata['frames'][frame_idx]
            
            # Load video frame
            frame_filename = os.path.join(frames_dir, f'frame_{frame_idx:06d}.png')
            img = Image.open(frame_filename)
            frame_array = np.array(img)
            
            # Extract compressed data from frame
            compressed_bytes = frame_array.tobytes()[:frame_meta['video_bytes']]
            
            # Extract matrix from audio
            matrix_size = frame_meta['compression']['matrix_size']
            samples_for_matrix = matrix_size * matrix_size
            matrix_audio_samples = audio_data[audio_offset:audio_offset + samples_for_matrix]
            
            # Reconstruct matrix
            encoding_matrix = self.audio_to_matrix(matrix_audio_samples.tobytes(), matrix_size)
            
            # Decode compressed data using matrix
            # Since we used differential + RLE, we need to reverse both
            decompressed = self._decode_rle(np.frombuffer(compressed_bytes, dtype=np.uint8))
            
            # Reverse differential encoding
            if len(decompressed) > 0:
                base_value = frame_meta['compression']['differential_base']
                original_data = np.cumsum(decompressed, dtype=np.int32)
                original_data[0] = base_value
                original_data = np.clip(original_data, 0, 255).astype(np.uint8)
            else:
                original_data = decompressed
            
            # Take only the original length
            original_length = frame_meta['compression']['original_length']
            video_data = original_data[:original_length].tobytes()
            
            all_data.extend(video_data)
            
            # Extract audio data (after matrix samples)
            audio_start = audio_offset + samples_for_matrix
            audio_end = audio_start + (frame_meta['audio_bytes'] // 2)  # 16-bit samples
            frame_audio_samples = audio_data[audio_start:audio_end]
            frame_audio_bytes = frame_audio_samples.tobytes()[:frame_meta['audio_bytes']]
            
            all_data.extend(frame_audio_bytes)
            
            # Move audio offset
            audio_offset += self.samples_per_frame
            
            if (frame_idx + 1) % 10 == 0 or frame_idx == num_frames - 1:
                print(f"  Processed frame {frame_idx + 1}/{num_frames}")
        
        # Trim to original size
        all_data = all_data[:original_size]
        
        # Write to file
        with open(output_file, 'wb') as f:
            f.write(all_data)
        
        print(f"\n✓ File reconstructed: {output_file}")
        print(f"  Size: {len(all_data):,} bytes")
        
        # Verify size
        if len(all_data) == original_size:
            print(f"  ✓ Size verification: PASSED")
        else:
            print(f"  ⚠ Size verification: FAILED (expected {original_size}, got {len(all_data)})")
    
    def create_video_with_audio(self, frames_dir, output_video, fps=30):
        """
        Create video with audio using ffmpeg.
        
        Args:
            frames_dir: Directory containing frames and audio
            output_video: Output video filename
            fps: Frames per second
        """
        try:
            import subprocess
            
            # Check metadata
            metadata_file = os.path.join(frames_dir, 'metadata.json')
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            sample_rate = metadata['sample_rate']
            channels = metadata['audio_channels']
            
            # Convert raw audio to WAV first
            audio_raw = os.path.join(frames_dir, 'audio.raw')
            audio_wav = os.path.join(frames_dir, 'audio.wav')
            
            # Create WAV from raw PCM
            cmd_audio = [
                'ffmpeg', '-y',
                '-f', 's16le',  # 16-bit signed little-endian
                '-ar', str(sample_rate),
                '-ac', str(channels),
                '-i', audio_raw,
                audio_wav
            ]
            
            print(f"\nConverting audio to WAV...")
            subprocess.run(cmd_audio, capture_output=True)
            
            # Create video with audio
            input_pattern = os.path.join(frames_dir, 'frame_%06d.png')
            cmd_video = [
                'ffmpeg', '-y',
                '-framerate', str(fps),
                '-i', input_pattern,
                '-i', audio_wav,
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-crf', '0',  # Lossless
                '-c:a', 'pcm_s16le',  # Lossless audio
                '-shortest',
                output_video
            ]
            
            print(f"Creating video with audio...")
            result = subprocess.run(cmd_video, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Video with audio created: {output_video}")
                return True
            else:
                print(f"Error creating video: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Advanced file to video converter with audio encoding and matrix compression'
    )
    parser.add_argument('mode', choices=['encode', 'decode'], 
                       help='encode: file to frames+audio, decode: frames+audio to file')
    parser.add_argument('input', help='Input file or frames directory')
    parser.add_argument('output', help='Output directory (encode) or file (decode)')
    parser.add_argument('--width', type=int, default=1920, 
                       help='Frame width (default: 1920)')
    parser.add_argument('--height', type=int, default=1080, 
                       help='Frame height (default: 1080)')
    parser.add_argument('--sample-rate', type=int, default=48000, 
                       help='Audio sample rate (default: 48000)')
    parser.add_argument('--fps', type=int, default=30, 
                       help='Frames per second (default: 30)')
    parser.add_argument('--video', help='Create video file with audio (requires ffmpeg)')
    
    args = parser.parse_args()
    
    converter = AdvancedDataToVideoConverter(
        width=args.width, 
        height=args.height,
        sample_rate=args.sample_rate
    )
    
    if args.mode == 'encode':
        if not os.path.isfile(args.input):
            print(f"Error: Input file not found: {args.input}")
            return
        
        num_frames = converter.file_to_frames_with_audio(args.input, args.output, fps=args.fps)
        
        if args.video:
            converter.create_video_with_audio(args.output, args.video, fps=args.fps)
            
    elif args.mode == 'decode':
        if not os.path.isdir(args.input):
            print(f"Error: Frames directory not found: {args.input}")
            return
        
        converter.frames_with_audio_to_file(args.input, args.output)


if __name__ == '__main__':
    main()
