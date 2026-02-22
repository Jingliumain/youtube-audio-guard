import core
import os

input_file = "/home/issey/flux.mp4"
output_file = "/home/issey/optimized_flux.mp4"

print("--- Start Test Run ---")
stats = core.get_loudness_stats(input_file)
if stats:
    print(f"Stats found: LUFS={stats['lufs']}, Peak={stats['peak']}")
    print("Normalizing...")
    core.normalize_audio(input_file, output_file, stats)
    print(f"Success! Output saved to {output_file}")
    print(f"Size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
else:
    print("Failed to get stats.")
