import pymysql
import os
import urllib.request
import urllib.error
import json
import time

def read_config():
    conf = {
        'EDUROGUE': {
            'WIFIDEVMON': os.environ["WIFI_DEV"],
            'TTL_TO_RETEST': os.environ["TTL_TO_RETEST"],
            'MAX_RETRIES': os.environ["MAX_RETRIES"],
            'ANONIMIZE': os.environ["ANONIMIZE"],
            'RESET_ON_INIT': os.environ["RESET_ON_INIT"]
        },
        'DB': {
            'DBHOST': 'localhost',
            'DBUSER': os.environ["MYSQL_USER"],
            'DBPASSWD': os.environ["MYSQL_PASSWORD"],
            'DBNAME': os.environ["MYSQL_DATABASE"]
        },
        'TELEGRAM': {
            'TOKEN': os.environ["TELEGRAM_TOKEN"],
            'CHATBOTID': os.environ["TELEGRAM_CHAT_LOG_ID"],
            'CHATBOTLOGID': os.environ["TELEGRAM_CHAT_DEBUG_ID"]
        }
    }
    return conf

class Database:
    def __init__(self):
        self.con = pymysql.connect(host=conf['DB']['DBHOST'], user=conf['DB']['DBUSER'],
                                   password=conf['DB']['DBPASSWD'], db=conf['DB']['DBNAME'],
                                   cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()

    def get_badlys(self):
        sql = "SELECT timestamp,device,user,status FROM devices WHERE status = 1"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        numrows = self.cur.rowcount
        return result,numrows

    def lookdevice(self,mac):
        sql = "SELECT timestamp,device,user,status FROM devices WHERE device = %s"
        self.cur.execute(sql,mac)
        result = self.cur.fetchall()
        numrows = self.cur.rowcount
        return result,numrows

    def lookuser(self,user):
        sql = "SELECT timestamp,device,user,status FROM devices WHERE user = %s"
        self.cur.execute(sql,user)
        result = self.cur.fetchall()
        numrows = self.cur.rowcount
        return result,numrows

    def get_goodys(self):
        sql = "SELECT timestamp,device,user,status FROM devices WHERE status = 0 OR status = 2"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        numrows = self.cur.rowcount
        return result,numrows

    def get_all(self):
        sql = "SELECT timestamp,device,user,status FROM devices"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        numrows = self.cur.rowcount
        return result,numrows

    def get_last(self,num):
        sql = "SELECT timestamp,device,user,status FROM devices ORDER BY timestamp DESC LIMIT %s"
        self.cur.execute(sql,int(num))
        result = self.cur.fetchall()
        numrows = self.cur.rowcount
        return result,numrows

def printstatus(num):
    if num == 0:
        return "GOODY"
    elif num == 1:
        return "BADLY"
    elif num == 2:
        return "~GOODY"
    elif num == 4:
        return "BADLY"
    elif num == 5:
        return "GOODY"

def userbadlys():
    badlys,numbadys = eduroguedb.get_badlys()
    printdevtable(badlys)

def lookdevice(mac):
    device,num = eduroguedb.lookdevice(mac)
    if num >= 1:
        print(f"\nDevice {mac} found {num} times")
        printdevtable(device)
    else:
        print(f"\nDevice {mac} not found.")
        print("\n")
        input(f"{bcolors.WARNING}Press Enter to return to the Main Menu.{bcolors.ENDC}")

def listall():
    devices,num = eduroguedb.get_all()
    if num >= 1:
        print(f"\nList of tested devices.")
        printdevtable(devices)
    else:
        print(f"\nDevice list is empty.")
        print("\n")
        input(f"{bcolors.WARNING}Press Enter to return to the Main Menu.{bcolors.ENDC}")

def listlast(num):
    if str(num).isdigit() == False:
        print(f"El valor debe ser un numero entero")
        time.sleep(2)
        return False
    devices,num = eduroguedb.get_last(num)
    if num >= 1:
        print(f"\nList of last {num} tested devices.")
        printdevtable(devices)
    else:
        print(f"\nDevice list is empty.")
        print("\n")
        input(f"{bcolors.WARNING}Press Enter to return to the Main Menu.{bcolors.ENDC}")

def stats():
    goodys,numgoodys = eduroguedb.get_goodys()
    badys,numbadys = eduroguedb.get_badlys()
    devices,totaldevs = eduroguedb.get_all()
    percent_numgoodys = round((numgoodys/totaldevs)*100,1)
    percent_numbadlys = round((numbadys / totaldevs) * 100, 1)
    print(f"\nEdurogue stats\n----------------------")
    print(f"Badlys: {numbadys} ({percent_numbadlys}%)")
    print(f"Goodys: {numgoodys} ({percent_numgoodys}%)")
    print(f"Total Devices Tested: {totaldevs}\n")
    print("\n")
    input(f"{bcolors.WARNING}Press Enter to return to the Main Menu.{bcolors.ENDC}")

def printdevtable(devices):
    print("Timestamp \t\tStatus \t Device \t\t User")
    print("---------------------------------------------------------------------------")
    for d in devices:
        status = printstatus(d['status'])
        print(f"{d['timestamp']}\t{status} \t {d['device']} \t {d['user']}")
    print("\n")
    input(f"{bcolors.WARNING}Press Enter to return to the Main Menu.{bcolors.ENDC}")

def lookforuser(username):
    devices,numdevs = eduroguedb.lookuser(username)
    if numdevs >= 1:
        print(f"\nUser {username} found in {numdevs} devices")
        printdevtable(devices)
    else:
        print(f"\nUser {username} not found.")
        print("\n")
        input(f"{bcolors.WARNING}Press Enter to return to the Main Menu.{bcolors.ENDC}")

def check_token(token):
    # If token has spaces is invalid
    if ' ' in token:
        print(f"------------------------------------------------------------")
        print(f"|{bcolors.FAIL}Configured telegram bot token has spaces and is invalid.{bcolors.ENDC}  |")
        print(f"|{bcolors.FAIL}Edurogue will Log only to console.{bcolors.ENDC}                        |")
        print(f"------------------------------------------------------------\n")
        print("\n")
        input(f"{bcolors.WARNING}Press Enter to return to the Main Menu.{bcolors.ENDC}")
        return False
    # URL for verify Telegram token bot
    api_url = f'https://api.telegram.org/bot{token}/getMe'
    try:
        # Request
        with urllib.request.urlopen(api_url) as response:
            data = json.load(response)
            # Verify if request is ok or not
            if data.get("ok", False) and data.get("result"):
                print(f"--------------------------------------------")
                print(f"|Telegram bot token is valid.              |")
                print(f"|Edurogue will log to Telegram and console.|")
                print(f"--------------------------------------------\n")
                print("\n")
                input(f"{bcolors.WARNING}Press Enter to return to the Main Menu.{bcolors.ENDC}")
                return True
            else:
                print(f"--------------------------------------------")
                print(f"|{bcolors.FAIL}Configured telegram bot token is invalid. {bcolors.ENDC}|")
                print(f"|{bcolors.FAIL}Edurogue will Log only to console. {bcolors.ENDC}       |")
                print(f"--------------------------------------------\n")
                print("\n")
                input(f"{bcolors.WARNING}Press Enter to return to the Main Menu.{bcolors.ENDC}")
                return False
    except urllib.error.URLError as e:
        print(f"An error occurred while checking the Telegram bot token: {e}")
        return False

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def show_menu():
    print(f"{bcolors.HEADER}Edurogue Main Menu")
    print(f"{bcolors.OKGREEN}1. List BADLY devices")
    print(f"2. Look for user")
    print(f"3. Look for device")
    print(f"4. List last N tested devices")
    print(f"5. List all tested devices")
    print(f"6. Show general stats")
    print(f"7. Check Telegram token")
    print(f"\n")
    print(f"{bcolors.WARNING}0. Exit{bcolors.ENDC}")

conf = read_config()
eduroguedb = Database()
def main():
    while True:
        os.system("clear")
        show_menu()
        choice = input("Choose option (1-7): ")
        if choice == '1':
            userbadlys()
        elif choice == '2':
            user = input("Enter username: ")
            lookforuser(user)
        elif choice == '3':
            mac = input("Enter device mac address: ")
            lookdevice(mac)
        elif choice == ('4'):
            num = input("Number of devices to list:")
            listlast(num)
        elif choice == '5':
            listall()
        elif choice == '6':
            stats()
        elif choice == '7':
            check_token(conf['TELEGRAM']['TOKEN'])
        elif choice == '0':
            print("Exiting from Edurogue Management. See you later!")
            break
        else:
            print(f"{bcolors.FAIL}Invalid option. Please choose a valid one.{bcolors.ENDC}")
            time.sleep(2)

        #input("Presiona Enter para volver al menú.")

if __name__ == "__main__":
    main()
