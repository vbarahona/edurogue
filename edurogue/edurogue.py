import os
import subprocess
import signal
import psutil
import pymysql
import time
import urllib.request
import logging
import socket
from urllib.error import HTTPError, URLError
from socket import timeout

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
    print(conf)
    return conf

class Database:
    def __init__(self):
        self.con = pymysql.connect(host=conf['DB']['DBHOST'], user=conf['DB']['DBUSER'], \
                                   password=conf['DB']['DBPASSWD'], db=conf['DB']['DBNAME'], \
                                   cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()

    def reset_on_init(self):
        try:
            self.cur.execute("TRUNCATE devices")
            self.cur.execute("TRUNCATE temp")
            self.con.commit()
            logger.warning("Reseting device table on init for testing purposes.")
            logger.warning("If not expected change RESET_ON_INIT to 0 in config.")
            telegram_log_message(f"WARN: reseting device table on init for devel.")
        except pymysql.Error as e:
            logger.error("Could not reset device table because: %s", str(e))


    def insert_dev_bad(self, dev, user):
        try:
            insert = self.cur.execute("INSERT devices SET device = %s , user = %s, status = 1", (dev, user))
            self.con.commit()
            if insert > 0:
                logger.debug("Device %s inserted in table devices as BADLY (status 1) for user %s", dev, user)
        except pymysql.Error as e:
            logger.error("Could not insert device because: %s", str(e))

    def insert_dev_bad_unnoticed(self, dev, user):
        try:
            insert = self.cur.execute("INSERT devices SET device = %s , user = %s, status = 4", (dev, user))
            self.con.commit()
            if insert > 0:
                logger.debug("Device %s inserted in table devices as BADLY but Un-noticed (status 4) for user %s", dev, user)
        except pymysql.Error as e:
            logger.error("Could not insert device because: %s", str(e))

    def insert_dev_good_unnoticed(self, dev):
        try:
            insert = self.cur.execute("INSERT devices SET device = %s , status = 5", dev)
            self.con.commit()
            if insert > 0:
                logger.debug("Device %s inserted in devices table as GOODY but Un-noticed (status 5)", dev)
        except pymysql.Error as e:
            logger.error("Could not insert device because: %s", str(e))

    def change_unnoticed_to_noticed(self, dev, newstatus):
        sql = "UPDATE devices SET status = %s WHERE device = %s"
        self.cur.execute(sql, (newstatus, dev))
        self.con.commit()

    def insert_dev_ok(self, dev):
        try:
            insert = self.cur.execute("INSERT devices SET device = %s , status = 0", dev)
            self.con.commit()
            if insert > 0:
                logger.debug("Device %s inserted in table devices as GOODY (status 0)", dev)
        except pymysql.Error as e:
            logger.error("Could not insert device because: %s", str(e))

    def insert_dev_unknown(self, dev):
        try:
            insert = self.cur.execute("INSERT devices SET device = %s , status = 2", dev)
            self.con.commit()
            if insert > 0:
                logger.debug("Device %s inserted in table devices as pobable GOODY (status 2)", dev)
        except pymysql.Error as e:
            logger.error("Could not insert device because: %s", str(e))

    def insert_testing_dev(self, dev):
        try:
            insert = self.cur.execute("INSERT temp SET device = %s", dev)
            self.con.commit()
            if insert > 0:
                logger.debug("Device %s inserted in table temp as testing device", dev)
        except pymysql.Error as e:
            logger.error("Could not insert device because: %s", str(e))

    def log_bad_dev(self, dev, user):
        try:
            insert = self.cur.execute("INSERT log SET device = %s , user = %s", (dev, user))
            self.con.commit()
            if insert > 0:
                logger.debug("Device %s inserted in table log as BADLY for user %s", dev, user)
        except pymysql.Error as e:
            logger.error("Could not insert device because: %s", str(e))

    def check_testing_dev(self, dev):
        sql = "SELECT count(device) AS d FROM temp WHERE device = %s "
        self.cur.execute(sql, dev)
        result = self.cur.fetchall()[0]['d']
        return result

    def check_dev(self, dev):
        sql = "SELECT count(device) AS d FROM devices WHERE device = %s "
        self.cur.execute(sql, dev)
        result = self.cur.fetchall()[0]['d']
        return result

    def clean_testing_dev(self, dev):
        try:
            self.cur.execute("DELETE FROM temp WHERE device = %s", dev)
            self.con.commit()
            logger.debug("Deleted testing device %s from table temp", dev)
        except pymysql.Error as e:
            logger.error("Could not delete testing device because: %s", str(e))

    def get_devs(self):
        sql = "SELECT device FROM devices"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

    def get_devs_pending(self):
        sql = "SELECT user,device,status FROM devices WHERE status = 4 OR status = 5"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

    def get_expired_devs(self):
        sql = "SELECT device,user FROM devices WHERE " \
              "status = 1 AND " \
              "timestamp <= (DATE(NOW()) - INTERVAL " + str(conf['EDUROGUE']['TTL_TO_RETEST']) + " DAY)"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

    def delete_dev(self, dev):
        self.cur.execute("DELETE FROM devices WHERE device = %s", dev)
        self.con.commit()
        result = self.cur.fetchall()
        return result

def get_pid(name):
    for proc in psutil.process_iter():
        if proc.name() == name and proc.status() != 'zombie':
            return proc.pid
    logger.warning('%s is not running.', name)
    return 0

def anon_user(user):
    if conf['EDUROGUE']['ANONIMIZE'] == "1":
        # split email in username and domain
        username, domain = user.split('@')
        # Hide the username with asterisks
        hidden_username = username[:2] + '*'*(len(username)-4) + username[-2:]
        return hidden_username + '@' + domain
    elif conf['EDUROGUE']['ANONIMIZE'] == "0":
        return user

def wl_dev():
    with open('/etc/hostapd-wpe/hostapd.deny', 'w') as wl:
        #wl = open('/etc/hostapd-wpe/hostapd.deny', 'w')
        devices = eduroguedb.get_devs()
        logger.debug('Re-creating hostapd.deny')
        for d in devices:
            wl.write(d['device'])
            wl.write("\n")
            #logger.debug('%s added', d['device'])
        wl.flush()
        pid = get_pid("hostapd-wpe")
        if pid != 0:
            os.kill(pid, signal.SIGHUP)
            logger.debug('SIGHUP hostapd-wpe (%s)', pid)
            logger.debug("Reloading hostapd-wpe config")
            return 1
        else:
            up_hostapd_wpe(conf['EDUROGUE']['WIFIDEVMON'])

def expire_devs():
    expired_devs = eduroguedb.get_expired_devs()
    for d in expired_devs:
        eduroguedb.delete_dev(d['device'])
        logger.info('%s - %s: unlisted for re-testing', d['user'], d['device'])
        telegram_log_message(f"{d['user']} - {d['device']}: unlisted for re-testing")

def telegram_log_message(log):
    msg = log.replace(" ", "+")
    url = 'https://api.telegram.org/bot'+conf['TELEGRAM']['TOKEN']+'/sendMessage?chat_id='+conf['TELEGRAM']['CHATBOTLOGID']+'&text=' + msg
    try:
        if check_name_resolution("api.telegram.org", 443) == 0:
            urllib.request.urlopen(url, timeout=5)
                #data = resp.read()
    except (HTTPError, URLError) as error:
        logger.warning('Error because %s\nURL: %s', error, url)
    except timeout:
        logger.warning('socket timed out - URL %s', url)
    else:
        return

def telegram_message(device, user, status):
    msg = "msg"
    if status == "BADLY":
        badly = str(anon_user(user))
        msg = "BADLY:+" + badly + "+->+" + device
    elif status == "GOODY":
        msg = "GOODY:+" + device
    elif status == "PROB":
        msg = "~GOODY" + device
    url = 'https://api.telegram.org/bot' + conf['TELEGRAM']['TOKEN'] + '/sendMessage?chat_id=' + conf['TELEGRAM']['CHATBOTID'] + '&text=' + msg
    try:
        if check_name_resolution("api.telegram.org", 443) == 0:
            resp = urllib.request.urlopen(url, timeout=5)
#           data = resp.read()
    except (HTTPError, URLError) as error:
        logger.warning('Error because %s\nURL: %s', error, url)
    except timeout:
        logger.warning('socket timed out - URL %s', url)
    else:
        return

def check_name_resolution(host, port):
    dns = 0
    try:
        socket.getaddrinfo(host, port)
    except socket.gaierror as e:
        if e.errno == socket.EAI_AGAIN:
            logger.warning("Temporary failure in name resolution")
            dns = 1
        else:
            raise
    return dns

def notify_pending():
    if check_name_resolution("api.telegram.org", 443) == 0:
        pend = eduroguedb.get_devs_pending()
        for p in pend:
            if p['status'] == 4:
                eduroguedb.change_unnoticed_to_noticed(p['device'], 1)
                logger.info('BADLY: %s -> %s (whitelisted) (deferred msg)', p['device'], p['user'])
                telegram_log_message(f"BADLY: {p['device']} -> {p['user']} (whitelisted) (deferred msg)")
            elif p['status'] == 5:
                eduroguedb.change_unnoticed_to_noticed(p['device'], 0)
                logger.info('GOODY: %s (whitelisted) (deferred msg)', p['device'], p['user'])
                telegram_log_message(f"GOODY: {p['device']} (whitelisted) (deferred msg)")
    else:
        logger.warning("Temporary failure in name resolution")
        return

def init_edurogue_info():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    host = socket.gethostname()
    logger.info("Starting Edurogue")
    telegram_log_message("-----Starting Edurogue-----")
    telegram_log_message(f"-->   Host: {host}   ")
    telegram_log_message(f"-->   Public IP: {ip}")

def config_hostapd_wpe(interface):
    with open('/etc/hostapd-wpe/hostapd-wpe.conf', 'r') as config_file:
        lines = config_file.readlines()

    with open('/etc/hostapd-wpe/hostapd-wpe.conf', 'w') as config_file:
        for line in lines:
            if "#interface=wlan0" in line:
                # Si la línea contiene el patrón, la reemplazamos con el nuevo string
                new_line = line.replace("#interface=wlan0", "interface=" + interface)
                config_file.write(new_line)
            else:
                config_file.write(line)

def up_hostapd_wpe(interface):
    # Create hostapd.deny
    wl = open('/etc/hostapd-wpe/hostapd.deny', 'w')
    wl.close()
    # Check if hostapd-wpe is running.
    pid = get_pid("hostapd-wpe")
    attempt = 0
    while pid == 0:
        # Kill any other hostapd-wpe instance
        #os.system("pkill -2 hostapd-wpe")
        attempt += 1
        logger.info("Starting hostsapd-wpe (%s/3)", attempt)
        telegram_log_message(f"Starting hostsapd-wpe ({attempt}/3)")
        # Run hostapd-wpe
        os.system("hostapd-wpe -s /etc/hostapd-wpe/hostapd-wpe.conf > /opt/edurogue/log/edurogue.log &")
        # Wait some time for errors in running hostapd-wpe
        time.sleep(5)
        # Check if hostapd-wpe is running.
        pid = get_pid("hostapd-wpe")
        if attempt == 3:
            logger.error("ERROR: hostapd-wpe can't run. Check logs for errors. Exiting!")
            telegram_log_message("ERROR: hostapd-wpe can't run. Check logs for errors. Exiting!")
            exit()
    # Create list of devices already tested
    wl_dev()
    # Expire devices in black list to be reevaluated
    expire_devs()
    return pid

def check_wifi_interface(interface):
    try:
        # Run the iwconfig command and get the output
        output = subprocess.check_output(["iwconfig"], stderr=subprocess.STDOUT, text=True)

        # If the output contains information about the interface, then it exists
        if interface in output:
            telegram_log_message(f"Starting in '{interface}' interface.")
            return True
        else:
            telegram_log_message(f"ERROR: The WiFi interface '{interface}' doesn't exist in the system.")

            # Print available WiFi interfaces
            telegram_log_message("Available WiFi interfaces:")
            try:
                output = subprocess.check_output(["iwconfig"], stderr=subprocess.STDOUT, text=True)
                available_interfaces_list = [line.split()[0] for line in output.splitlines() if line.strip()if "IEEE 802.11" in line]
                available_interfaces = ', '.join(available_interfaces_list)
                telegram_log_message(available_interfaces)
                telegram_log_message("Adapt you docker-compose.yml to include one of the list and recreate containers again.")
                telegram_log_message("Exiting!!")
                exit()
            except subprocess.CalledProcessError:
                telegram_log_message("Couldn't retrieve the list of available WiFi interfaces. Exiting!!")
                exit()
    except subprocess.CalledProcessError as e:
        # If there's an error, the interface doesn't exist.
        telegram_log_message(f"ERROR: Couldn't retrieve the list of available WiFi interfaces. Exiting!!")
        exit()

def init_log_console():
    # Establecer el nivel de logging a DEBUG
    logger = logging.getLogger("edurogue")
    logger.setLevel(logging.DEBUG)
    # Crear un handler para enviar los mensajes a la consola
    console_handler = logging.StreamHandler()
    # Crear un formatter para dar formato a los mensajes
    console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # Asignar el formatter al handler
    console_handler.setFormatter(console_formatter)
    # Añadir el handler al logger
    logger.addHandler(console_handler)
    return logger

# Global vars. Don't touch if don't know what are you doing
bad_user = "user"

# Read conf
conf = read_config()
# Init logging
logger = init_log_console()
# Init DB link
eduroguedb = Database()

def main():
    # Check if reset of device table needs to be reset. Just for devel
    if conf['EDUROGUE']['RESET_ON_INIT'] == "1":
        eduroguedb.reset_on_init()
    # Notice edurogue init
    init_edurogue_info()
    # Check if interface exists
    check_wifi_interface(conf['EDUROGUE']['WIFIDEVMON'])
    # Adds interface in hostapd-wpe config file
    config_hostapd_wpe(conf['EDUROGUE']['WIFIDEVMON'])
    # Runs hostapd-wpe
    up_hostapd_wpe(conf['EDUROGUE']['WIFIDEVMON'])
    # Open hostapd-wpe logs to parse output
    with open('/opt/edurogue/log/edurogue.log', 'r') as logs:
        telegram_log_message(f"-----Edurogue running-----")
        # Parse logs
        while True:
            loglines = logs.readline()
            if loglines.find('EAP-STARTED') >= 0:
                testing_dev = loglines.split(' ')[2].strip()
                eduroguedb.insert_testing_dev(testing_dev)
                num_tests = eduroguedb.check_testing_dev(testing_dev)
                logger.info("Testing %s (%s/%s)", testing_dev, num_tests, conf['EDUROGUE']['MAX_RETRIES'])
                telegram_log_message(f"Testing {testing_dev} ({num_tests}/{conf['EDUROGUE']['MAX_RETRIES']})")
                if eduroguedb.check_testing_dev(testing_dev) >= int(conf['EDUROGUE']['MAX_RETRIES']):
                    eduroguedb.clean_testing_dev(testing_dev)
                    eduroguedb.insert_dev_unknown(testing_dev)
                    wl_dev()
                    logger.info("Alcanzado limite de intentos (%s). Probablemente GOODY: %s (whitelisted)", conf['EDUROGUE']['MAX_RETRIES'], testing_dev)
                    telegram_log_message(f"Alcanzado limite de intentos ({conf['EDUROGUE']['MAX_RETRIES']}). Probablemente GOODY: {testing_dev} (whitelisted)")
                    telegram_message(testing_dev, "NA", "PROB")
            if loglines.find('username') >= 0:
                bad_user = anon_user(loglines.split('\t')[2].strip())
                logger.info("Testing %s with device %s", bad_user, testing_dev)
                telegram_log_message(f"Testing {bad_user} with device {testing_dev}")
            if loglines.find('EAP-SUCCESS') >= 0:
                bad_device = loglines.split(' ')[2].strip()
                if eduroguedb.check_dev(bad_device) == 0:
                    if check_name_resolution("api.telegram.org", 443) == 0:
                        logger.info("BADLY: %s -> %s (whitelisted)", bad_user, bad_device)
                        telegram_log_message(f"BADLY: {bad_user} -> {bad_device} (whitelisted)")
                        telegram_message(bad_device, bad_user, "BADLY")
                        eduroguedb.insert_dev_bad(bad_device, bad_user)
                    else:
                        eduroguedb.insert_dev_bad_unnoticed(bad_device, bad_user)
                    eduroguedb.clean_testing_dev(bad_device)
                    eduroguedb.log_bad_dev(bad_device, bad_user)
                    expire_devs()
                    wl_dev()
                else:
                    logger.warning('BADLY Device %s -> %s already exists in DB', bad_user, bad_device)
                    telegram_log_message(f"WARNING: BADLY Device {bad_user} -> {bad_device} already exists in DB")
            if loglines.find('EAP-FAILURE') >= 0:
                good_device = loglines.split(' ')[2].strip()
                if eduroguedb.check_dev(good_device) == 0:
                    if check_name_resolution("api.telegram.org", 443) == 0:
                        eduroguedb.insert_dev_ok(good_device)
                        logger.info("GOODY: %s (whitelisted)", good_device)
                        telegram_log_message(f"GOODY: {good_device} (whitelisted)")
                        telegram_message(good_device, "NA", "GOODY")
                    else:
                        eduroguedb.insert_dev_good_unnoticed(good_device)
                        eduroguedb.clean_testing_dev(good_device)
                    expire_devs()
                    wl_dev()
                else:
                    logger.warning('GOODY Device %s already exists in DB', good_device)
            if len(loglines) == 0:
                time.sleep(5)
                notify_pending()


if __name__ == '__main__': main()
