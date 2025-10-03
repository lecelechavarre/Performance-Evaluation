from filelock import FileLock
import json

def load_json(path):
    lock = FileLock(path + '.lock')
    with lock:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

def save_json(path, data):
    lock = FileLock(path + '.lock')
    with lock:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
