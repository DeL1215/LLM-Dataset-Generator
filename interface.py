import customtkinter as ctk
from tkinter import messagebox
from configuration import get_llm, openai_model, openrouter_model
import main
import threading
import re
import datetime
import os
import time

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("LLM Dataset Generator")
app.geometry("1000x650")
app.resizable(False, False)

# 狀態變數
is_running = False
thread = None
generated_count = 0
iteration_count = 0
max_iterations = 0
log_file = None

# 控制元件變數
entry_example = None
entry_additional = None
entry_num = None
entry_max_iter = None
start_button = None
stop_button = None
log_textbox = None

def now():
    return datetime.datetime.now().strftime("%H:%M:%S")

def write_log(message: str):
    log_textbox.configure(state="normal")
    log_textbox.insert("end", message + "\n")
    log_textbox.configure(state="disabled")
    log_textbox.see("end")
    if log_file:
        log_file.write(message + "\n")
        log_file.flush()

# 模型切換
def on_model_select(model_name):
    try:
        llm_instance = get_llm(model_name)
        main.set_llm(llm_instance)
        write_log(f"[{now()}] 模型已切換為：{model_name}")
    except Exception as e:
        messagebox.showerror("錯誤", f"模型切換失敗：{e}")

# 背景產生邏輯
def run_loop(example, addtional, num):
    global is_running, generated_count, iteration_count, max_iterations
    first = True
    iteration_count = 0

    while is_running and iteration_count < max_iterations:
        try:
            result_count, prompt_text = main.generate_and_stream(example, addtional, num)
            generated_count += result_count
            iteration_count += 1

            if first:
                write_log(f"\n[Prompt 開始]\n{prompt_text}\n[Prompt 結束]\n")
                first = False
            write_log(f"[{now()}] 第 {iteration_count}/{max_iterations} 次：產生 {result_count} 筆，累計：{generated_count}")

        except Exception as e:
            write_log(f"[{now()}] 錯誤：{e}")
            break

    if is_running:
        on_stop()

# 開始執行
def on_start():
    global is_running, thread, max_iterations, log_file

    if is_running:
        return

    example = entry_example.get("1.0", "end").strip()
    addtional = entry_additional.get("1.0", "end").strip()
    num_str = entry_num.get().strip()
    max_iter_str = entry_max_iter.get().strip()

    if not example:
        messagebox.showerror("錯誤", "請輸入範例內容")
        return
    if not re.fullmatch(r"[1-9]\d*", num_str):
        messagebox.showerror("錯誤", "批次數量必須為正整數")
        return
    if not re.fullmatch(r"[1-9]\d*", max_iter_str):
        messagebox.showerror("錯誤", "最大次數必須為正整數")
        return

    os.makedirs("logs", exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_file = open(f"logs/log-{timestamp}.txt", "w", encoding="utf-8")

    write_log(f"[{now()}] 開始產生資料...")

    num = int(num_str)
    max_iterations = int(max_iter_str)

    entry_example.configure(state="disabled")
    entry_additional.configure(state="disabled")
    entry_num.configure(state="disabled")
    entry_max_iter.configure(state="disabled")
    start_button.configure(state="disabled")
    stop_button.configure(state="normal")

    is_running = True
    thread = threading.Thread(target=run_loop, args=(example, addtional, num))
    thread.daemon = True
    thread.start()

# 停止執行
def on_stop():
    global is_running
    if not is_running:
        return

    is_running = False

    entry_example.configure(state="normal")
    entry_additional.configure(state="normal")
    entry_num.configure(state="normal")
    entry_max_iter.configure(state="normal")
    start_button.configure(state="normal")
    stop_button.configure(state="disabled")

    write_log(f"[{now()}] 已停止產生資料")

def on_exit():
    on_stop()
    if log_file:
        log_file.close()
    app.destroy()

# === Layout ===
main_frame = ctk.CTkFrame(app)
main_frame.pack(expand=True, fill="both", padx=10, pady=10)

# ==== Left Panel ====
left_panel = ctk.CTkFrame(main_frame, width=450)
left_panel.pack(side="left", fill="y", padx=(10, 5), pady=10)

ctk.CTkLabel(left_panel, text="選擇模型", font=("Microsoft JhengHei", 14)).pack(pady=(10, 0))
model_selector = ctk.CTkOptionMenu(
    left_panel,
    values=[openai_model, openrouter_model],
    command=on_model_select,
    font=("Arial", 12)
)
model_selector.pack(pady=(5, 15))
model_selector.set(openai_model)
main.set_llm(get_llm(openai_model))

ctk.CTkLabel(left_panel, text="範例", font=("Microsoft JhengHei", 14)).pack()
entry_example = ctk.CTkTextbox(left_panel, width=420, height=100, font=("Arial", 12))
entry_example.pack()

ctk.CTkLabel(left_panel, text="補充說明", font=("Microsoft JhengHei", 14)).pack(pady=(15, 0))
entry_additional = ctk.CTkTextbox(left_panel, width=420, height=100, font=("Arial", 12))
entry_additional.pack()

batch_row = ctk.CTkFrame(left_panel)
batch_row.pack(pady=(15, 0))

ctk.CTkLabel(batch_row, text="每批數", font=("Microsoft JhengHei", 13)).grid(row=0, column=0, padx=(0, 5))
entry_num = ctk.CTkEntry(batch_row, width=80, font=("Arial", 12))
entry_num.grid(row=0, column=1)

ctk.CTkLabel(batch_row, text="最大次數", font=("Microsoft JhengHei", 13)).grid(row=0, column=2, padx=(10, 5))
entry_max_iter = ctk.CTkEntry(batch_row, width=80, font=("Arial", 12))
entry_max_iter.grid(row=0, column=3)

button_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
button_frame.pack(pady=25)

start_button = ctk.CTkButton(button_frame, text="執行", command=on_start, font=("Microsoft JhengHei", 12))
start_button.grid(row=0, column=0, padx=10)

stop_button = ctk.CTkButton(button_frame, text="停止", command=on_stop, font=("Microsoft JhengHei", 12), state="disabled")
stop_button.grid(row=0, column=1, padx=10)

ctk.CTkButton(button_frame, text="離開", command=on_exit, font=("Microsoft JhengHei", 12)).grid(row=0, column=2, padx=10)

# ==== Right Panel ====
right_panel = ctk.CTkFrame(main_frame)
right_panel.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

ctk.CTkLabel(right_panel, text="日誌輸出 Log", font=("Microsoft JhengHei", 16)).pack(pady=(5, 0))

log_textbox = ctk.CTkTextbox(right_panel, width=500, height=500, wrap="word", font=("Arial", 12))
log_textbox.pack(pady=(10, 10), padx=10, fill="both", expand=True)
write_log("[啟動] 請輸入參數後點選『執行』產生資料。")

app.mainloop()
