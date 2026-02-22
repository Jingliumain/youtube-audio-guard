import subprocess
import re
import os
import json
import shutil

def check_dependencies():
    """Check if ffmpeg and ffprobe are available in the system path"""
    deps = ["ffmpeg", "ffprobe"]
    missing = [d for d in deps if shutil.which(d) is None]
    if missing:
        return False, f"Missing dependencies: {', '.join(missing)}. Please install FFmpeg and add it to your PATH."
    return True, ""

def get_duration(file_path):
    """Get duration of media file in seconds"""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return 0.0
        return float(result.stdout.strip())
    except:
        return 0.0

def run_ffmpeg_with_progress(cmd, duration, progress_callback):
    """Run FFmpeg and parse stderr for progress"""
    # On Windows, we need to handle subprocess slightly differently for 'noconsole' mode
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True, universal_newlines=True, startupinfo=startupinfo)
    
    time_regex = re.compile(r"time=(\d+):(\d+):(\d+).(\d+)")
    
    full_output = []
    while True:
        line = process.stderr.readline()
        if not line:
            break
        full_output.append(line)
        
        match = time_regex.search(line)
        if match and duration > 0:
            hours, minutes, seconds, ms = map(int, match.groups())
            current_time = hours * 3600 + minutes * 60 + seconds + ms / 100
            progress = min(100, int((current_time / duration) * 100))
            if progress_callback:
                progress_callback(progress)
                
    process.wait()
    return "".join(full_output)

def get_loudness_stats(file_path, progress_callback=None):
    """Analyze loudness stats with progress tracking"""
    duration = get_duration(file_path)
    cmd = [
        "ffmpeg", "-threads", "0", "-i", file_path,
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json",
        "-f", "null", "-"
    ]
    
    output = run_ffmpeg_with_progress(cmd, duration, progress_callback)
    
    match = re.search(r"\{[\s\S]*\}", output)
    if match:
        stats = json.loads(match.group())
        stats['lufs'] = float(stats['input_i'])
        stats['peak'] = float(stats['input_tp'])
        return stats
    return None

def normalize_audio(input_path, output_path, stats, codec_mode="copy", target_lufs=-14.0, progress_callback=None):
    """Apply normalization with optional video re-encoding"""
    duration = get_duration(input_path)
    
    loudnorm_filter = (
        f"loudnorm=I={target_lufs}:TP=-1.0:LRA=11:"
        f"measured_I={stats['input_i']}:"
        f"measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:"
        f"measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:linear=true"
    )
    
    cmd = ["ffmpeg", "-threads", "0", "-i", input_path, "-af", loudnorm_filter]
    
    if codec_mode == "copy":
        cmd += ["-c:v", "copy"]
    elif codec_mode == "h264_cpu":
        cmd += ["-c:v", "libx264", "-preset", "faster", "-crf", "23"]
    elif codec_mode == "h264_vaapi":
        cmd += ["-c:v", "h264_vaapi", "-vaapi_device", "/dev/dri/renderD128", "-vf", "format=nv12,hwupload"]
    elif codec_mode == "h264_nvenc":
        cmd += ["-c:v", "h264_nvenc", "-preset", "fast"]
        
    cmd += ["-c:a", "aac", "-b:a", "192k", output_path, "-y"]
    
    run_ffmpeg_with_progress(cmd, duration, progress_callback)
    return True
