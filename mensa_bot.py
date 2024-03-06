from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from bs4 import BeautifulSoup
import datetime
from cfg import config
import asyncio
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BOT_TOKEN = config.TOKEN
BOT_USERNAME = config.USERNAME

# Scraping and Formatting
def scrape_menus(day_offset=0) -> str:
    url = "https://www.mensen.at"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
        "Cookie": "_ga=GA1.2.785020346.1709669962; _gid=GA1.2.743105493.1709669962; _fbp=fb.1.1709669961584.1882955926; _ga_G6P0XJCGTB=GS1.2.1709680247.2.0.1709680247.0.0.0; mensenCookieHintClosed=1; mensenExtLocation=1",
        }

    response = requests.get(url, headers=headers, verify=False)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        raw = soup.get_text().split('Menü Classic')
        if day_offset > 4:
            return "Mensa opens again on Monday!"
        else:
            m1_raw, v_raw, f_raw = raw[1+day_offset].split('Tagesgericht')
            m2_raw = raw[6+day_offset]
            menu_v = get_menu1(m1_raw)
            menu_f = get_menu2(m2_raw)
            meal_v = get_meal_veggie(v_raw)
            meal_f = get_meal_meat(f_raw)
            return menu_v + "\n\n" + menu_f + "\n\n" + meal_v + "\n\n" + meal_f
    else:
        return "Failed to retrieve the webpage. Status code:", response.status_code

def get_menu1(raw: str) -> str:
    name = 'Menü Veggie'
    desc, price, _ = raw.split('\n',1)[1].replace('\n', ' ').split(' €')
    price = " (€ " + price.strip(' ').split('-')[0] + ')'
    d1, d2 = desc.split('Getränk')
    return name + price + "\n" + d1.strip(' ') + ' Getränk' + '\n' + d2.strip(' ')

def get_menu2(raw: str) -> str:
    name = 'Menü Fleisch'
    x1, x2 = raw.split('€',1)
    x = x1.split('\n',1)[1].replace('\n', ' ')
    price = " (€ " + x2.split('-')[0].strip(' ') + ')'
    desc = x.replace('Getränk ', 'Getränk\n')
    return name + price + "\n" + desc

def get_meal_veggie(raw: str) -> str:
    name = 'Gericht Veggie'
    lines = raw.split('\n')
    price = " (€ " + lines[-2].split('€ ')[-1].strip(' ').strip('\n') + ')\n'
    desc = "".join(line + ' ' for line in lines[1:-2]).replace('\n', ' ').strip(' ')
    return name + price + desc

def get_meal_meat(raw: str) -> str:
    name = 'Gericht Fleisch'
    lines = raw.split('\n')
    price = " (€" + lines[-4].split('€')[-1].strip(' ') + ')\n'
    desc = "".join(line + ' ' for line in lines[1:-4]).replace('\n', ' ').strip(' ')
    return name + price + desc

# Commands 
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text('Snerz! Thx for ch@tting with me!')

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day_offset = datetime.datetime.today().weekday()
    menu_formatted = scrape_menus(day_offset=day_offset)
    msg = "Today's menus: \n\n" + menu_formatted
    await update.message.reply_text(msg)

async def monday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_formatted = scrape_menus(day_offset=0)
    msg = "Monday's menus: \n\n" + menu_formatted
    await update.message.reply_text(msg)

async def tuesday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_formatted = scrape_menus(day_offset=1)
    msg = "Tuesday's menus: \n\n" + menu_formatted
    await update.message.reply_text(msg)

async def wednesday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_formatted = scrape_menus(day_offset=2)
    msg = "Wednesday's menus: \n\n" + menu_formatted
    await update.message.reply_text(msg)

async def thursday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_formatted = scrape_menus(day_offset=3)
    msg = "Thursday's menus: \n\n" + menu_formatted
    await update.message.reply_text(msg)

async def friday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_formatted = scrape_menus(day_offset=4)
    msg = "Friday's menus: \n\n" + menu_formatted
    await update.message.reply_text(msg)
    
# Errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
	print(f'Update {update} caused error {context.error}')

# Main
if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('menu', menu_command))
    app.add_handler(CommandHandler('monday', monday_command))
    app.add_handler(CommandHandler('tuesday', tuesday_command))
    app.add_handler(CommandHandler('wednesday', wednesday_command))
    app.add_handler(CommandHandler('thursday', thursday_command))
    app.add_handler(CommandHandler('friday', friday_command))

    app.add_error_handler(error)

    loop = asyncio.get_event_loop()
    try:
        print('Polling...')
        loop.run_until_complete(app.run_polling(poll_interval=3))
    except KeyboardInterrupt:
        print('Stopping bot...')
        loop.run_until_complete(app.stop())
        loop.close()