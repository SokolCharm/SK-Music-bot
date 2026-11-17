import telebot
import json
import os
import random
import threading
import time
from datetime import datetime, timedelta

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")      # Берется из настроек Bothost
DB_FILE   = "users.json"

RELEASE     = datetime(2026, 11, 18, 23, 0)
INTERVAL_H  = 4          # напоминание раз в 4 часа
QUIET_START = 23         # тихие часы с 23:00
QUIET_END   = 9          # ...до 09:00

# ==================== ТЕКСТЫ ====================
MESSAGES = [
    "🎧 Совсем скоро — <b>GLEB 6</b>. Уже <b>18.11.2026 в 18:00</b>.\n\n<i>Ждём именно тебя на платформе SK music</i>",
    "Что-то интересное готовится. 18 ноября, 18:00 — <b>GLEB 6</b>.\n\n<i>Ждём именно тебя на платформе SK music</i>",
    "📅 Записал в календарь? <b>18.11.2026, 18:00</b> — премьера <b>GLEB 6</b>.\n\n<i>Ждём именно тебя на платформе SK music</i>",
    "Ты в курсе, что 18 ноября выходит <b>GLEB 6</b>? Теперь в курсе 😉\n\n<i>Ждём именно тебя на платформе SK music</i>",
    "🔔 Небольшое напоминание: <b>GLEB 6</b> — <b>18.11.2026 в 18:00</b>.\n\n<i>Ждём именно тебя на платформе SK music</i>",
    "Между делом: премьера <b>GLEB 6</b> — 18 ноября в 18:00. Сохрани себе.\n\n<i>Ждём именно тебя на платформе SK music</i>",
    "🎶 <b>GLEB 6</b>. 18.11.2026. 18:00. Всё сходится.\n\n<i>Ждём именно тебя на платформе SK music</i>",
    "Осталось совсем чуть-чуть: <b>GLEB 6</b> выходит <b>18.11.2026 в 18:00</b>.\n\n<i>Ждём именно тебя на платформе SK music</i>",
    "🎵 Тихо напомню: 18.11.2026, 18:00 — <b>GLEB 6</b>. Без суеты.\n\n<i>Ждём именно тебя на платформе SK music</i>",
    "Есть дата: 18 ноября 2026, 18:00. Есть трек: <b>GLEB 6</b>.\n\n<i>Ждём именно тебя на платформе SK music</i>",
    "⏳ До премьеры <b>GLEB 6</b> ещё есть время — <b>18.11.2026, 18:00</b>.\n\n<i>Ждём именно тебя на платформе SK music</i>",
    "Просто дружеское напоминание: <b>GLEB 6</b> скоро. 18.11.2026, 18:00.\n\n<i>Ждём именно тебя на платформе SK music</i>",
]

# 🔥 СООБЩЕНИЕ РЕЛИЗА СО ССЫЛКОЙ
RELEASE_MSG = (
    "🚀 <b>ДОЛГОЖДАННЫЙ ТРЕК GLEB 6 УЖЕ ВЫШЕЛ!!!!</b>\n\n"
    "СКОРЕЕ ИДИ СЛУШАТЬ в SK Music!!!\n\n"
    "👉 <a href='https://skmusic-phi.vercel.app'>https://skmusic-phi.vercel.app</a>\n\n"
    "<i>Ждём именно тебя на платформе SK music</i>"
)

WELCOME_MSG = (
    "Привет! 👋\n\n"
    "<b>GLEB 6</b> выходит <b>18.11.2026 в 18:00</b>.\n"
    f"Буду тихонько напоминать каждые {INTERVAL_H} ч (ночью сплю 🌙).\n\n"
    "Команды:\n"
    "/stop — выключить\n"
    "/status — статус\n"
    "/help — все команды\n\n"
    "<i>Ждём именно тебя на платформе SK music</i>"
)

HELP_MSG = (
    "<b>Команды</b>\n\n"
    "/start — включить напоминания\n"
    "/stop — выключить\n"
    "/status — статус\n"
    "/help — эта справка\n\n"
    f"Каждые <b>{INTERVAL_H} ч</b>, тишина с {QUIET_START}:00 до {QUIET_END}:00.\n"
    "Релиз: <b>18.11.2026 в 18:00</b> — <b>GLEB 6</b>.\n\n"
    "<i>Ждём именно тебя на платформе SK music</i>"
)

# ==================== БАЗА ====================
def load():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save(users):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def is_quiet(now):
    return now.hour >= QUIET_START or now.hour < QUIET_END

# ==================== БОТ ====================
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start"])
def cmd_start(msg):
    users = load()
    uid = str(msg.chat.id)

    if datetime.now() >= RELEASE:
        bot.send_message(msg.chat.id, RELEASE_MSG, parse_mode="HTML", disable_web_page_preview=False)
        return

    if uid not in users or not users[uid].get("active"):
        users[uid] = {
            "active": True,
            "released": False,
            "last_sent": datetime.now().isoformat(),
            "order": [],
        }
        save(users)
        bot.send_message(msg.chat.id, WELCOME_MSG, parse_mode="HTML")
    else:
        bot.send_message(msg.chat.id, "Напоминания уже включены ✅\n\n/help — команды", parse_mode="HTML")

@bot.message_handler(commands=["help"])
def cmd_help(msg):
    bot.send_message(msg.chat.id, HELP_MSG, parse_mode="HTML")

@bot.message_handler(commands=["stop"])
def cmd_stop(msg):
    users = load()
    uid = str(msg.chat.id)
    if uid in users:
        users[uid]["active"] = False
        save(users)
    bot.reply_to(msg, "Напоминания выключены. Включить — /start")

@bot.message_handler(commands=["status"])
def cmd_status(msg):
    users = load()
    u = users.get(str(msg.chat.id))
    if not u or not u.get("active"):
        bot.reply_to(msg, "Напоминания выключены. /start — включить.")
        return
    last = datetime.fromisoformat(u["last_sent"]).strftime("%d.%m.%Y %H:%M") if u.get("last_sent") else "—"
    bot.reply_to(
        msg,
        f"Напоминания включены ✅\n"
        f"Интервал: каждые {INTERVAL_H} ч\n"
        f"Последнее: {last}\n"
        f"Релиз: 18.11.2026, 18:00 — GLEB 6",
    )

# ==================== ПЛАНИРОВЩИК ====================
def next_message(u):
    if not u.get("order"):
        u["order"] = list(range(len(MESSAGES)))
        random.shuffle(u["order"])
    return MESSAGES[u["order"].pop(0)]

def safe_send(chat_id, text):
    try:
        # disable_web_page_preview=False делает так, чтобы ссылка развернулась красивой плашкой
        bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=False)
        return True
    except Exception as e:
        print(f"[send error {chat_id}] {e}")
        return False

def scheduler():
    while True:
        try:
            users = load()
            now = datetime.now()
            changed = False

            # Если до релиза осталось меньше 5 секунд или он только что наступил
            # Мы используем точную проверку, чтобы поймать 18:00:00
            is_release_time = now >= RELEASE

            for uid, u in list(users.items()):
                if not u.get("active"):
                    continue

                # ВЫСТРЕЛ РОВНО В 18:00
                if is_release_time and not u.get("released"):
                    if safe_send(int(uid), RELEASE_MSG):
                        u["released"] = True
                        u["active"] = False
                        changed = True
                    continue

                # тихие часы (пропускаем, если это момент релиза)
                if not is_release_time and is_quiet(now):
                    continue

                # пора напомнить (каждые 4 часа)
                last = datetime.fromisoformat(u["last_sent"]) if u.get("last_sent") else None
                if last is None or now - last >= timedelta(hours=INTERVAL_H):
                    if safe_send(int(uid), next_message(u)):
                        u["last_sent"] = now.isoformat()
                        changed = True

            if changed:
                save(users)
        except Exception as e:
            print(f"[scheduler error] {e}")
        
        # 🔥 УМНЫЙ ТАЙМЕР: проверяем время каждую секунду, чтобы не пропустить 18:00
        time.sleep(1)

# ==================== УСТОЙЧИВЫЙ ЗАПУСК ====================
def run_bot():
    while True:
        try:
            print("🤖 Бот запущен")
            bot.infinity_polling(
                timeout=15,
                long_polling_timeout=10,
                none_stop=True,
                skip_pending=True,
            )
        except Exception as e:
            print(f"[polling упал] {e} — перезапуск через 5 сек")
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=scheduler, daemon=True).start()
    run_bot()
