import customtkinter as ctk
from tkinter import messagebox
from main import generate_and_stream
import threading
import re
import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("LLM Dataset Generator")
app.geometry("1000x600")
app.resizable(False, False)

# 狀態變數
is_running = False
thread = None
generated_count = 0
log_textbox = None

# 時間顯示函數
def now():
    return datetime.datetime.now().strftime("%H:%M:%S")

# 背景執行函數
def run_loop(example, addtional, num):
    global is_running, generated_count
    first = True  
    while is_running:
        try:
            result_count, prompt_text = generate_and_stream(example, addtional, num)
            generated_count += result_count

            log_textbox.configure(state="normal")

            if first:
                log_textbox.insert("end", f"\n[Prompt 開始]\n{prompt_text}\n[Prompt 結束]\n\n")
                first = False

            log_textbox.insert("end", f"[{now()}] 產生 {result_count} 筆資料，總共：{generated_count}\n")
            log_textbox.configure(state="disabled")
            log_textbox.see("end")

        except Exception as e:
            log_textbox.configure(state="normal")
            log_textbox.insert("end", f"[{now()}] 錯誤：{e}\n")
            log_textbox.configure(state="disabled")
            log_textbox.see("end")


# 啟動執行
def on_start():
    global is_running, thread
    if is_running:
        return

    example = entry_example.get("1.0", "end").strip()
    addtional = entry_additional.get("1.0", "end").strip()
    num_str = entry_num.get()

    # 檢查必填欄位
    if not example:
        messagebox.showerror("錯誤", "請輸入範例內容")
        return

    if not re.fullmatch(r"\d+", num_str):
        messagebox.showerror("錯誤", "請輸入有效數字")
        log_textbox.configure(state="normal")
        log_textbox.insert("end", f"[{now()}] 錯誤：num 必須是數字\n")
        log_textbox.configure(state="disabled")
        log_textbox.see("end")
        return

    num = int(num_str)
    is_running = True
    thread = threading.Thread(target=run_loop, args=(example, addtional, num))
    thread.daemon = True
    thread.start()


# 停止執行
def on_stop():
    global is_running
    is_running = False
    log_textbox.configure(state="normal")
    log_textbox.insert("end", f"[{now()}] 已停止產生資料\n")
    log_textbox.configure(state="disabled")
    log_textbox.see("end")

# 離開應用程式
def on_exit():
    on_stop()
    app.destroy()

# === Layout: main 2 columns ===
main_frame = ctk.CTkFrame(app)
main_frame.pack(expand=True, fill="both", padx=10, pady=10)

# ==== Left Panel ====
left_panel = ctk.CTkFrame(main_frame, width=450)
left_panel.pack(side="left", fill="y", padx=(10, 5), pady=10)

ctk.CTkLabel(left_panel, text="範例", font=("Arial", 14)).pack(pady=(10, 0))
entry_example = ctk.CTkTextbox(left_panel, width=420, height=100, font=("Arial", 12))
entry_example.pack()

ctk.CTkLabel(left_panel, text="補充說明", font=("Arial", 14)).pack(pady=(15, 0))
entry_additional = ctk.CTkTextbox(left_panel, width=420, height=100, font=("Arial", 12))
entry_additional.pack()

ctk.CTkLabel(left_panel, text="批次產生數量", font=("Arial", 14)).pack(pady=(15, 0))
entry_num = ctk.CTkEntry(left_panel, width=150, font=("Arial", 12))
entry_num.pack()

button_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
button_frame.pack(pady=25)

ctk.CTkButton(button_frame, text="執行", command=on_start, font=("Arial", 12)).grid(row=0, column=0, padx=10)
ctk.CTkButton(button_frame, text="停止", command=on_stop, font=("Arial", 12)).grid(row=0, column=1, padx=10)
ctk.CTkButton(button_frame, text="離開", command=on_exit, font=("Arial", 12)).grid(row=0, column=2, padx=10)

# ==== Right Panel ====
right_panel = ctk.CTkFrame(main_frame)
right_panel.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

ctk.CTkLabel(right_panel, text="日誌輸出 Log", font=("Arial", 16)).pack(pady=(5, 0))

log_textbox = ctk.CTkTextbox(right_panel, width=500, height=500, wrap="word", font=("Arial", 12))
log_textbox.pack(pady=(10, 10), padx=10, fill="both", expand=True)
log_textbox.insert("end", "[啟動] LLM Dataset Generator 已啟動...\n")
log_textbox.configure(state="disabled")

app.mainloop()