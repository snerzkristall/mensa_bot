# local config for bot
from cfg import config

# external modules
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
import asyncio

BOT_TOKEN = config.TOKEN
BOT_USERNAME = config.USERNAME

def scrape_via_api() -> list:
    url = "https://menu.jku.at/api/menus";
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "close",
        "Cookie": "84967f855aa492c1c8079ed7ab50186f=649a681895fa59344d265e5b7ade3082; CookieConsent=OK",
    }
    return requests.get(url, headers=headers, verify=False).json()

def get_jku_menu(data: dict) -> str:
    menu_veg = extract_menu(data[3]["menuTypes"][0])
    menu_carnv = extract_menu(data[3]["menuTypes"][1], veg=False)
    plate_veg = extract_plate(data[3]["menuTypes"][2]["menu"]["groupedDishes"]["MAIN_COURSE"][0])
    plate_carnv = extract_plate(data[3]["menuTypes"][2]["menu"]["groupedDishes"]["MAIN_COURSE"][1], veg=False)
    return "JKU MENU\n\n" + menu_veg + "\n\n" + menu_carnv + "\n\n" + plate_veg + "\n\n" + plate_carnv + "\n\n"

def get_khg_menu(data: dict) -> str:
    menu_veg = extract_menu(data[2]["menuTypes"][0])
    menu_carnv = extract_menu(data[2]["menuTypes"][1], veg=False)
    return "KHG MENU\n\n" + menu_veg + "\n\n" + menu_carnv + "\n\n"

def extract_menu(data: dict, veg: bool = True) -> str:
    price = data["menu"]["prices"][0]["price"]
    menu = data["menu"]["groupedDishes"]
    starters = menu["STARTER"][0]["name"]
    main = menu["MAIN_COURSE"][0]["name"] + " " + menu["MAIN_COURSE"][0]["sides"]
    if veg:
        return f"Veggie Menu ({price:.2f})\n{main},\n{starters}."
    else:
        return f"Meat Menu ({price:.2f})\n{main},\n{starters}."

def extract_plate(data: dict, veg: bool = True) -> str:
    price = data["prices"][0]["price"]
    main = data["name"] + " " + data["sides"]
    if veg:
        return f"Veggie Plate (€ {price:.2f})\n{main}."
    else:
        return f"Meat Plate (€ {price:.2f})\n{main}."

# Commands 
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Snerz! Thx for ch@tting with me!')

async def jku_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = scrape_via_api()
    msg = get_jku_menu(data)
    await update.message.reply_text(msg)
    
async def khg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = scrape_via_api()
    msg = get_khg_menu(data)
    await update.message.reply_text(msg)
    
# Errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# Main
if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('jku', jku_command))
    app.add_handler(CommandHandler('khg', khg_command))

    app.add_error_handler(error)

    loop = asyncio.get_event_loop()
    try:
        print('Polling...')
        loop.run_until_complete(app.run_polling(poll_interval=3))
    except KeyboardInterrupt:
        print('Stopping bot...')
        loop.run_until_complete(app.stop())
        loop.close()