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
log.write("Warning: This log file contains sensitive information, please keep it safe.\n")

# load config from secret.ini
secret = configparser.ConfigParser()
if not os.path.exists('secret.ini'):
    log.write('secret.ini not found\n')
    exit(1)
secret.read('secret.ini')

openai.api_key = secret['Openai']['api_key']
steam_username = secret['Steam']['username']
log.write('config loaded\n')
log.write(f'api_key length: {len(openai.api_key)}\n')
log.write(f'steam_username: {steam_username}\n')

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
log.write('idlist loaded\n')
log.write(f'idlist: {idlist}\n')

subprocess.run(['steamcmd/steamcmd.exe', '+runscript', 'steamorder.txt'], cwd='steamcmd')

steam_workshop_dir = os.path.join(current_dir, 'steamcmd', 'steamapps', 'workshop', 'content', '1062090')

data_dir = os.path.join(current_dir, 'data')
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
translated_dir = os.path.join(data_dir, 'mod')
temp_dir = os.path.join(data_dir, 'temp')
if os.path.exists(temp_dir):
    is_temp_available = True
else:
    is_temp_available = False
    os.mkdir(temp_dir)
last_dir = os.path.join(data_dir, 'last')
log.write('dir setup\n')
log.write(f'translated_dir: {translated_dir}\n')
log.write(f'temp_dir: {temp_dir}\n')
log.write(f'last_dir: {last_dir}\n')

idlist.remove('3346918947')
if os.path.exists(translated_dir):
    shutil.rmtree(translated_dir)
shutil.move(os.path.join(steam_workshop_dir, '3346918947'), translated_dir)

exist_csv = open(os.path.join(translated_dir, 'Localizations', 'zhCN.csv'), 'r')
csv_edit = csv.reader(exist_csv)

for id in idlist:
    shutil.move(os.path.join(steam_workshop_dir, id, 'Localizations', 'enUS.csv'), os.path.join(temp_dir, f"{id}.csv"))