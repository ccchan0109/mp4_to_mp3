import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip

# --- High DPI Scaling ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- Core Conversion Logic ---


def convert_mp4_to_mp3(mp4_path, mp3_path, progress_callback):
    """
    Converts a single MP4 file to MP3 using moviepy.

    Args:
        mp4_path (str): Full path to the input MP4 file.
        mp3_path (str): Full path to the output MP3 file.
        progress_callback (func): A function to call with progress updates.
    """
    try:
        progress_callback(f"開始轉換: {os.path.basename(mp4_path)}...")

        # Load the video file
        video_clip = VideoFileClip(mp4_path)

        # Extract the audio
        audio_clip = video_clip.audio

        # Write the audio file as MP3
        audio_clip.write_audiofile(mp3_path, codec="mp3", logger=None)

        # Close the clips to release resources
        audio_clip.close()
        video_clip.close()

        progress_callback(
            f"成功 ✓: {os.path.basename(mp4_path)} -> {os.path.basename(mp3_path)}"
        )
    except Exception as e:
        error_message = f"失敗 ✗: {os.path.basename(mp4_path)}. 原因: {e}"
        progress_callback(error_message)


# --- UI Application Class ---


class ConverterApp(ctk.CTk):
    def __init__(self):
        """
        Initializes the CustomTkinter application UI.
        """
        super().__init__()

        self.title("MP4 轉 MP3 批次轉換工具")
        self.geometry("700x550")

        # --- UI Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Input Folder Section
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            self.input_frame, placeholder_text="選擇來源資料夾 (MP4 檔案)"
        )
        self.input_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.input_button = ctk.CTkButton(
            self.input_frame,
            text="選擇資料夾",
            width=100,
            command=self.select_input_folder,
        )
        self.input_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        # Output Folder Section
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
        self.output_frame.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(
            self.output_frame, placeholder_text="選擇儲存資料夾 (MP3 檔案)"
        )
        self.output_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.output_button = ctk.CTkButton(
            self.output_frame,
            text="選擇資料夾",
            width=100,
            command=self.select_output_folder,
        )
        self.output_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        # Action Button
        self.convert_button = ctk.CTkButton(
            self,
            text="開始轉換",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.start_conversion_thread,
        )
        self.convert_button.grid(
            row=2, column=0, padx=15, pady=10, ipady=8, sticky="ew"
        )

        # Progress Log Section
        self.progress_text = ctk.CTkTextbox(self, wrap="word", state="disabled")
        self.progress_text.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="nsew")

    def select_input_folder(self):
        folder_path = filedialog.askdirectory(title="選擇包含 MP4 檔案的資料夾")
        if folder_path:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, folder_path)
            self.log_message(f"已選擇來源資料夾: {folder_path}")

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="選擇儲存 MP3 檔案的資料夾")
        if folder_path:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, folder_path)
            self.log_message(f"已選擇儲存資料夾: {folder_path}")

    def log_message(self, message):
        """Appends a message to the progress text area."""
        self.progress_text.configure(state="normal")
        self.progress_text.insert("end", message + "\n")
        self.progress_text.see("end")  # Auto-scroll
        self.progress_text.configure(state="disabled")
        self.update_idletasks()

    def start_conversion_thread(self):
        """Starts the conversion process in a separate thread to prevent UI freezing."""
        input_dir = self.input_entry.get()
        output_dir = self.output_entry.get()

        if not input_dir or not output_dir:
            messagebox.showerror("錯誤", "請先選擇來源資料夾和儲存資料夾。")
            return

        # Find all MP4 files
        try:
            mp4_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".mp4")]
        except FileNotFoundError:
            messagebox.showerror("錯誤", f"找不到指定的來源資料夾:\n{input_dir}")
            return

        if not mp4_files:
            messagebox.showinfo("提示", "在來源資料夾中沒有找到任何 .mp4 檔案。")
            return

        self.convert_button.configure(state="disabled", text="轉換中...")
        self.log_message("-" * 50)
        self.log_message(f"找到 {len(mp4_files)} 個 MP4 檔案，準備開始轉換。")

        # Run conversion in a new thread
        conversion_thread = threading.Thread(
            target=self.run_batch_conversion,
            args=(input_dir, output_dir, mp4_files),
            daemon=True,
        )
        conversion_thread.start()

    def run_batch_conversion(self, input_dir, output_dir, mp4_files):
        """The main loop for converting files."""
        total_files = len(mp4_files)
        success_count = 0
        fail_count = 0

        for i, filename in enumerate(mp4_files):
            self.log_message(f"[{i + 1}/{total_files}] 正在處理: {filename}")
            mp4_filepath = os.path.join(input_dir, filename)

            # Create the output filename by replacing the extension
            base_filename, _ = os.path.splitext(filename)
            mp3_filename = base_filename + ".mp3"
            mp3_filepath = os.path.join(output_dir, mp3_filename)

            try:
                convert_mp4_to_mp3(mp4_filepath, mp3_filepath, self.log_message)
                success_count += 1
            except Exception:
                fail_count += 1

        self.log_message("=" * 50)
        self.log_message(f"全部轉換完成！ 成功: {success_count}, 失敗: {fail_count}")
        self.convert_button.configure(state="normal", text="開始轉換")
        messagebox.showinfo(
            "完成",
            f"所有轉換任務已處理完畢。\n\n成功: {success_count}\n失敗: {fail_count}",
        )


# --- Main Execution ---

if __name__ == "__main__":
    app = ConverterApp()
    app.mainloop()
