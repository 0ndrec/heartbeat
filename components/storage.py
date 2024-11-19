import json
import os

class LocalStorageManager:
    @staticmethod
    def get_local_storage():
        if os.path.exists('localStorage.json'):
            try:
                with open('localStorage.json', 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # If the file is empty or corrupted, return an empty dictionary
                return {}
        return {}

    @staticmethod
    def set_local_storage(data):
        current_data = LocalStorageManager.get_local_storage()
        new_data = {**current_data, **data}
        with open('localStorage.json', 'w') as f:
            json.dump(new_data, f)
