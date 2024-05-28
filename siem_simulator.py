import numpy as np

def siem_process(classified_logs):
    for idx, log in enumerate(classified_logs):
        log_class = np.argmax(log)
        if log_class == 1:
            print(f"Alert: Malicious activity detected in log {idx}")
        else:
            print(f"Info: Normal activity in log {idx}")
