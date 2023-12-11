import pymysql
import os
import urllib.request
import json

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
        self.con = pymysql.connect(host=conf['DB']['DBHOST'], user=conf['DB']['DBUSER'], \
                                   password=conf['DB']['DBPASSWD'], db=conf['DB']['DBNAME'], \
                                   cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()

    def get_badlys(self):
        sql = "SELECT timestamp,device,user FROM devices WHERE status = 1"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        numrows = self.cur.rowcount
        return result,numrows

    def lookdevice(self,mac):
        sql = "SELECT timestamp,device,user FROM devices WHERE device = %s"
        self.cur.execute(sql,mac)
        result = self.cur.fetchall()
        numrows = self.cur.rowcount
        return result,numrows

    def lookuser(self,user):
        sql = "SELECT timestamp,device,user FROM devices WHERE user = %s"
        self.cur.execute(sql,user)
        result = self.cur.fetchall()
        numrows = self.cur.rowcount
        return result,numrows

    def get_goodys(self):
        sql = "SELECT timestamp,device FROM devices WHERE status = 0 OR status = 2"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        numrows = self.cur.rowcount
        return result,numrows

    def get_all(self):
        sql = "SELECT device AS c FROM devices"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        numrows = self.cur.rowcount

        return numrows

def userbadlys():
    badlys,numbadys = eduroguedb.get_badlys()
    print("\nTimestamp \t\t\t Device \t User")
    print("-----------------------------------------------------------")
    for b in badlys:
        print(f"{b['timestamp']} \t {b['device']} \t {b['user']}")
    print("\n")

def lookdevice(mac):
    device,num = eduroguedb.lookdevice(mac)
    if num >= 1:
        print(f"\nDevice {mac} found {num} times")
        print("Timestamp \t\t\t Device \t User")
        print("-------------------------------------------------------------")
        for d in device:
            print(f"{d['timestamp']} \t {d['device']} \t {d['user']}")
        print("\n")

def stats():
    goodys,numgoodys = eduroguedb.get_goodys()
    badys,numbadys = eduroguedb.get_badlys()
    totaldevs = eduroguedb.get_all()
    percent_numgoodys = round((numgoodys/totaldevs)*100,1)
    percent_numbadlys = round((numbadys / totaldevs) * 100, 1)
    print(f"\nEdurogue stats\n----------------------")
    print(f"Badlys: {numbadys} ({percent_numbadlys}%)")
    print(f"Goodys: {numgoodys} ({percent_numgoodys}%)")
    print(f"Total Devices Tested: {totaldevs}\n")

def lookforuser(username):
    devices,numdevs = eduroguedb.lookuser(username)
    if numdevs >= 1:
        print(f"\nUser {username} found in {numdevs} devices")
        print("Timestamp \t\t\t Device \t User")
        print("-------------------------------------------------------------")
        for d in devices:
            print(f"{d['timestamp']} \t {d['device']} \t {d['user']}")
        print("\n")

def check_token(token):
    # If token has spaces is invalid
    if ' ' in token:
        print(f"------------------------------------------------------------")
        print(f"|Configured telegram bot token has spaces and is invalid.  |")
        print(f"|Edurogue will Log only to console.                        |")
        print(f"------------------------------------------------------------\n")
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
                return True
            else:
                print(f"--------------------------------------------")
                print(f"|Configured telegram bot token is invalid. |")
                print(f"|Edurogue will Log only to console.        |")
                print(f"--------------------------------------------\n")
                return False
    except urllib.error.URLError as e:
        print(f"An error occurred while checking the Telegram bot token: {e}")
        return False

def show_menu():
    print("1. Show BADLY devices")
    print("2. Look for user")
    print("3. Look for device")
    print("4. Show stats")
    print("5. Check Telegram token")
    print("6. Exit")

conf = read_config()
eduroguedb = Database()
def main():
    while True:
        show_menu()
        choice = input("Choose option (1-6): ")
        if choice == '1':
            print("Printing badly devices.")
            userbadlys()
        elif choice == '2':
            user = input("Enter username: ")
            lookforuser(user)
        elif choice == '3':
            mac = input("Enter device mac address: ")
            lookdevice(mac)
        elif choice == '4':
            print("Show Stats.")
            stats()
        elif choice == '5':
            print("\nCheck Telegram Token.")
            check_token(conf['TELEGRAM']['TOKEN'])
        elif choice == '6':
            print("Saliendo del programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, elige una opción válida.")

        #input("Presiona Enter para volver al menú.")

if __name__ == "__main__":
    main()
