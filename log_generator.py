import os
import re

def read_files(path):
    dataset = []
    for filename in os.listdir(path):
        with open(os.path.join(path, filename), encoding='utf-8') as f:
            line = f.read().replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
            dataset.append(re.sub(r'\s+', ' ', line))
    return dataset

def generate_logs_from_dataset(dataset_path, log_output_path):
    if not os.path.exists(log_output_path):
        os.makedirs(log_output_path)
 
    dataset = read_files(dataset_path)

    for idx, content in enumerate(dataset):
        log_filename = os.path.join(log_output_path, f"log_{idx}.txt")
        with open(log_filename, 'w', encoding='utf-8') as log_file:
            log_file.write(content)
