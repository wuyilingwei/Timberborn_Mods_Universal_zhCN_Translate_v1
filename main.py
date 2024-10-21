import openai
import configparser
import os
import subprocess
import shutil
import hashlib

# load config from secret.ini
secret = configparser.ConfigParser()
secret.read('secret.ini')

openai.api_key = secret['Openai']['api_key']
steam_username = secret['Steam']['username']

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

subprocess.run(['steamcmd/steamcmd.exe', '+runscript', 'steamorder.txt'], cwd='steamcmd')

steam_workshop_dir = os.path.join(current_dir, 'steamcmd', 'steamapps', 'workshop', 'content', '1062090')

data_dir = os.path.join(current_dir, 'data')
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
translated_dir = os.path.join(data_dir, 'mods')
temp_dir = os.path.join(data_dir, 'temp')
if os.path.exists(temp_dir):
    is_temp_available = True
last_dir = os.path.join(data_dir, 'last')

idlist.remove('3346918947')
if os.path.exists(translated_dir):
    shutil.rmtree(translated_dir)
    shutil.move(os.path.join(steam_workshop_dir, '3346918947'), translated_dir)

exist_csv = open(os.path.join(translated_dir, 'Localizations', 'zhCN.csv'), 'r')

for id in idlist:
    shutil.move(os.path.join(steam_workshop_dir, id, 'Localizations', 'enUS.csv'), os.path.join(temp_dir, id, 'enUS.csv'))