import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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
        self.root.title("YouTube Audio Guard v3 🌌")
        self.root.geometry("600x600")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Header
        header = tk.Frame(root, bg="#2c3e50", height=80)
        header.pack(fill=tk.X)
        tk.Label(header, text="YouTube Audio Optimizer", font=("Helvetica", 20, "bold"), fg="white", bg="#2c3e50").pack(pady=20)
        
        main_frame = tk.Frame(root, padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # File Selection
        self.file_label = tk.Label(main_frame, text="Step 1: Select a media file", wraplength=500, font=("Helvetica", 11))
        self.file_label.pack(pady=10)
        tk.Button(main_frame, text="Browse File", command=self.select_file, width=20, bg="#ecf0f1").pack()
        
        # Options
        opt_frame = tk.LabelFrame(main_frame, text=" Video Options ", pady=10, padx=10)
        opt_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(opt_frame, text="Video Codec:").grid(row=0, column=0, sticky=tk.W)
        self.codec_var = tk.StringVar(value="copy")
        codecs = [
            ("Stream Copy (Fastest - No Video Changes)", "copy"),
            ("H.264 (Standard CPU)", "h264_cpu"),
            ("H.264 (Hardware - AMD/Intel Linux)", "h264_vaapi"),
            ("H.264 (Hardware - NVIDIA)", "h264_nvenc")
        ]
        self.codec_menu = ttk.Combobox(opt_frame, textvariable=self.codec_var, width=40, state="readonly")
        self.codec_menu['values'] = [c[0] for c in codecs]
        self.codec_menu.current(0)
        self.codec_menu.grid(row=0, column=1, padx=10)
        self.codecs_map = {c[0]: c[1] for c in codecs}

        # Analyze
        self.analyze_btn = tk.Button(main_frame, text="Step 2: Start Fast Analysis", 
                                    command=self.start_analysis, state=tk.DISABLED, width=25, height=2)
        self.analyze_btn.pack(pady=10)
        
        self.info_box = tk.Label(main_frame, text="", font=("Courier New", 10), justify=tk.LEFT, bg="#f9f9f9", width=50, height=3)
        self.info_box.pack(pady=5)
        
        # Optimize
        self.optimize_btn = tk.Button(main_frame, text="Step 3: Optimize & Export", 
                                     command=self.start_optimization, state=tk.DISABLED, 
                                     bg="#ff4d00", fg="white", font=("Helvetica", 12, "bold"), width=30, height=2)
        self.optimize_btn.pack(pady=20)
        
        # Progress
        tk.Label(main_frame, text="Progress:").pack(anchor=tk.W)
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=540, mode='determinate')
        self.progress.pack(pady=5)
        
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
            self.progress['value'] = 0
            self.status_var.set("File loaded. Please analyze.")

    def update_progress(self, val):
        self.progress['value'] = val
        self.root.update_idletasks()

    def start_analysis(self):
        self.analyze_btn.config(state=tk.DISABLED)
        self.status_var.set("Analyzing audio levels...")
        self.progress['value'] = 0
        threading.Thread(target=self.run_analysis).start()

    def run_analysis(self):
        try:
            stats = core.get_loudness_stats(self.current_path, progress_callback=self.update_progress)
            if stats:
                self.current_stats = stats
                self.root.after(0, self.on_analysis_complete, stats)
            else:
                raise Exception("Could not retrieve statistics.")
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed: {str(e)}"))
            self.root.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL))

    def on_analysis_complete(self, stats):
        self.info_box.config(text=f"LOUDNESS: {stats['lufs']} LUFS\nPEAK: {stats['peak']} dBFS\nReady to adjust by {stats['target_offset']} dB")
        self.optimize_btn.config(state=tk.NORMAL)
        self.status_var.set("Analysis complete.")
        self.progress['value'] = 100

    def start_optimization(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".mp4", 
                                                initialfile=f"youtube_{os.path.basename(self.current_path)}")
        if save_path:
            self.optimize_btn.config(state=tk.DISABLED)
            self.progress['value'] = 0
            mode = self.codecs_map[self.codec_menu.get()]
            self.status_var.set(f"Processing ({mode})...")
            threading.Thread(target=self.run_optimization, args=(save_path, mode)).start()

    def run_optimization(self, output_path, mode):
        try:
            core.normalize_audio(self.current_path, output_path, self.current_stats, 
                                 codec_mode=mode, progress_callback=self.update_progress)
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Done!\n{output_path}"))
            self.root.after(0, lambda: self.status_var.set("Optimization Successful!"))
            self.root.after(0, lambda: self.progress.config(value=100))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Export failed: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.optimize_btn.config(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioGuardGUI(root)
    root.mainloop()
