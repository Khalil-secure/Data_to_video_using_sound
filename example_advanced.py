#!/usr/bin/env python3
"""
Example usage of the Advanced Data to Video Converter
Demonstrates audio encoding and matrix compression
"""

from advanced_data_to_video import AdvancedDataToVideoConverter
import os

def example_capacity_comparison():
    """Compare capacity between basic and advanced encoding"""
    print("=" * 70)
    print("CAPACITY COMPARISON: Basic vs Advanced Encoding")
    print("=" * 70)
    
    width, height = 1920, 1080
    sample_rate = 48000
    fps = 30
    
    # Basic encoding (video only)
    pixels_per_frame = width * height
    video_bytes = pixels_per_frame * 3
    
    # Advanced encoding (video + audio)
    samples_per_frame = sample_rate // fps
    audio_bytes = samples_per_frame * 2 * 2  # stereo, 16-bit
    total_bytes = video_bytes + audio_bytes
    
    improvement = ((total_bytes - video_bytes) / video_bytes) * 100
    
    print(f"\nResolution: {width}x{height}")
    print(f"Sample Rate: {sample_rate} Hz")
    print(f"FPS: {fps}")
    print(f"\n{'Basic Encoding (Video Only)':40} {video_bytes:>15,} bytes/frame")
    print(f"{'Audio Channel Addition':40} {audio_bytes:>15,} bytes/frame")
    print(f"{'─' * 70}")
    print(f"{'Advanced Encoding (Video + Audio)':40} {total_bytes:>15,} bytes/frame")
    print(f"\n{'Improvement:':40} {improvement:>14.1f}% more capacity")
    
    print(f"\n{'Storage Examples (Advanced Encoding):'}")
    print(f"  • Per frame:        {total_bytes / (1024**2):.2f} MB")
    print(f"  • Per second:       {(total_bytes * fps) / (1024**2):.2f} MB")
    print(f"  • Per minute:       {(total_bytes * fps * 60) / (1024**2):.2f} MB")
    
    print(f"\n{'File Size Examples:'}")
    for size_mb in [1, 10, 100, 1000]:
        size_bytes = size_mb * 1024 * 1024
        frames_basic = size_bytes / video_bytes
        frames_advanced = size_bytes / total_bytes
        
        print(f"\n  {size_mb:4d} MB file:")
        print(f"    Basic:    {frames_basic:6.1f} frames ({frames_basic/fps:5.1f} seconds)")
        print(f"    Advanced: {frames_advanced:6.1f} frames ({frames_advanced/fps:5.1f} seconds)")


def example_matrix_encoding():
    """Demonstrate matrix encoding concept"""
    print("\n" + "=" * 70)
    print("MATRIX ENCODING DEMONSTRATION")
    print("=" * 70)
    
    converter = AdvancedDataToVideoConverter()
    
    # Create sample data
    sample_data = b"Hello, World! This is test data. " * 100
    
    print(f"\nOriginal data size: {len(sample_data)} bytes")
    
    # Create compression matrix
    compressed, matrix, metadata = converter.create_compression_matrix(sample_data)
    
    print(f"\nCompression Results:")
    print(f"  Compressed size:    {metadata['compressed_length']} bytes")
    print(f"  Compression ratio:  {metadata['compression_ratio']:.3f}")
    print(f"  Space saved:        {(1 - metadata['compression_ratio']) * 100:.1f}%")
    print(f"  Matrix size:        {metadata['matrix_size']}x{metadata['matrix_size']}")
    
    # Show matrix storage in audio
    matrix_audio = converter.matrix_to_audio(matrix)
    print(f"\nMatrix Storage:")
    print(f"  Matrix elements:    {matrix.size}")
    print(f"  Audio bytes needed: {len(matrix_audio)} bytes")
    print(f"  Audio samples:      {len(matrix_audio) // 2} (16-bit)")
    
    # Calculate efficiency
    overhead = len(matrix_audio)
    net_savings = len(sample_data) - metadata['compressed_length'] - overhead
    
    print(f"\nNet Efficiency:")
    print(f"  Original:           {len(sample_data)} bytes")
    print(f"  Compressed data:    {metadata['compressed_length']} bytes")
    print(f"  Matrix overhead:    {overhead} bytes")
    print(f"  Net savings:        {net_savings} bytes")
    
    if net_savings > 0:
        print(f"  ✓ Encoding beneficial for this data")
    else:
        print(f"  ⚠ Encoding adds overhead for this small sample")


def example_audio_channel_analysis():
    """Analyze audio channel capacity at different settings"""
    print("\n" + "=" * 70)
    print("AUDIO CHANNEL CAPACITY ANALYSIS")
    print("=" * 70)
    
    configs = [
        (44100, 1, "CD Quality Mono"),
        (48000, 1, "Professional Mono"),
        (48000, 2, "Professional Stereo"),
        (96000, 2, "High-Res Stereo"),
    ]
    
    fps = 30
    
    print(f"\nCapacity at {fps} FPS:")
    print(f"\n{'Configuration':30} {'Samples/Frame':>15} {'Bytes/Frame':>15} {'MB/Minute':>12}")
    print("─" * 75)
    
    for sample_rate, channels, name in configs:
        samples_per_frame = sample_rate // fps
        bytes_per_frame = samples_per_frame * channels * 2  # 16-bit
        mb_per_minute = (bytes_per_frame * fps * 60) / (1024**2)
        
        print(f"{name:30} {samples_per_frame:>15,} {bytes_per_frame:>15,} {mb_per_minute:>11.2f}")


def example_full_encoding_decoding():
    """Full encode-decode cycle demonstration"""
    print("\n" + "=" * 70)
    print("FULL ENCODE-DECODE CYCLE")
    print("=" * 70)
    
    # Create test file
    test_file = 'test_advanced.bin'
    test_data = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ' * 5000  # ~130KB
    
    with open(test_file, 'wb') as f:
        f.write(test_data)
    
    print(f"\nCreated test file: {test_file}")
    print(f"Size: {len(test_data):,} bytes")
    
    # Initialize converter
    converter = AdvancedDataToVideoConverter(width=1920, height=1080)
    
    # Encode
    print("\n" + "─" * 70)
    print("ENCODING PHASE")
    print("─" * 70)
    
    frames_dir = 'output_advanced'
    converter.file_to_frames_with_audio(test_file, frames_dir, fps=30)
    
    # Decode
    print("\n" + "─" * 70)
    print("DECODING PHASE")
    print("─" * 70)
    
    output_file = 'reconstructed_advanced.bin'
    converter.frames_with_audio_to_file(frames_dir, output_file)
    
    # Verify
    with open(output_file, 'rb') as f:
        reconstructed = f.read()
    
    print("\n" + "─" * 70)
    print("VERIFICATION")
    print("─" * 70)
    
    if test_data == reconstructed:
        print("✓ Perfect reconstruction - all bytes match!")
    else:
        print("⚠ Reconstruction mismatch")
        print(f"  Original size:      {len(test_data)}")
        print(f"  Reconstructed size: {len(reconstructed)}")
    
    # Cleanup
    os.remove(test_file)
    os.remove(output_file)
    
    print("\nTest files cleaned up.")


def example_technical_breakdown():
    """Show technical breakdown of the encoding"""
    print("\n" + "=" * 70)
    print("TECHNICAL BREAKDOWN")
    print("=" * 70)
    
    print("""
The Advanced Encoding System uses THREE layers of optimization:

1. VIDEO CHANNEL (RGB Pixels)
   • Each pixel = 3 bytes (R, G, B values 0-255)
   • 1920×1080 = 2,073,600 pixels = 6,220,800 bytes/frame
   • Stores compressed data after RLE + differential encoding

2. AUDIO CHANNEL (PCM Samples)
   • Matrix Encoding: Transformation matrix stored as audio samples
   • Data Overflow: Additional data beyond video capacity
   • 48kHz stereo = ~6,400 bytes/frame at 30fps
   
3. COMPRESSION LAYER
   • Differential Encoding: Store differences between bytes
   • RLE (Run-Length Encoding): Compress repeated patterns
   • Matrix Transformation: DCT-like compression
   
TOTAL CAPACITY per frame at 1920×1080, 48kHz stereo:
   Video: 6,220,800 bytes
   Audio:     6,400 bytes
   ──────────────────────
   Total: 6,227,200 bytes (~6.23 MB/frame)

ENCODING FLOW:
   File → Split → Compress (RLE+Diff) → Create Matrix → 
   Video: Store compressed data → 
   Audio: Store matrix + overflow data →
   Combine into video file

DECODING FLOW:
   Video file → Extract frames + audio →
   Video: Read compressed data →
   Audio: Extract matrix + overflow →
   Apply matrix → Decompress (reverse RLE+Diff) →
   Reconstruct file
""")


if __name__ == '__main__':
    print("\n" + "█" * 70)
    print("ADVANCED DATA TO VIDEO CONVERTER - EXAMPLES")
    print("█" * 70)
    
    example_capacity_comparison()
    example_matrix_encoding()
    example_audio_channel_analysis()
    example_full_encoding_decoding()
    example_technical_breakdown()
    
    print("\n" + "█" * 70)
    print("All examples completed!")
    print("█" * 70 + "\n")
