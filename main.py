import openai
import configparser
import os
import subprocess
import shutil
import hashlib
import csv
import time

timestamp = time.strftime('%Y-%m-%d-%H-%M-%S')
log = open(f'{timestamp}.log', 'w', encoding='utf-8')
def log_write(msg: str) -> None:
    logtimestamp = time.strftime('%Y-%m-%d-%H-%M-%S')
    print(f'{logtimestamp}: {msg}')
    log.write(f'{logtimestamp}: {msg}\n')

log_write("Warning: This log file contains sensitive information, please keep it safe.\n")

# load config from secret.ini
secret = configparser.ConfigParser()
if not os.path.exists('secret.ini'):
    log_write('secret.ini not found')
    log.close()
    exit(1)
secret.read('secret.ini')

openai.api_key = secret['Openai']['api_key']
steam_username = secret['Steam']['username']
log_write('config loaded')
log_write(f'api_key length: {len(openai.api_key)}')
log_write(f'steam_username: {steam_username}')

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
if os.path.exists(mod_dir):
    shutil.rmtree(mod_dir)
shutil.move(os.path.join(steam_workshop_dir, '3346918947'), mod_dir)

for id in idlist:
    if not os.path.exists(os.path.join(steam_workshop_dir, id, 'Localizations')):
        log_write(f'ERROR: {id} Localizations dir not found')
        continue
    if os.path.exists(os.path.join(steam_workshop_dir, id, 'Localizations', 'enUS.csv')):
        shutil.copy(os.path.join(steam_workshop_dir, id, 'Localizations', 'enUS.csv'), os.path.join(raw_csv_dir, f"{id}.csv"))
        log_write(f'FOUND: {id} enUS.csv found, copied to {id}.csv')
        continue
    if os.path.exists(os.path.join(steam_workshop_dir, id, 'Localizations', 'enUS.txt')):
        shutil.copy(os.path.join(steam_workshop_dir, id, 'Localizations', 'enUS.txt'), os.path.join(raw_csv_dir, f"{id}.csv"))
        log_write(f'FOUND: {id} enUS.txt found, copied to {id}.csv')
        continue
    # 尝试匹配以en开头的文件，妈的就不能统一命名吗
    for file in os.listdir(os.path.join(steam_workshop_dir, id, 'Localizations')):
        if "en" in file and (file.endswith('.csv') or file.endswith('.txt')):
            # 尝试检查文件头部是否是csv
            with open(os.path.join(steam_workshop_dir, id, 'Localizations', file), 'r', encoding='utf-8') as f:
                firstline = f.readline().strip()
                log_write(f'Debug: CSV style match Test {id} {file} firstline: {firstline}')
                if 'ID,' in firstline:
                    shutil.copy(os.path.join(steam_workshop_dir, id, 'Localizations', file), os.path.join(raw_csv_dir, f"{id}.csv"))
                    log_write(f'FOUND: {id} not exist class file, {file} matched, copied to {id}.csv')
                    break
    else:
        log_write(f'ERROR: {id} enUS.csv not found, and no matching file found')



log.close()