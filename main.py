import os
import threading
import time
import logging
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk
from log_generator import generate_logs_from_dataset
from model_loader import load_model, classify_logs
from siem_simulator import siem_process

class LogProcessingThread(threading.Thread):
    def __init__(self, logs, model, results, lock, threat_files):
        super(LogProcessingThread, self).__init__()
        self.logs = logs
        self.model = model
        self.results = results
        self.lock = lock
        self.threat_files = threat_files

    def run(self):
        try:
            classified_logs = classify_logs(self.logs, self.model)
            with self.lock:
                for idx, log in enumerate(classified_logs):
                    log_class = log.argmax()
                    if log_class == 1:
                        self.threat_files.append(self.logs[idx])
        except Exception as e:
            logging.error(f"An error occurred in files: {self.logs}: {str(e)}")

def send_notification(title, message):
    root = tk.Tk()
    root.withdraw()  # Скрыть корневое окно
    root.after(1000)  # Небольшая задержка перед показом окна
    messagebox.showerror(title, message)
    root.mainloop()  # Запуск цикла обработки событий Tkinter

def show_notification(threat_files, time_taken, files_checked):
    root = tk.Tk()
    root.title("SIEM Notification")
    root.iconbitmap("icon.ico")  # Установите путь к вашей иконке

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=15)
    text_area.pack(expand=True, fill='both')

    summary = f"Time taken: {time_taken:.2f} seconds\nFiles checked: {files_checked}\nAlert files: {len(threat_files)}\n\n"
    text_area.insert(tk.END, summary)
    
    if threat_files:
        text_area.insert(tk.END, "Malicious activity detected in the following log files:\n")
        for file in threat_files:
            text_area.insert(tk.END, file + "\n")
    else:
        text_area.insert(tk.END, "No malicious activity detected.")

    root.mainloop()

def main(log_output_path):
    try:
        start_time = time.time()

        # Генерация логов
        dataset_path = 'test_ds_valid'
        generate_logs_from_dataset(dataset_path, log_output_path)

        # Загрузка модели
        model_path = 'model_pwsh'
        model = load_model(model_path)

        # Классификация логов
        logs = [os.path.join(log_output_path, f) for f in os.listdir(log_output_path)]

        # Многопоточная обработка логов
        num_threads = 4  # Вы можете настроить количество потоков в соответствии с вашими ресурсами
        results = []
        lock = threading.Lock()
        threat_files = []
        threads = []
        for i in range(num_threads):
            thread_logs = logs[i::num_threads]
            thread = LogProcessingThread(thread_logs, model, results, lock, threat_files)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Симуляция работы SIEM системы
        siem_process(results)

        end_time = time.time()
        time_taken = end_time - start_time

        show_notification(threat_files, time_taken, len(logs))

    except Exception as e:
        # Обработка ошибок и отправка уведомления
        logging.error(f"An error occurred: {str(e)}")
        send_notification("SIEM Error", f"An error occurred: {str(e)}")

def select_folder():
    folder_selected = filedialog.askdirectory()
    return folder_selected

def start_default_scan():
    log_output_path = 'logs'
    threading.Thread(target=main, args=(log_output_path,)).start()

def start_custom_scan():
    log_output_path = select_folder()
    if log_output_path:
        threading.Thread(target=main, args=(log_output_path,)).start()

def run_in_background(root, interval_minutes):
    def background_task():
        while True:
            main('logs')
            time.sleep(interval_minutes * 60)  # Перезапуск через указанный интервал в минутах
    threading.Thread(target=background_task, daemon=True).start()
    root.iconify()  # Свернуть окно, но программа будет работать в фоновом режиме

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def create_gui():
    root = tk.Tk()
    root.title("SIEM Log Scanner")
    root.iconbitmap("icon.ico")  # Установите путь к вашей иконке

    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 12), background='lightblue', foreground='black')
    style.configure('TLabel', font=('Helvetica', 12), background='lightblue', foreground='black')
    root.configure(background='lightblue')

    frame = ttk.Frame(root, padding="10")
    frame.pack(expand=True, fill='both')

    ttk.Label(frame, text="Select log output folder or use default:").pack(pady=10)

    ttk.Button(frame, text="Use Default", command=start_default_scan).pack(pady=5)
    ttk.Button(frame, text="Select Folder", command=start_custom_scan).pack(pady=5)

    # Добавление выпадающего списка для выбора интервала времени
    interval_label = ttk.Label(frame, text="Select interval (minutes) for background scan:")
    interval_label.pack(pady=10)

    interval_var = tk.IntVar(value=60)  # Значение по умолчанию 60 минут
    interval_combobox = ttk.Combobox(frame, textvariable=interval_var, values=[10, 30, 60, 120, 240])
    interval_combobox.pack(pady=5)

    ttk.Button(frame, text="Run in Background", command=lambda: run_in_background(root, interval_var.get())).pack(pady=5)

    root.geometry('400x250')
    center_window(root)
    root.mainloop()

if __name__ == "__main__":
    create_gui()
