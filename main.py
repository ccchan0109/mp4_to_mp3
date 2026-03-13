import os
import json
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
from moviepy.editor import VideoFileClip


# --- Constants & Config Path ---
def get_config_path():
    """
    Determines the appropriate cross-platform path for the config file.
    Ensures the directory exists.
    """
    app_name = "Mp4ToMp3Converter"

    # For Windows
    if sys.platform == "win32":
        app_data_dir = os.path.join(os.environ["APPDATA"], app_name)
    # For macOS
    elif sys.platform == "darwin":
        app_data_dir = os.path.join(
            os.path.expanduser("~"), "Library", "Application Support", app_name
        )
    # For Linux and other Unix-like systems
    else:
        app_data_dir = os.path.join(os.path.expanduser("~"), ".config", app_name)

    # Create the directory if it doesn't exist
    os.makedirs(app_data_dir, exist_ok=True)

    return os.path.join(app_data_dir, "config.json")


# --- High DPI Scaling ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# --- Configuration Handling ---
def load_config(file_path):
    """Loads configuration from a JSON file."""
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(config, file_path):
    """Saves configuration to a JSON file."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except IOError as e:
        print(f"Error saving config: {e}")


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

        # --- Encapsulated Configuration ---
        self.config_path = get_config_path()
        self.config = load_config(self.config_path)

        # Set geometry from config or default
        initial_geometry = self.config.get("window_geometry", "700x550")
        self.geometry(initial_geometry)

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

        self.load_initial_paths()

        # Protocol for saving settings on close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle window closing event to save geometry."""
        self.config["window_geometry"] = self.geometry()
        save_config(self.config, self.config_path)
        self.destroy()

    def load_initial_paths(self):
        """Load and set initial paths from config."""
        last_input = self.config.get("last_input_folder")
        last_output = self.config.get("last_output_folder")
        if last_input and os.path.isdir(last_input):
            self.input_entry.insert(0, last_input)
            self.log_message(f"已載入上次的來源資料夾: {last_input}")
        if last_output and os.path.isdir(last_output):
            self.output_entry.insert(0, last_output)
            self.log_message(f"已載入上次的儲存資料夾: {last_output}")

    def select_input_folder(self):
        """Selects input folder and saves it to config."""
        initial_dir = self.input_entry.get() or self.config.get("last_input_folder")
        folder_path = filedialog.askdirectory(
            title="選擇包含 MP4 檔案的資料夾", initialdir=initial_dir, parent=self
        )
        if folder_path:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, folder_path)
            self.log_message(f"已選擇來源資料夾: {folder_path}")
            self.config["last_input_folder"] = folder_path
            save_config(self.config, self.config_path)

    def select_output_folder(self):
        """Selects output folder and saves it to config."""
        initial_dir = self.output_entry.get() or self.config.get("last_output_folder")
        folder_path = filedialog.askdirectory(
            title="選擇儲存 MP3 檔案的資料夾", initialdir=initial_dir, parent=self
        )
        if folder_path:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, folder_path)
            self.log_message(f"已選擇儲存資料夾: {folder_path}")
            self.config["last_output_folder"] = folder_path
            save_config(self.config, self.config_path)

    def log_message(self, message):
        """Appends a message to the progress text area."""
        self.progress_text.configure(state="normal")
        self.progress_text.insert("end", message + "\n")
        self.progress_text.see("end")  # Auto-scroll
        self.progress_text.configure(state="disabled")
        self.update_idletasks()

    def start_conversion_thread(self):
        """
        Validates paths, confirms with user, and starts the conversion
        process in a separate thread to prevent UI freezing.
        """
        input_dir = self.input_entry.get()
        output_dir = self.output_entry.get()

        if not input_dir or not output_dir:
            CTkMessagebox(
                title="錯誤", message="請先選擇來源資料夾和儲存資料夾。", icon="cancel"
            )
            return

        # Find all MP4 files
        try:
            mp4_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".mp4")]
        except FileNotFoundError:
            CTkMessagebox(
                title="錯誤", message=f"找不到指定的來源資料夾:\n{input_dir}", icon="cancel"
            )
            return

        if not mp4_files:
            CTkMessagebox(
                title="提示", message="在來源資料夾中沒有找到任何 .mp4 檔案。", icon="info"
            )
            return

        # --- PRE-CONVERSION CONFIRMATION ---
        file_list_str = "\n".join(f"- {f}" for f in mp4_files)
        if len(file_list_str) > 800:  # Limit length to avoid huge dialogs
            file_list_str = file_list_str[:800] + "\n..."

        confirmation_message = (
            f"即將轉換以下 {len(mp4_files)} 個檔案：\n\n{file_list_str}\n\n是否繼續？"
        )

        msg = CTkMessagebox(
            title="確認轉換清單",
            message=confirmation_message,
            icon="question",
            option_1="取消",
            option_2="繼續",
        )

        if msg.get() != "繼續":
            self.log_message("使用者取消了操作。")
            return
        # --- END CONFIRMATION ---

        self.convert_button.configure(state="disabled", text="轉換中...")
        self.log_message("-" * 50)
        self.log_message(
            f"使用者已確認，找到 {len(mp4_files)} 個 MP4 檔案，準備開始轉換。"
        )

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
        CTkMessagebox(
            title="完成",
            message=f"所有轉換任務已處理完畢。\n\n成功: {success_count}\n失敗: {fail_count}",
            icon="check",
            option_1="太棒了",
        )


# --- Main Execution ---
if __name__ == "__main__":
    app = ConverterApp()
    app.mainloop()
