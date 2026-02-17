#!/usr/bin/env python3
"""
Comparison Script: Basic vs Advanced Encoding
Shows the benefits of audio channel + matrix compression
"""

import numpy as np
from data_to_video import DataToVideoConverter as BasicConverter
from advanced_data_to_video import AdvancedDataToVideoConverter as AdvancedConverter
import os
import time


def create_test_files():
    """Create various test files with different characteristics"""
    test_files = {}
    
    # 1. Highly repetitive data (best for compression)
    repetitive = b'A' * 10000 + b'B' * 10000 + b'C' * 10000
    test_files['repetitive.bin'] = repetitive
    
    # 2. Text data (good for compression)
    text = (b'The quick brown fox jumps over the lazy dog. ' * 500)
    test_files['text.txt'] = text
    
    # 3. Sequential data (good for differential encoding)
    sequential = bytes(range(256)) * 100
    test_files['sequential.bin'] = sequential
    
    # 4. Random data (poor for compression)
    random = np.random.randint(0, 256, 25000, dtype=np.uint8).tobytes()
    test_files['random.bin'] = random
    
    # 5. Already compressed (no benefit)
    # Simulate compressed data with high entropy
    pseudo_compressed = bytes(np.random.randint(0, 256, 25000, dtype=np.uint8))
    test_files['compressed.bin'] = pseudo_compressed
    
    # Create files
    for filename, data in test_files.items():
        with open(filename, 'wb') as f:
            f.write(data)
    
    return test_files


def compare_encoders(filename, data):
    """Compare basic vs advanced encoder on a file"""
    print(f"\n{'='*80}")
    print(f"Testing: {filename}")
    print(f"Original size: {len(data):,} bytes")
    print(f"{'='*80}")
    
    # Basic Encoder
    print(f"\n{'BASIC ENCODER':^80}")
    print("─" * 80)
    
    basic = BasicConverter(width=1920, height=1080)
    
    basic_frames = len(data) / basic.bytes_per_frame
    basic_dir = f'basic_{filename}_frames'
    
    start_time = time.time()
    basic.file_to_frames(filename, basic_dir)
    basic_time = time.time() - start_time
    
    # Count actual frames
    basic_frame_count = len([f for f in os.listdir(basic_dir) if f.startswith('frame_')])
    
    print(f"Frames created: {basic_frame_count}")
    print(f"Processing time: {basic_time:.3f} seconds")
    print(f"Capacity used: {len(data) / (basic_frame_count * basic.bytes_per_frame) * 100:.1f}%")
    
    # Advanced Encoder
    print(f"\n{'ADVANCED ENCODER':^80}")
    print("─" * 80)
    
    advanced = AdvancedConverter(width=1920, height=1080)
    
    advanced_frames = len(data) / advanced.bytes_per_frame_total
    advanced_dir = f'advanced_{filename}_frames'
    
    start_time = time.time()
    advanced.file_to_frames_with_audio(filename, advanced_dir, fps=30)
    advanced_time = time.time() - start_time
    
    # Count actual frames
    advanced_frame_count = len([f for f in os.listdir(advanced_dir) if f.startswith('frame_')])
    
    # Check compression from metadata
    import json
    with open(os.path.join(advanced_dir, 'metadata.json'), 'r') as f:
        metadata = json.load(f)
    
    avg_compression = np.mean([frame['compression']['compression_ratio'] 
                               for frame in metadata['frames']])
    
    print(f"Frames created: {advanced_frame_count}")
    print(f"Processing time: {advanced_time:.3f} seconds")
    print(f"Average compression ratio: {avg_compression:.3f}")
    print(f"Capacity used: {len(data) / (advanced_frame_count * advanced.bytes_per_frame_total) * 100:.1f}%")
    
    # Comparison
    print(f"\n{'COMPARISON':^80}")
    print("─" * 80)
    
    frame_reduction = basic_frame_count - advanced_frame_count
    time_diff = advanced_time - basic_time
    effective_capacity_improvement = (basic_frame_count / advanced_frame_count - 1) * 100
    
    print(f"\n{'Metric':<40} {'Basic':<15} {'Advanced':<15} {'Difference':<15}")
    print("─" * 80)
    print(f"{'Frames needed':<40} {basic_frame_count:<15} {advanced_frame_count:<15} {frame_reduction:>+14}")
    print(f"{'Processing time (s)':<40} {basic_time:<15.3f} {advanced_time:<15.3f} {time_diff:>+14.3f}")
    print(f"{'Bytes per frame':<40} {basic.bytes_per_frame:<15,} {advanced.bytes_per_frame_total:<15,}")
    
    if advanced_frame_count < basic_frame_count:
        print(f"\n✓ Advanced encoder is more efficient!")
        print(f"  → {effective_capacity_improvement:.1f}% better capacity utilization")
        print(f"  → Uses {frame_reduction} fewer frame(s)")
    else:
        print(f"\n⚠ Both encoders use same number of frames")
        print(f"  → Compression ratio: {avg_compression:.3f}")
    
    # Verify reconstruction
    print(f"\n{'VERIFICATION':^80}")
    print("─" * 80)
    
    # Basic reconstruction
    basic_output = f'basic_reconstructed_{filename}'
    basic.frames_to_file(basic_dir, basic_output)
    with open(basic_output, 'rb') as f:
        basic_reconstructed = f.read()
    
    basic_match = basic_reconstructed == data
    
    # Advanced reconstruction
    advanced_output = f'advanced_reconstructed_{filename}'
    advanced.frames_with_audio_to_file(advanced_dir, advanced_output)
    with open(advanced_output, 'rb') as f:
        advanced_reconstructed = f.read()
    
    advanced_match = advanced_reconstructed == data
    
    print(f"Basic reconstruction:    {'✓ PASS' if basic_match else '✗ FAIL'}")
    print(f"Advanced reconstruction: {'✓ PASS' if advanced_match else '✗ FAIL'}")
    
    # Cleanup
    import shutil
    shutil.rmtree(basic_dir)
    shutil.rmtree(advanced_dir)
    os.remove(basic_output)
    os.remove(advanced_output)
    
    return {
        'filename': filename,
        'size': len(data),
        'basic_frames': basic_frame_count,
        'advanced_frames': advanced_frame_count,
        'compression_ratio': avg_compression,
        'basic_time': basic_time,
        'advanced_time': advanced_time,
        'basic_match': basic_match,
        'advanced_match': advanced_match
    }


def print_summary(results):
    """Print summary of all tests"""
    print(f"\n{'='*80}")
    print(f"{'SUMMARY OF ALL TESTS':^80}")
    print(f"{'='*80}\n")
    
    print(f"{'File':<20} {'Size':>10} {'Basic':>8} {'Advanced':>8} {'Compression':>12} {'Saved':<8}")
    print(f"{'':20} {'(bytes)':>10} {'Frames':>8} {'Frames':>8} {'Ratio':>12} {'Frames':<8}")
    print("─" * 80)
    
    for result in results:
        saved = result['basic_frames'] - result['advanced_frames']
        print(f"{result['filename']:<20} {result['size']:>10,} {result['basic_frames']:>8} "
              f"{result['advanced_frames']:>8} {result['compression_ratio']:>12.3f} {saved:>+7}")
    
    print("\n" + "─" * 80)
    
    total_basic = sum(r['basic_frames'] for r in results)
    total_advanced = sum(r['advanced_frames'] for r in results)
    total_saved = total_basic - total_advanced
    avg_compression = np.mean([r['compression_ratio'] for r in results])
    
    print(f"{'TOTALS:':<20} {'':>10} {total_basic:>8} {total_advanced:>8} "
          f"{avg_compression:>12.3f} {total_saved:>+7}")
    
    improvement = (total_saved / total_basic) * 100 if total_basic > 0 else 0
    
    print(f"\n{'Overall Improvement:':<40} {improvement:>6.1f}%")
    print(f"{'Average Compression Ratio:':<40} {avg_compression:>6.3f}")
    print(f"{'All Verifications Passed:':<40} {'Yes' if all(r['basic_match'] and r['advanced_match'] for r in results) else 'No'}")


def main():
    print("█" * 80)
    print(f"{'BASIC vs ADVANCED ENCODER COMPARISON':^80}")
    print("█" * 80)
    
    print("\nCreating test files with different characteristics...")
    test_files = create_test_files()
    print(f"Created {len(test_files)} test files")
    
    results = []
    
    for filename, data in test_files.items():
        result = compare_encoders(filename, data)
        results.append(result)
    
    print_summary(results)
    
    # Cleanup test files
    print("\nCleaning up test files...")
    for filename in test_files.keys():
        if os.path.exists(filename):
            os.remove(filename)
    
    print("\n" + "█" * 80)
    print(f"{'COMPARISON COMPLETE':^80}")
    print("█" * 80 + "\n")


if __name__ == '__main__':
    main()
