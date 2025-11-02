import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

from build_manifest import ManifestBuilder


class ManifestBuilderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ACC Livery Manifest Builder")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        self.is_building = False

        # Create main frame
        main_frame = ttk.Frame(root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text="ACC Livery Manifest Builder",
                         font=("Arial", 14, "bold"))
        title.pack(pady=10)

        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        input_frame.pack(fill=tk.X, pady=10)

        # Liveries folder
        ttk.Label(input_frame, text="Liveries Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.folder_var = tk.StringVar()
        folder_entry = ttk.Entry(input_frame, textvariable=self.folder_var, width=50)
        folder_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)

        # Output folder
        ttk.Label(input_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar(value=str(Path.cwd()))
        output_entry = ttk.Entry(input_frame, textvariable=self.output_var, width=50)
        output_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)

        # League name
        ttk.Label(input_frame, text="League Name:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.league_var = tk.StringVar(value="GT3 Championship")
        league_entry = ttk.Entry(input_frame, textvariable=self.league_var, width=50)
        league_entry.grid(row=2, column=1, padx=5, pady=5)

        # Version
        ttk.Label(input_frame, text="Version:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.version_var = tk.StringVar(value="1.0.0")
        version_entry = ttk.Entry(input_frame, textvariable=self.version_var, width=50)
        version_entry.grid(row=3, column=1, padx=5, pady=5)

        # Checkboxes
        self.skip_compare_var = tk.BooleanVar(value=False)
        skip_check = ttk.Checkbutton(input_frame, text="Skip comparison with existing manifest",
                                     variable=self.skip_compare_var)
        skip_check.grid(row=4, column=1, sticky=tk.W, pady=10)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.build_button = ttk.Button(button_frame, text="Build Manifest", command=self.start_build)
        self.build_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT, padx=5)

        # Output frame
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Output text widget
        self.output_text = scrolledtext.ScrolledText(output_frame, height=20, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Liveries Folder")
        if folder:
            self.folder_var.set(folder)

    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_var.set(folder)

    def log_output(self, message):
        """Append text to output widget."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def clear_output(self):
        """Clear the output widget."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def start_build(self):
        """Start building manifest in a separate thread."""
        if self.is_building:
            messagebox.showwarning("Warning", "Build already in progress")
            return

        liveries_folder = self.folder_var.get()
        if not liveries_folder:
            messagebox.showerror("Error", "Please select a liveries folder")
            return

        self.is_building = True
        self.build_button.config(state=tk.DISABLED)
        self.status_var.set("Building manifest...")

        # Capture stdout/stderr
        output_capture = io.StringIO()
        error_capture = io.StringIO()

        def build_thread():
            try:
                with redirect_stdout(output_capture), redirect_stderr(error_capture):
                    builder = ManifestBuilder(
                        liveries_folder,
                        self.output_var.get()
                    )

                    self.log_output("Building manifest from: " + str(builder.liveries_folder))
                    self.log_output("")

                    # Load existing manifest for comparison
                    old_manifest = None if self.skip_compare_var.get() else builder.load_existing_manifest()

                    # Build new manifest
                    new_manifest = builder.build_manifest(
                        self.league_var.get(),
                        self.version_var.get()
                    )

                    # Compare if old manifest exists
                    if old_manifest and not self.skip_compare_var.get():
                        builder.compare_manifests(old_manifest, new_manifest)
                        self.log_output("")

                    # Save manifest
                    builder.save_manifest(new_manifest)

                self.status_var.set("Manifest built successfully!")
                messagebox.showinfo("Success", "Manifest built successfully!")

            except Exception as e:
                self.log_output(f"Error: {str(e)}")
                self.status_var.set(f"Error: {str(e)}")
                messagebox.showerror("Error", f"Failed to build manifest:\n{str(e)}")

            finally:
                self.is_building = False
                self.build_button.config(state=tk.NORMAL)

                # Output captured content
                output = output_capture.getvalue()
                if output:
                    for line in output.strip().split('\n'):
                        self.log_output(line)

                error = error_capture.getvalue()
                if error:
                    for line in error.strip().split('\n'):
                        self.log_output(f"ERROR: {line}")

        thread = threading.Thread(target=build_thread, daemon=True)
        thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ManifestBuilderGUI(root)
    root.mainloop()
