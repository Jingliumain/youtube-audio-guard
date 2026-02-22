import subprocess
import re
import os
import json

def get_loudness_stats(file_path):
    """1st pass: Analyze loudness stats"""
    cmd = [
        "ffmpeg", "-i", file_path,
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    
    # Extract JSON part from stderr
    match = re.search(r"\{[\s\S]*\}", result.stderr)
    if match:
        return json.loads(match.group())
    return None

def normalize_audio(input_path, output_path, stats, target_lufs=-14.0):
    """2nd pass: Apply normalization based on stats"""
    # Build the loudnorm filter string with measured data for perfect results
    loudnorm_filter = (
        f"loudnorm=I={target_lufs}:TP=-1.0:LRA=11:"
        f"measured_I={stats['input_i']}:"
        f"measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:"
        f"measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:linear=true"
    )
    
    cmd = [
        "ffmpeg", "-i", input_path,
        "-af", loudnorm_filter,
        "-c:v", "copy", # Keep video as is (no re-encoding)
        "-c:a", "aac",  # Standard audio for YouTube
        "-b:a", "192k",
        output_path, "-y"
    ]
    
    subprocess.run(cmd, check=True)
    return True

def analyze_only(file_path):
    """Simple check for human feedback"""
    cmd = [
        "ffmpeg", "-i", file_path,
        "-af", "ebur128=peak=true",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    output = result.stderr
    
    int_match = re.search(r"Integrated loudness:\s+(-?\d+\.?\d*)\s+LUFS", output)
    tp_match = re.search(r"True peak:\s+(-?\d+\.?\d*)\s+dBFS", output)
    
    if int_match:
        return {
            "lufs": float(int_match.group(1)),
            "peak": float(tp_match.group(1)) if tp_match else 0.0
        }
    return None
