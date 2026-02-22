import subprocess
import re
import os
import json

def get_loudness_stats(file_path):
    """Analyze loudness stats as fast as possible using threads"""
    # Use loudnorm to get precise data needed for normalization
    cmd = [
        "ffmpeg", "-threads", "0", "-i", file_path,
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    
    # Extract JSON part from stderr
    match = re.search(r"\{[\s\S]*\}", result.stderr)
    if match:
        stats = json.loads(match.group())
        # Add simple lufs/peak mapping for UI feedback
        stats['lufs'] = float(stats['input_i'])
        stats['peak'] = float(stats['input_tp'])
        return stats
    return None

def normalize_audio(input_path, output_path, stats, target_lufs=-14.0):
    """Apply normalization based on pre-measured stats"""
    loudnorm_filter = (
        f"loudnorm=I={target_lufs}:TP=-1.0:LRA=11:"
        f"measured_I={stats['input_i']}:"
        f"measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:"
        f"measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:linear=true"
    )
    
    cmd = [
        "ffmpeg", "-threads", "0", "-i", input_path,
        "-af", loudnorm_filter,
        "-c:v", "copy", 
        "-c:a", "aac", 
        "-b:a", "192k",
        output_path, "-y"
    ]
    
    subprocess.run(cmd, check=True)
    return True
