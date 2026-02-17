#!/usr/bin/env python3
"""
Example usage of the Data to Video Converter
"""

from data_to_video import DataToVideoConverter
import os

def example_encode():
    """Example: Encode a file into video frames"""
    print("=" * 60)
    print("EXAMPLE: Encoding file to video frames")
    print("=" * 60)
    
    # Create converter with custom resolution
    converter = DataToVideoConverter(width=1920, height=1080)
    
    # Example: Create a test file
    test_file = 'test_data.bin'
    test_data = b'Hello, this is test data! ' * 10000  # ~260KB
    
    with open(test_file, 'wb') as f:
        f.write(test_data)
    
    print(f"\nCreated test file: {test_file} ({len(test_data):,} bytes)")
    
    # Convert to frames
    frames_dir = 'output_frames'
    converter.file_to_frames(test_file, frames_dir)
    
    print(f"\nFrames can be found in: {frames_dir}/")
    print(f"Metadata saved in: {frames_dir}/metadata.txt")
    
    # Clean up test file
    os.remove(test_file)
    
    return frames_dir


def example_decode(frames_dir):
    """Example: Decode frames back to original file"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Decoding frames back to file")
    print("=" * 60)
    
    converter = DataToVideoConverter()
    
    # Reconstruct file
    output_file = 'reconstructed_data.bin'
    converter.frames_to_file(frames_dir, output_file)
    
    # Verify
    with open(output_file, 'rb') as f:
        reconstructed = f.read()
    
    print(f"\n✓ Reconstruction successful!")
    print(f"  First 50 bytes: {reconstructed[:50]}")
    
    # Clean up
    os.remove(output_file)


def example_different_resolutions():
    """Example: Try different resolutions"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Different resolutions comparison")
    print("=" * 60)
    
    test_data = b'X' * 100000  # 100KB
    test_file = 'test_100kb.bin'
    
    with open(test_file, 'wb') as f:
        f.write(test_data)
    
    resolutions = [
        (1920, 1080),  # Full HD
        (1280, 720),   # HD
        (854, 480),    # SD
        (640, 360),    # Low
    ]
    
    print(f"\nFile size: {len(test_data):,} bytes\n")
    
    for width, height in resolutions:
        converter = DataToVideoConverter(width=width, height=height)
        pixels_per_frame = width * height
        bytes_per_frame = pixels_per_frame * 3
        num_frames = (len(test_data) + bytes_per_frame - 1) // bytes_per_frame
        
        print(f"{width}x{height}:")
        print(f"  Pixels per frame: {pixels_per_frame:,}")
        print(f"  Bytes per frame: {bytes_per_frame:,}")
        print(f"  Frames needed: {num_frames}")
        print()
    
    os.remove(test_file)


def example_capacity_calculator():
    """Calculate storage capacity for different resolutions"""
    print("\n" + "=" * 60)
    print("STORAGE CAPACITY CALCULATOR")
    print("=" * 60)
    
    resolutions = [
        ("4K", 3840, 2160),
        ("Full HD", 1920, 1080),
        ("HD", 1280, 720),
        ("SD", 854, 480),
    ]
    
    print("\nCapacity per frame (3 bytes per pixel):\n")
    
    for name, width, height in resolutions:
        bytes_per_frame = width * height * 3
        mb_per_frame = bytes_per_frame / (1024 * 1024)
        
        # For 1 minute at 30 fps
        bytes_per_minute = bytes_per_frame * 30 * 60
        mb_per_minute = bytes_per_minute / (1024 * 1024)
        
        print(f"{name} ({width}x{height}):")
        print(f"  Per frame: {bytes_per_frame:,} bytes ({mb_per_frame:.2f} MB)")
        print(f"  Per minute (30fps): {mb_per_minute:.2f} MB")
        print()


if __name__ == '__main__':
    # Run examples
    frames_dir = example_encode()
    example_decode(frames_dir)
    example_different_resolutions()
    example_capacity_calculator()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
