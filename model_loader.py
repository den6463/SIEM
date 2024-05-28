import tensorflow as tf
import os
import re

def load_model(model_path):
    return tf.keras.models.load_model(model_path)

def clean_data_to_tokens(dataset):
    tokens = []
    char_replace = "()[]{},;'/\=:^<>|`+\""
    for source_string in dataset:
        source_string = re.sub(r"FromBase64String\(\'(.*)\'\)", "base64_string", source_string)
        source_string = re.sub(r"([a-zA-Z0-9\/\+=]{100,})+", "base64_string", source_string)
        for char in char_replace:
            source_string = source_string.replace(char, ' ')
        source_string = re.sub(r"(?<!\S)\d+(?!\S)", " ", source_string)
        source_string = re.sub(r"0x\S+", " ", source_string)
        ip_addresses = re.findall(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', source_string)
        for ip in ip_addresses:
            if ip.startswith('10.') or ip.startswith('192.') or ip.startswith('172.16.') or ip.startswith('127.0.'):
                source_string = source_string.replace(ip, 'internal_ip')
            else:
                source_string = source_string.replace(ip, 'external_ip')
        source_string = source_string.replace('.', ' ')
        tokens.append(re.sub(r'\s+', ' ', source_string.lower()))
    return tokens

def classify_logs(logs, model):
    logs_data = []
    for log in logs:
        with open(log, 'r', encoding='utf-8') as file:
            logs_data.append(file.read())
    
    tokenized_logs = clean_data_to_tokens(logs_data)
    vectorized_logs = tf.constant(tokenized_logs)  # Convert to TensorFlow constant
    
    # Assuming text_vectorizer and token_embed are already created as per the model training script
    text_vectorizer = model.get_layer('text_vectorization')
    token_embed = model.get_layer('embedding')

    vectorized_logs_flat = tf.reshape(vectorized_logs, [-1])  # Flatten to 1D array
    predictions = model.predict(vectorized_logs_flat)

    return predictions
