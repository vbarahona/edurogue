from telegram.ext import (Updater, CommandHandler)
import pymysql
import logging
from functools import wraps

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# DB stuff
dbhost = 'localhost'
dbuser = 'edurogue'
dbpasswd = 'trons'
db = 'edurogue'

# Admins list
LIST_OF_ADMINS = [8070225,6521125017]

def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped

class Database:
    def __init__(self):
        self.con = pymysql.connect(host=dbhost, user=dbuser, password=dbpasswd, db=db, cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()

    def get_badys(self):
        sql = "SELECT timestamp,device,user FROM devices WHERE status = 1"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        numrows = self.cur.rowcount

        return result,numrows

    def get_goodys(self):
        sql = "SELECT timestamp,device FROM devices WHERE status = 0 OR status = 2"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        numrows = self.cur.rowcount

        return result,numrows

    def get_historical_badys(self):
        sql = "SELECT timestamp,device,user FROM log"
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

@restricted
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

@restricted
def help(update, context):
    """Send a message when the command /help is issued."""
    help ="Edurogue help. Commands supported:\n" \
          "/start - Welcome message.\n" \
          "/help - Show this help.\n" \
          "/numbadys_all_time - Show the number of Badys from ever\n" \
          "/numbadys - Show the number of Badys in actual TtT.\n" \
          "/numgoodys - Show the number of Goodys in actual TtT.\n" \
          "/stats - Show complete stats.\n\n" \
          "Glossary:\n" \
          "\t- Bady - device NOT checking the radius certificate signature. Exposed to be cheated by a MitM attack.\n" \
          "\t- Goody - device checking the radius certificate signature. They are secure.\n" \
          "\t- TtT - 'Time to Test' period of time to wait for retest a Bady (7d) or a Goody (90d)."
    context.bot.send_message(chat_id=update.message.chat_id, text=help)

@restricted
def numbadys(update, context):
    badys,numbadys = eduroguedb.get_badys()
    totaldevs = eduroguedb.get_all()
    percent = round((numbadys/totaldevs)*100,1)
    msg = f"The number of Badys is: {str(numbadys)}/{str(totaldevs)} ({percent}%)"
    context.bot.send_message(chat_id=update.message.chat_id, text=msg)

@restricted
def numbadys_all_time(update, context):
    badys,numbadys = eduroguedb.get_historical_badys()
    msg = f"The number of Badys is: {str(numbadys)}"
    context.bot.send_message(chat_id=update.message.chat_id, text=msg)

@restricted
def numgoodys(update, context):
    goodys,numgoodys = eduroguedb.get_goodys()
    totaldevs = eduroguedb.get_all()
    percent = round((numgoodys/totaldevs)*100,1)
    msg = f"The number of Goodys is: {str(numgoodys)}/{str(totaldevs)} ({percent}%)"
    context.bot.send_message(chat_id=update.message.chat_id, text=msg)

@restricted
def userbadys(update, context):
    badys,numbadys = eduroguedb.get_badys()
    users="Device                     User\n" \
          "----------------------------------------------\n"
    for b in badys:
        bady = b['device']+" \t "+b['user']+"\n"
        users+=bady
        if len(users) > 1000:
            context.bot.send_message(chat_id=update.message.chat_id, text=users)
            users = "Device                     User\n" \
                    "----------------------------------------------\n"

@restricted
def usergoodys(update, context):
    goodys,numgoodys = eduroguedb.get_goodys()
    users="Device\n" \
          "------------------------------\n"
    for g in goodys:
        goody = g['device']+"\n"
        users+=goody
        if len(users) > 1000:
            context.bot.send_message(chat_id=update.message.chat_id, text=users)
            users = "Device\n" \
                    "------------------------------\n"

@restricted
def stats(update, context):
    goodys,numgoodys = eduroguedb.get_goodys()
    badys,numbadys = eduroguedb.get_badys()
    totaldevs = eduroguedb.get_all()
    percent_numgoodys = round((numgoodys/totaldevs)*100,1)
    percent_numbadys = round((numbadys/totaldevs)*100,1)
    msg = f"Edurogue stats\n----------------------\n" \
          f"Badys: {numbadys} ({percent_numbadys}%)\n" \
          f"Goodys: {numgoodys} ({percent_numgoodys}%)\n" \
          f"Total Devices Tested: {totaldevs}"
    context.bot.send_message(chat_id=update.message.chat_id, text=msg)

@restricted
def start(update, context):
    ''' START '''
    # Enviar un mensaje a un ID determinado.
    context.bot.send_message(chat_id=update.effective_chat.id, text="Wellcome to Edurogue Bot. At your service!")



eduroguedb = Database()


def main():
    TOKEN = ""
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Eventos que activarán nuestro bot.
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('numbadys', numbadys))
    dp.add_handler(CommandHandler('numgoodys', numgoodys))
    dp.add_handler(CommandHandler('numbadys_all_time', numbadys_all_time))
    #dp.add_handler(CommandHandler('userbadys', userbadys))
    dp.add_handler(CommandHandler('stats', stats))
    #dp.add_handler(CommandHandler('usergoodys', usergoodys))
    # Comienza el bot
    updater.start_polling()
    # Lo deja a la escucha. Evita que se detenga.
    updater.idle()


if __name__ == '__main__':
    main()
