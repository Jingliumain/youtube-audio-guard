import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import core

class AudioGuardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Audio Guard 🌌")
        self.root.geometry("500x400")
        
        # UI Elements
        tk.Label(root, text="YouTube Audio Adjustment Tool", font=("Helvetica", 16, "bold")).pack(pady=20)
        
        self.file_label = tk.Label(root, text="No file selected", wraplength=400)
        self.file_label.pack(pady=10)
        
        tk.Button(root, text="Select Video/Audio File", command=self.select_file).pack(pady=5)
        
        self.info_box = tk.Label(root, text="", fg="blue")
        self.info_box.pack(pady=20)
        
        self.process_btn = tk.Button(root, text="Optimize for YouTube (-14 LUFS)", 
                                    command=self.start_process, state=tk.DISABLED, 
                                    bg="#ff4d00", fg="white", font=("Helvetica", 10, "bold"))
        self.process_btn.pack(pady=10)
        
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)
        
        self.current_path = None

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Media Files", "*.mp4 *.mkv *.mov *.mp3 *.wav")])
        if file_path:
            self.current_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.status_var.set("Analyzing file...")
            
            # Run analysis in background thread
            threading.Thread(target=self.run_initial_analysis).start()

    def run_initial_analysis(self):
        stats = core.analyze_only(self.current_path)
        if stats:
            self.info_box.config(text=f"Current: {stats['lufs']} LUFS\nTrue Peak: {stats['peak']} dBFS")
            self.process_btn.config(state=tk.NORMAL)
            self.status_var.set("Analysis complete. Ready to optimize.")
        else:
            self.status_var.set("Failed to analyze file.")

    def start_process(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".mp4", 
                                                initialfile=f"optimized_{os.path.basename(self.current_path)}")
        if save_path:
            self.process_btn.config(state=tk.DISABLED)
            self.status_var.set("Optimizing... Please wait (this may take a minute)")
            threading.Thread(target=self.run_optimization, args=(save_path,)).start()

    def run_optimization(self, output_path):
        try:
            # 1. Get detailed stats
            stats = core.get_loudness_stats(self.current_path)
            if not stats:
                raise Exception("Failed to get audio statistics.")
            
            # 2. Normalize
            core.normalize_audio(self.current_path, output_path, stats)
            
            messagebox.showinfo("Success", f"Optimization complete!\nSaved to: {output_path}")
            self.status_var.set("Success!")
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
            self.status_var.set("Error occurred.")
        finally:
            self.process_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioGuardGUI(root)
    root.mainloop()
