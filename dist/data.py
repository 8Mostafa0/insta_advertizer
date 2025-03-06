import json
s_file = "setting.json"

def default_settings():
    data = {
        'state':"home",
        'username':"",
        'password':"",
        'max_likes':60,
        'max_comments':13,
        'max_follows':12,
        'likes':0,
        'comments':0,
        'follows':0,
    }
    save_set(data)

def change_data(data):
    sets = settings()
    sets['max_likes'] = data['max_likes']
    sets['max_comments'] = data['max_comments']
    sets['max_follow'] = data['max_follow']
    save_set(sets)
    
def reset_sets():
    default_settings()

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
