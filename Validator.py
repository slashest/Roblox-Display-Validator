import requests
import json

def get_csrf_token(session, url, headers): # needed to authenticate the account
    response = session.post(url, headers=headers)
    if 'X-CSRF-TOKEN' in response.headers:
        csrf_token = response.headers['X-CSRF-TOKEN']
        return csrf_token
    else:
        raise ValueError("CSRF token not found in response headers")

def validate_display_name(user_id, cookie, display_name):
    url = f"https://users.roblox.com/v1/users/{user_id}/display-names/validate?displayName={display_name}" # the URL to post to for validation
    
    headers = {
        'Cookie': f'.ROBLOSECURITY={cookie}'
    }
    
    with requests.Session() as session:
        options_response = session.options(url, headers=headers)
        if options_response.status_code == 200:
            print("Throttled") # OPTIONS request is needed to prepare GET request
        
        csrf_token_url = "https://auth.roblox.com/v2/login"
        csrf_token = get_csrf_token(session, csrf_token_url, headers)
        
        headers['X-CSRF-TOKEN'] = csrf_token
        
        response = session.get(url, headers=headers)
        
        return response.status_code

def read_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config['user_id'], config['cookie'], config['mode'], config['holder'] # importing options from the config file

def read_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as file: # utf-8 encoding is needed to support special characters
        return [line.strip() for line in file] # splitting into lines

def log_result(log_file, display_name, status_code):
    with open(log_file, 'a', encoding='utf-8') as file:
        if status_code == 200: # will return 200 if the display name is valid by roblox
            file.write(f"{display_name} is a valid display name\n") # logging any valids to logs.txt
        elif status_code == 400:
            file.write(f"{display_name} is an invalid display name\n")
        else: # handles stuff like 429 and 500
            file.write(f"{display_name} returned status code {status_code}\n")

if __name__ == "__main__":
    config_file_path = 'config.json'
    list_file_path = 'list.txt'
    log_file_path = 'logs.txt'
    
    user_id, cookie, mode, holder = read_config(config_file_path)
    lines = read_list(list_file_path)
    
    for line in lines:
        if mode == "Character":
            display_name1 = holder + line
            display_name2 = line * 3

            status_code1 = validate_display_name(user_id, cookie, display_name1)
            log_result(log_file_path, display_name1, status_code1)
            
            status_code2 = validate_display_name(user_id, cookie, display_name2)
            log_result(log_file_path, display_name2, status_code2)
        
        elif mode == "String":
            display_name = line
            
            status_code = validate_display_name(user_id, cookie, display_name)
            log_result(log_file_path, display_name, status_code)
