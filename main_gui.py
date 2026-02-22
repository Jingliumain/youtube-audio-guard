import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import core

# High DPI Awareness for Windows
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class AudioGuardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Audio Guard 🌌")
        self.root.geometry("600x450")
        
        # UI Elements
        tk.Label(root, text="YouTube Audio Optimizer", font=("Helvetica", 18, "bold")).pack(pady=20)
        
        self.file_label = tk.Label(root, text="Step 1: Select a media file", wraplength=500, font=("Helvetica", 10))
        self.file_label.pack(pady=10)
        
        tk.Button(root, text="Browse File", command=self.select_file, width=20).pack(pady=5)
        
        # Analyze Section
        self.analyze_btn = tk.Button(root, text="Step 2: Start Analysis", 
                                    command=self.start_analysis, state=tk.DISABLED, width=20)
        self.analyze_btn.pack(pady=20)
        
        self.info_box = tk.Label(root, text="", font=("Courier", 10), justify=tk.LEFT)
        self.info_box.pack(pady=10)
        
        # Optimize Section
        self.optimize_btn = tk.Button(root, text="Step 3: Optimize (-14 LUFS)", 
                                     command=self.start_optimization, state=tk.DISABLED, 
                                     bg="#ff4d00", fg="white", font=("Helvetica", 12, "bold"), width=25)
        self.optimize_btn.pack(pady=20)
        
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)
        
        self.current_path = None
        self.current_stats = None

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Media Files", "*.mp4 *.mkv *.mov *.mp3 *.wav")])
        if file_path:
            self.current_path = file_path
            self.file_label.config(text=f"Selected: {os.path.basename(file_path)}")
            self.analyze_btn.config(state=tk.NORMAL)
            self.optimize_btn.config(state=tk.DISABLED)
            self.info_box.config(text="")
            self.status_var.set("File loaded. Please analyze.")

    def start_analysis(self):
        self.analyze_btn.config(state=tk.DISABLED)
        self.status_var.set("Analyzing... (This may take a while for large files)")
        threading.Thread(target=self.run_analysis).start()

    def run_analysis(self):
        stats = core.get_loudness_stats(self.current_path)
        if stats:
            self.current_stats = stats
            # Update UI from thread
            self.root.after(0, self.on_analysis_complete, stats)
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", "Failed to analyze file."))
            self.root.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL))

    def on_analysis_complete(self, stats):
        self.info_box.config(text=f"Integrated: {stats['lufs']} LUFS\nTrue Peak: {stats['peak']} dBFS")
        self.optimize_btn.config(state=tk.NORMAL)
        self.status_var.set("Analysis complete. Ready to optimize.")

    def start_optimization(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".mp4", 
                                                initialfile=f"optimized_{os.path.basename(self.current_path)}")
        if save_path:
            self.optimize_btn.config(state=tk.DISABLED)
            self.status_var.set("Processing... Please wait.")
            threading.Thread(target=self.run_optimization, args=(save_path,)).start()

    def run_optimization(self, output_path):
        try:
            core.normalize_audio(self.current_path, output_path, self.current_stats)
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Optimized file saved!\n{output_path}"))
            self.root.after(0, lambda: self.status_var.set("Done!"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Processing failed: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.optimize_btn.config(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioGuardGUI(root)
    root.mainloop()
