import core
import os

input_file = "/home/issey/flux.mp4"
output_file = "/home/issey/optimized_flux_v3.mp4"

def p_callback(p):
    if p % 10 == 0:
        print(f"Progress: {p}%")

print("--- Start v3 Test ---")
stats = core.get_loudness_stats(input_file, progress_callback=p_callback)
if stats:
    print(f"Analysis Done: {stats['lufs']} LUFS")
    core.normalize_audio(input_file, output_file, stats, codec_mode="copy", progress_callback=p_callback)
    print(f"Success! Output: {output_file}")
else:
    print("Failed.")
