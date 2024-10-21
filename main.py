import openai
import configparser
import os
import subprocess

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

