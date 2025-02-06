import json
s_file = "setting.json"

def default_settings():
    data = {
        'max_like':0,
        'max_comments':0,
        'max_follow':0,
        'likes':0,
        'comments':0,
        'follows':0,
    }
    save_set(data)

def settings():
    try:
        with open(s_file, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        default_settings()
        return settings()
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file {s_file}.")
        return None


def save_set(data):
    try:
        with open(s_file, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error : {e}")
