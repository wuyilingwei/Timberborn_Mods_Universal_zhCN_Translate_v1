import configparser
import os
import subprocess
import shutil
import requests
import csv
import json
import time

timestamp = time.strftime('%Y-%m-%d-%H-%M-%S')
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', f'{timestamp}.log')
if not os.path.exists(os.path.dirname(os.path.abspath(__file__)) + '/logs'):
    os.makedirs(os.path.dirname(os.path.abspath(__file__)) + '/logs')

def log_write(msg: str) -> None:
    with open(log_dir, 'a', encoding='utf-8') as log:
        logtimestamp = time.strftime('%Y-%m-%d-%H-%M-%S')
        print(f'{logtimestamp}: {msg}')
        log.write(f'{logtimestamp}: {msg}\n')

if os.path.exists('changes.log'):
    os.remove('changes.log')
def change_write(msg: str) -> None:
    with open("changes.log", 'a', encoding='utf-8') as change_log:
        change_log.write(f'{msg}\n')

if os.path.exists('Update.log'):
    os.remove('Update.log')
def update_write(msg: str) -> None:
    with open("Update.log", 'a', encoding='utf-8') as update_log:
        update_log.write(f'{msg}\n')

log_write("Warning: This log file contains sensitive information, please keep it safe.\n")

# load config from secret.ini
secret = configparser.ConfigParser()
if not os.path.exists('secret.ini'):
    log_write('secret.ini not found')
    exit(1)
secret.read('secret.ini')

OPENAI_API_KEY = secret['Openai']['api_key']
OPENAI_API_URL = secret['Openai']['api_url']
model = secret['Openai']['model']
prompt_tokens_price = float(secret['Openai']['prompt_tokens_price'])
completion_tokens_price = float(secret['Openai']['completion_tokens_price'])
steam_username = secret['Steam']['username']
log_write('config loaded')
log_write(f'api_key length: {len(OPENAI_API_KEY)}')
log_write(f'model: {model}')
log_write(f'steam_username: {steam_username}')

prompt_tokens = 0
completion_tokens = 0

# load steamcmd order
current_dir = os.path.dirname(os.path.abspath(__file__))
order_file_path = os.path.join(current_dir, 'steamcmd', 'steamorder.txt')

# load steamcmd order
if os.path.exists(order_file_path):
    os.remove(order_file_path)

idlist = []
with open(order_file_path, 'w') as steamorder:
    steamorder.write(f'login {steam_username}\n')

    with open(os.path.join(current_dir, 'ids.txt'), 'r') as ids:
        for id in ids:
            steamorder.write(f'workshop_download_item 1062090 {id.strip()}\n')
            idlist.append(id.strip())
    steamorder.write('quit\n')
log_write('idlist loaded')
log_write(f'idlist: {idlist}')

subprocess.run(['steamcmd/steamcmd.exe', '+runscript', 'steamorder.txt'], cwd='steamcmd')

steam_workshop_dir = os.path.join(current_dir, 'steamcmd', 'steamapps', 'workshop', 'content', '1062090')

mod_dir = os.path.join(current_dir, 'mod')
if not os.path.exists(mod_dir):
    os.mkdir(mod_dir)
main_csv_path = os.path.join(mod_dir, 'Localizations', 'zhCN.csv')
raw_csv_dir = os.path.join(mod_dir,'data', 'enUS')
translated_dir = os.path.join(mod_dir,'data', 'zhCN')
temp_dir = os.path.join(current_dir, 'temp')
log_write('dir setup')
log_write(f'current_dir: {current_dir}')
log_write(f'mod_dir: {mod_dir}')
log_write(f'main_csv_path: {main_csv_path}')
log_write(f'raw_csv_dir: {raw_csv_dir}')
log_write(f'translated_dir: {translated_dir}')
log_write(f'temp_dir: {temp_dir}')

idlist.remove('3346918947')

if os.path.exists(os.path.join(current_dir, "Supports.txt")):
    os.remove(os.path.join(current_dir, "Supports.txt"))
if os.path.exists(mod_dir):
    shutil.rmtree(mod_dir)
shutil.move(os.path.join(steam_workshop_dir, '3346918947'), mod_dir)

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
shutil.copytree(os.path.join(mod_dir, 'Data'), temp_dir)
shutil.rmtree(os.path.join(mod_dir, 'Data', 'zhCN'))
os.mkdir(os.path.join(mod_dir, 'Data', 'zhCN'))

for id in idlist:
    if os.path.exists(os.path.join(steam_workshop_dir, id, 'Localizations', 'enUS.csv')):
        shutil.copy(os.path.join(steam_workshop_dir, id, 'Localizations', 'enUS.csv'), os.path.join(raw_csv_dir, f"{id}.csv"))
        log_write(f'FOUND: {id} enUS.csv found, copied to {id}.csv')
        continue
    if os.path.exists(os.path.join(steam_workshop_dir, id, 'Localizations', 'enUS.txt')):
        shutil.copy(os.path.join(steam_workshop_dir, id, 'Localizations', 'enUS.txt'), os.path.join(raw_csv_dir, f"{id}.csv"))
        log_write(f'FOUND: {id} enUS.txt found, copied to {id}.csv')
        continue
    # 尝试匹配文件，妈的就不能统一命名吗
    found_file = False
    # 遍历文件夹结构查找匹配的文件
    for root, dirs, files in os.walk(os.path.join(steam_workshop_dir, id)):
        for file in files:
            if "en" in file and (file.endswith('.csv') or file.endswith('.txt')):
                # 检查文件头部内容是否符合csv格式
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    firstline = f.readline().strip()
                    if 'ID,Text,Comment' in firstline:
                        shutil.copy(os.path.join(root, file), os.path.join(raw_csv_dir, f"{id}.csv"))
                        log_write(f'FOUND: {id} not exist class file, {file} matched, copied to {id}.csv')
                        found_file = True
                        break
        if found_file:
            break
        for file in files:
            #放宽条件至满足格式要求
            if file.endswith('.csv') or file.endswith('.txt'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    firstline = f.readline().strip()
                    if 'ID,Text,Comment' in firstline:
                        shutil.copy(os.path.join(root, file), os.path.join(raw_csv_dir, f"{id}.csv"))
                        log_write(f'FOUND: {id} not exist en file, {file} matched, copied to {id}.csv')
                        found_file = True
                        break
        if found_file:
            break
    if not found_file:
        log_write(f'ERROR: {id} enUS.csv not found, and no matching file found')

def openai_translate(text="Blank placeholder 1", description="Blank placeholder 2", model="gpt-4o-mini"):
    content = text + "||" + description

    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    # 构建请求体
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional, authentic machine translation engine. Translate text to Simplified Chinese, preserving structure, codes, and markup. Separate translations with ||."
            },
            {
                "role": "user",
                "content": content
            }
        ]
    }

    # 发送POST请求
    response = requests.post(OPENAI_API_URL, headers=headers, data=json.dumps(data))

    global prompt_tokens, completion_tokens
    response_data = response.json()
    if 'usage' in response_data:
        prompt_tokens += response_data['usage']['prompt_tokens']
        completion_tokens += response_data['usage']['completion_tokens']
    else:
        log_write('No usage data found')
    # 打印响应结果
    if response.status_code == 200:
        openai_result = response_data['choices'][0]['message']['content']
        log_write(f'{content} -> {openai_result}')
        return openai_result
    else:
        log_write(f"Request failed, status code: {response.status_code}")
        log_write(headers)
        log_write(data)
        log_write(response.text)
        return "Failed"

def parse_mod_info(file_path):
    mod_info = {}
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        for line in file:
            line = line.strip()
            if "\"Version\"" in line:
                mod_info['Version'] = line.split(':')[1].strip().strip('",')
            elif "\"Name\"" in line:
                mod_info['Name'] = line.split(':')[1].strip().strip('",')
    return mod_info

for id in idlist:
    # load mod info form manifest.json
    if os.path.exists(os.path.join(steam_workshop_dir, id, 'manifest.json')):
        info_file_path = os.path.join(steam_workshop_dir, id, 'manifest.json')
    elif os.path.exists(os.path.join(steam_workshop_dir, id, 'mod.json')):
        info_file_path = os.path.join(steam_workshop_dir, id, 'mod.json')
    log_write(f'{id} mod info file: {info_file_path}')
    mod_info = parse_mod_info(info_file_path)
    mod_version = mod_info.get('Version', 'Unknown')
    log_write(f'{id} mod version: {mod_version}')
    mod_name = mod_info.get('Name', 'Unknown').replace(' ', '_')
    log_write(f'{id} mod name: {mod_name}')
    with open(current_dir + '/Supports.txt', 'a', encoding='utf-8') as supports:
        supports.write(f'{mod_name} {mod_version}\n')

    # load raw csv
    raw_id_csv_path = os.path.join(raw_csv_dir, f"{id}.csv")
    with open(raw_id_csv_path, 'r', encoding='utf-8') as raw_file:
        raw = list(csv.reader(raw_file))

    # load old translated csv
    old_translated_path = os.path.join(temp_dir, 'zhCN', f"{id}.csv")
    if os.path.exists(old_translated_path):
        old_available = True
        with open(old_translated_path, 'r', encoding='utf-8') as old_translated_file:
            old_translated = list(csv.reader(old_translated_file))
            if old_translated[1][1] == mod_name and old_translated[1][2] == mod_version:
                log_write(f'{id} no change, skip')
                shutil.copy(old_translated_path, os.path.join(translated_dir, f"{id}.csv"))
                continue
            else:
                log_write(f'{id} changed, retranslate')
                change_write(f'{id} {mod_name}: {old_translated[1][2]} -> {mod_version}')
                update_write(f'{mod_name}: {old_translated[1][2]} -> {mod_version}')
    else:
        old_available = False

    # load old raw csv
    old_raw_csv_path = os.path.join(temp_dir, 'enUS', f"{id}.csv")
    with open(old_raw_csv_path, 'r', encoding='utf-8') as old_raw_file:
        old_raw = list(csv.reader(old_raw_file))

    # load new translated csv
    with open(os.path.join(translated_dir, f"{id}.csv"), 'w', newline='', encoding='utf-8') as csvfile:
        new_translated = csv.writer(csvfile)
        new_translated.writerow(['ID', 'Text', 'Comment'])
        new_translated.writerow([f'#workshop{id}', mod_name, mod_version])
        for row in raw:
            if len(row) < 2:
                continue
            if 'ID' in row[0]:
                continue
            raw_id = row[0]
            raw_text = row[1]
            if len(row) == 3:
                have_description = True
                raw_description = row[2]
            else:
                have_description = False
                raw_description = ""
            log_write(f'dealing with {id}: ID:{raw_id} Text:{raw_text} Comment:{raw_description} {have_description}')
            matched = False
            if old_available:
                for old_row in old_raw:
                    if 'ID' in old_row[0]:
                        continue
                    if len(old_row) < 2:
                        continue
                    if old_row[0] == raw_id:
                        if have_description and len(old_row) == 3 and old_row[1] == raw_text and old_row[2] == raw_description:
                            for old_translated_row in old_translated:
                                if old_translated_row[0] == raw_id:
                                    if len(old_translated_row) < 3:
                                        new_translated.writerow([raw_id, old_translated_row[1], ""])
                                        log_write(f'Matched translated found: {id} {raw_id} {raw_text} {raw_description} -> {old_translated_row[1]} NoComment')
                                    else:
                                        new_translated.writerow([raw_id, old_translated_row[1], old_translated_row[2]])
                                        log_write(f'Matched translated found: {id} {raw_id} {raw_text} {raw_description} -> {old_translated_row[1]} {old_translated_row[2]}')
                                    matched = True
                                    break
                        elif old_row[1] == raw_text:
                            for old_translated_row in old_translated:
                                if old_translated_row[0] == raw_id:
                                    new_translated.writerow([raw_id, old_translated_row[1], ""])
                                    log_write(f'Matched translated found: {id} {raw_id} {raw_text} -> {old_translated_row[1]} NoComment')
                                matched = True
                                break
                    if matched:
                        break
            if matched:
                continue
            openai_translate_result = openai_translate(raw_text, raw_description, model)
            if openai_translate_result == "Failed":
                log_write(f'ERROR: {id} {raw_id} {raw_text} {raw_description} translation failed')
                new_translated.writerow([raw_id, raw_text, raw_description])
            else:
                openai_translate_text = openai_translate_result.split('||')[0]
                if openai_translate_result.endswith('||'):
                    openai_translate_discription = ""
                else:
                    openai_translate_discription = openai_translate_result.split('||')[1]
                new_translated.writerow([raw_id, openai_translate_text, openai_translate_discription])
                log_write(f'OpenAI translate: {id} {raw_id} {raw_text} {raw_description} -> {openai_translate_text} {openai_translate_discription}')
                change_write(f'{id} {raw_id} {raw_text} {raw_description} -> {openai_translate_text} {openai_translate_discription}')
    log_write(f'{id} translation done')
log_write('All translation done')

# merge csv
log_write('Start merge csv')
if os.path.exists(main_csv_path):
    os.remove(main_csv_path)
with open(main_csv_path, 'w', newline='', encoding='utf-8') as main_csv:
    writer = csv.writer(main_csv)
    writer.writerow(['ID', 'Text', 'Comment'])
    for id in idlist:
        with open(os.path.join(translated_dir, f"{id}.csv"), 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            for row in reader:
                writer.writerow(row)
log_write('Merge csv done')

log_write(f'prompt_tokens_Usage: {prompt_tokens} completion_tokens_Usage: {completion_tokens}')
price = f"{prompt_tokens * prompt_tokens_price + completion_tokens * completion_tokens_price:.9f}"
log_write("Predict Cost " + price)
log_write('All done')
