import asyncio
import random
import logging
import json

# Функція для збереження даних у файл
def save_users(stats):
    try:
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Помилка при збереженні файлу: {e}")
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F, types
from aiogram.types import LabeledPrice
from datetime import datetime
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

def reset_daily_tasks(user):
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Якщо раптом поля daily_tasks немає, створюємо його
    if 'daily_tasks' not in user:
        user['daily_tasks'] = {'hits_count': 0, 'wins_today': 0, 'last_reset': today}
        user['completed_tasks'] = []
        return True

    if user['daily_tasks'].get('last_reset') != today:
        user['daily_tasks']['hits_count'] = 0
        user['daily_tasks']['wins_today'] = 0
        user['daily_tasks']['last_reset'] = today
        user['completed_tasks'] = []
        return True
    return False

# Налаштування логів
logging.basicConfig(level=logging.INFO)

TOKEN = "8246610126:AAHh6B6c89VaD_g9XSHBQwJNRHgPWVJJAa4"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Сховище статистики
user_stats = {}

# --- ДОПОМІЖНІ ФУНКЦІЇ ---
def get_user_data(uid):
    uid = str(uid)
    # Якщо юзера взагалі немає — створюємо з нуля
    if 'gold_jaw' not in user['inventory']: user['inventory']['gold_jaw'] = 0
    if 'beer' not in user['inventory']: user['inventory']['beer'] = 0
    if uid not in user_stats:
        
        user_stats[uid] = {
            'balance': 100,
            'wins': 0,
            'deaths': 0,
            'inventory': {'knuckles': 0, 'armor': 0},
            'emoji': None,
            'daily_tasks': {'hits_count': 0, 'wins_today': 0, 'last_reset': ""},
            'completed_tasks': [],
            'toxic_hits': 0
        }
    
    # ПЕРЕВІРКА НА НОВІ ПОЛЯ (для старих гравців)
    user = user_stats[uid]
    
    if 'daily_tasks' not in user:
        user['daily_tasks'] = {'hits_count': 0, 'wins_today': 0, 'last_reset': ""}
    if 'completed_tasks' not in user:
        user['completed_tasks'] = []
    if 'inventory' not in user:
        user['inventory'] = {'knuckles': 0, 'armor': 0}
    if 'armor' not in user['inventory']: # Якщо інвентар є, а броні в ньому немає
        user['inventory']['armor'] = 0
    if 'toxic_hits' not in user:
        user['toxic_hits'] = 0
        
    return user



def update_stat(uid, key, amount=1):
    user = get_user_data(uid)
    user[key] += amount

OWNER_ID = 5296605201  # Твій Telegram ID сюди

def get_rank(uid, wins):
    # Якщо це ти — ти Власник незалежно від перемог
    if int(uid) == OWNER_ID:
        return "💎 ВЛАСНИК 💎"
    
    # Всі інші отримують ранги за схемою
    if wins >= 1000: return "Бос Мафії 🐉"
    if wins >= 500: return "Бос району 👑"
    if wins >= 200: return "👑 Смотрящий за районом"
    if wins >= 100:  return "🦅 Авторитет"
    if wins >= 50:  return "👊 Колєга-Коліжанка"
    if wins >= 25:  return "👟 дрищь"
    if wins >= 10:   return "Шнурок"
    if wins >= 10:   return "🤏 Шнирь"
    return "🤡 Піздюк"

def get_user_data(uid):
    uid = str(uid)
    if uid not in user_stats:
        user_stats[uid] = {
            'balance': 100,
            'wins': 0,
            'deaths': 0,
            'inventory': {'knuckles': 0},
            'emoji': None  # Нове поле
        }
    return user_stats[uid]


# --- 1. БАЗОВІ КОМАНДИ ---
@dp.message(CommandStart())
async def start(message: types.Message):
    get_user_data(message.from_user.id)
    await message.answer("Привіт 👋 Підар! Напиши /help, щоб я набив тобі єбало. Також можеш просрати бабло на підтримку автора /donate ")

@dp.message(Command("help"))
async def help_command(message: types.Message):
    help_text = (
        "❓ **Шо ти вилупився? Ось список команд:**\n\n"
        "🛒 **ЧОРНИЙ РИНОК:**\n"
        "🏪 `/shop` — Купити кастет, бронік або пиво\n\n"
        "🎮 **ІГРИ ТА КАЗИНО:**\n"
        "👊 `/fight` — Махач на районі\n"
        "✌️ `/knp` — Камінь, ножиці, папір\n"
        "🎰 `/bet` — Більше-Менше\n"
        "🎰 `/slots` — Однорукий бандит (ставка: 10 зубів)\n"
        "🎲 `/dice` — Кинути кубик (ставка: 10 зубів)\n"
        "🎳 `/bowling` — Збити кеглі (ставка: 10 зубів)\n"
        "⚔️ `/duel` — Визвати на дуель (відповісти на повідомлення)\n\n"
        "📊 **ІНФО:**\n"
        "📈 `/my_stats` — Твої успіхи\n"
        "🏆 `/top` — ТОП-10 найбагатших на районі\n"
        "😀 `/set_emoji` — Вибрати свій символ для топа, поміняти НЕ МОЖЛИВО\n"
        "👥 `/emojis` — Подивитися, які символи вибрали інші жителі району\n\n"
        "💎  /donate — Підтримати автора\n"
        "📝 `/task` — Подивитися свої щоденні завдання району (оновлюються кожного дня)"
        "/inventory (або /inv) — Показує твій рюкзак: скільки чого ти накупив у магазині\n"
        "/drink — Випити пиво з інвентарю. Дає випадковий ефект (можна знайти зуби, а можна отруїтися і втратити трохи)"
    )
    try:
        await message.answer(help_text, parse_mode="Markdown")
    except Exception:
        await message.answer(help_text.replace("*", "").replace("`", ""))

ADMIN_ID = 5296605201

@dp.message(Command("reset_emoji"))
async def admin_set_emoji(message: types.Message):
    # 1. Перевірка: чи ти адмін?
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ Тобі не дозволено змінювати реальність!")

    # 2. Розбираємо команду (наприклад: /set_emoji 1234567 👑)
    args = message.text.split()
    
    if len(args) < 3:
        return await message.answer("⚠️ Використовуй: <code>/reset_emoji [ID] [emoji]</code>", parse_mode="HTML")

    target_id = args[1] # ID того, кому міняємо
    new_emoji = args[2] # Новий емодзі

    # 3. Перевіряємо, чи є такий юзер у базі
    if target_id not in user_stats:
        return await message.answer(f"❌ Юзера з ID {target_id} немає в базі.")

    # 4. Оновлюємо дані
    user_stats[target_id]['emoji'] = new_emoji
    save_users(user_stats) # Зберігаємо у файл

    await message.answer(f"✅ Готово! Юзеру {target_id} встановлено емодзі {new_emoji}")

@dp.message(Command("send"))
async def send_teeth(message: types.Message):
    uid = str(message.from_user.id)
    user = get_user_data(uid)
    args = message.text.split()

    # Визначаємо отримувача (або через Reply, або по ID)
    if message.reply_to_message:
        target_id = str(message.reply_to_message.from_user.id)
        try:
            amount = int(args[1])
        except:
            return await message.answer("❓ Пиши: <code>/send [сума]</code> відповіддю на повідомлення.", parse_mode="HTML")
    else:
        if len(args) < 3:
            return await message.answer("❓ Пиши: <code>/send [ID] [сума]</code>", parse_mode="HTML")
        target_id = str(args[1])
        try:
            amount = int(args[2])
        except:
            return await message.answer("❌ Сума має бути числом!")

    if target_id == uid:
        return await message.answer("🤡 Передавати зуби самому собі? Геніально!")

    if amount <= 0:
        return await message.answer("❌ Сума має бути більшою за 0.")

    if user['balance'] < amount:
        return await message.answer("❌ У тебе немає стільки зубів!")

    # Розрахунок податку (5%)
    tax = int(amount * 0.05)
    final_amount = amount - tax

    target_user = get_user_data(target_id)
    
    user['balance'] -= amount
    target_user['balance'] += final_amount
    
    save_users(user_stats)

    await message.answer(f"✅ Переказано <b>{final_amount}</b> зубів.\n📟 Податок району (5%): {tax} зубів.", parse_mode="HTML")
    
    try:
        await bot.send_message(target_id, f"💰 Гравцець {message.from_user.first_name} переказав тобі <b>{final_amount}</b> зубів!", parse_mode="HTML")
    except:
        pass

# КОМАНДА ДЛЯ ВИДАЧІ ЗУБІВ: /give [ID юзера] [кількість]
@dp.message(Command("give"))
async def give_teeth(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return await message.answer("❌ Куди лізеш? Ти не адмін цього району!")

    args = message.text.split()
    if len(args) < 3:
        return await message.answer("❓ Правильно так: <code>/give [ID] [кількість]</code>", parse_mode="HTML")

    try:
        target_id = str(args[1])
        amount = int(args[2])
        
        # Отримуємо дані цілі
        target_user = get_user_data(target_id)
        target_user['balance'] += amount
        save_users(user_stats)

        await message.answer(f"✅ Успішно! Гравцю <code>{target_id}</code> нараховано <b>{amount}</b> зубів.", parse_mode="HTML")
        
        # Сповіщення гравцю
        try:
            await bot.send_message(target_id, f"🎁 <b>АДМІН-ПОДАРУНОК!</b>\nТобі щойно прилетіло {amount} зубів! Не протринькай все в казино.")
        except:
            pass

    except ValueError:
        await message.answer("❌ Кількість має бути числом!")
    except Exception as e:
        await message.answer(f"❌ Помилка: {e}")

OWNER_ID = 5296605201

@dp.message(Command("broadcast"))
async def broadcast_message(message: types.Message):
    # ПЕРЕВІРКА: Тільки ти можеш це робити
    if message.from_user.id != OWNER_ID:
        return await message.answer("❌ Тобі не дозволено робити оголошення на весь район!")

    # Беремо текст після команди /broadcast
    command_text = message.text.replace("/broadcast", "").strip()
    
    if not command_text:
        return await message.answer("❓ Напиши текст оголошення: <code>/broadcast Всім привіт!</code>", parse_mode="HTML")

    # Отримуємо список всіх ID з твоєї бази
    all_users = list(user_stats.keys())
    count = 0
    blocked = 0

    await message.answer(f"📢 Починаю розсилку для {len(all_users)} жителів...")

    for uid in all_users:
        try:
            # Надсилаємо текст юзеру
            await bot.send_message(uid, f"🔔 <b>ОГОЛОШЕННЯ ВІД БОСА:</b>\n\n{command_text}", parse_mode="HTML")
            count += 1
            # Робимо паузу 0.05 сек, щоб Telegram не забанив за швидку розсилку
            await asyncio.sleep(0.05)
        except Exception:
            # Якщо юзер заблокував бота, буде помилка
            blocked += 1

    await message.answer(f"✅ Розсилка завершена!\n📥 Отримали: {count}\n🚫 Заблокували бота: {blocked}")

OWNER_ID = 5296605201

# КОМАНДА ДЛЯ ВІДНІМАННЯ ЗУБІВ: /take [ID юзера] [кількість]
@dp.message(Command("take"))
async def take_teeth(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return await message.answer("❌ Руки забрав! Тільки батя може розкулачувати.")

    args = message.text.split()
    if len(args) < 3:
        return await message.answer("❓ Правильно так: <code>/take [ID] [кількість]</code>", parse_mode="HTML")

    try:
        target_id = str(args[1])
        amount = int(args[2])
        
        target_user = get_user_data(target_id)
        target_user['balance'] = max(0, target_user['balance'] - amount) # Щоб не пішло в мінус
        save_users(user_stats)

        await message.answer(f"🧹 <b>РОЗКУЛАЧЕННЯ!</b>\nУ гравця <code>{target_id}</code> вилучено {amount} зубів.", parse_mode="HTML")
        
        try:
            await bot.send_message(target_id, f"⚠️ <b>КОНФІСКАЦІЯ!</b>\nАдмін вилучив у тебе {amount} зубів. Будеш знати, як порушувати правила району!")
        except:
            pass

    except ValueError:
        await message.answer("❌ Кількість має бути числом!")


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    uid = message.from_user.id
    is_new = uid not in user_stats # Перевіряємо, чи новий це юзер
    
    user = get_user_data(uid) # Створюємо дані
    
    await message.answer("Ласкаво просимо на район! Пиши /help, щоб не отримати по щелепі.")

    # Якщо юзер новий, бот пише тобі
    if is_new:
        admin_text = (
            f"🔔 <b>Новий гравець на районі!</b>\n\n"
            f"👤 Ім'я: {message.from_user.full_name}\n"
            f"🆔 ID: <code>{uid}</code>\n"
            f"🔗 Юзернейм: @{message.from_user.username}"
        )
        await bot.send_message(OWNER_ID, admin_text, parse_mode="HTML")

@dp.message(Command("task"))
async def show_tasks(message: types.Message):
    uid = str(message.from_user.id)
    user = get_user_data(uid)
    reset_daily_tasks(user) # Скидаємо, якщо настав новий день

    # Список завдань (можна додати більше)
    tasks = [
        {"id": "hits", "desc": "👊 Нанести 5 будь-яких ударів", "goal": 5, "current": user['daily_tasks']['hits_count'], "reward": 50},
        {"id": "wins", "desc": "🏆 Виграти 3 махачі", "goal": 3, "current": user['daily_tasks']['wins_today'], "reward": 100},
    ]

    text = "📝 <b>ЩОДЕННІ КВЕСТИ РАЙОНУ:</b>\n\n"
    
    for t in tasks:
        status = "✅ Виконано" if t['id'] in user['completed_tasks'] else f"⏳ {t['current']}/{t['goal']}"
        text += f"🔹 {t['desc']}\n   Нагорода: 💰 {t['reward']} зубів | {status}\n\n"

    text += "<i>Завдання оновлюються автоматично кожного дня!</i>"
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("donate"))
async def donate_stars_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    
    # Суми в зірках
    amounts = [10, 25, 50, 100, 250, 500, 1000]
    
    for am in amounts:
        builder.button(text=f"⭐️ {am}", callback_data=f"star_{am}")
    
    builder.adjust(2) # по 2 в ряд
    
    await message.answer(
        "💎 <b>ПІДТРИМКА АВТОРА ЗІРКАМИ</b> 💎\n\n"
        "Ти можеш закинути автору Telegram Stars, щоб підтримати розробку бота!",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("star_"))
async def send_invoice(callback: types.CallbackQuery):
    amount = int(callback.data.split("_")[1])
    
    # Опис платежу
    title = f"Донат автору: {amount} ⭐️"
    description = f"Дякую за твою підтримку району! Твій внесок: {amount} зірок."
    payload = f"donate_{amount}" # Технічна мітка
    currency = "XTR" # Код для Telegram Stars

    await callback.message.answer_invoice(
        title=title,
        description=description,
        prices=[LabeledPrice(label="XTR", amount=amount)],
        payload=payload,
        currency=currency
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    # Тут можна додати перевірки, але для донату просто підтверджуємо
    await pre_checkout_query.answer(ok=True)

@dp.message(F.successful_payment)
async def on_successful_payment(message: types.Message):
    payment_info = message.successful_payment
    stars_amount = payment_info.total_amount
    
    uid = str(message.from_user.id)
    user = get_user_data(uid)
    
    # Бонус за донат: наприклад, даємо 100 зубів за кожну зірку
    bonus_teeth = stars_amount * 100
    user['balance'] += bonus_teeth
    save_users(user_stats)
    
    await message.answer(
        f"🥳 <b>ДЯКУЮ ЗА ДОНАТ!</b>\n\n"
        f"Ти закинув {stars_amount} ⭐️.\n"
        f"В подяку батя насипав тобі {bonus_teeth} зубів! Твій баланс оновлено.",
        parse_mode="HTML"
    )
    
    # Сповіщення власнику
    await bot.send_message(
        OWNER_ID, 
        f"🚀 <b>РЕАЛЬНИЙ ДОНАТ!</b>\nЮзер {message.from_user.full_name} закинув {stars_amount} зірок!"
    )

@dp.message(Command("set_emoji"))
async def set_user_emoji(message: types.Message):
    uid = str(message.from_user.id)
    user = get_user_data(uid)
    
    # Перевірка, чи вже вибрано емодзі
    if user.get('emoji'):
        return await message.answer(f"❌ Ти вже вибрав свій символ: {user['emoji']}. Міняти не можна, це на все життя!")

    # Витягуємо емодзі з повідомлення
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("❓ Треба написати команду і емодзі, наприклад: <code>/set_emoji 🔥</code>", parse_mode="HTML")

    chosen_emoji = args[1]
    
    # Зберігаємо (можна додати перевірку, чи це справді емодзі, але зазвичай вистачає просто взяти перший символ)
    user['emoji'] = chosen_emoji[0] # Беремо лише один символ
    save_users(user_stats)
    
    await message.answer(f"✅ Вітаю! Тепер твій символ — {user['emoji']}. Його побачить весь район у топі.")

@dp.message(Command("emojis"))
async def show_all_emojis(message: types.Message):
    if not user_stats:
        return await message.answer("Район пустий.")

    text = "🏘 <b>Жителі району та їхні символи:</b>\n\n"
    for uid, stats in user_stats.items():
        emoji = stats.get('emoji', '❓')
        try:
            user_info = await message.bot.get_chat(int(uid))
            name = user_info.full_name
        except:
            name = f"Юзер {uid}"
        
        text += f"{emoji} — {name}\n"
    
    await message.answer(text, parse_mode="HTML")

# --- 2. МАГАЗИН (/shop) ---
@dp.message(Command("shop"))
async def show_shop(message: types.Message):
    kb = InlineKeyboardBuilder()
    # Важливо: callback_data повинна бути без пробілів!
    kb.row(types.InlineKeyboardButton(text="👊 Кастет (50 зубів)", callback_data="buy_knuckles"))
    kb.row(types.InlineKeyboardButton(text="🛡️ Бронік (100 зубів)", callback_data="buy_armor"))
    kb.row(types.InlineKeyboardButton(text="✨ Золота щелепа (500 зубів)", callback_data="buy_gold_jaw"))
    kb.row(types.InlineKeyboardButton(text="🍺 Пиво (30 зубів)", callback_data="buy_beer"))
    
    await message.answer("🏪 <b>МАГАЗИН НА РАЙОНІ</b>\n\n"
                         "✨ <i>Золота щелепа: дає бонус до вибивання зубів!</i>\n"
                         "🍺 <i>Пиво: випадковий ефект (команда /drink).</i>", 
                         reply_markup=kb.as_markup(), parse_mode="HTML")

@dp.message(Command("drink"))
async def drink_beer(message: types.Message):
    uid = str(message.from_user.id)
    user = get_user_data(uid)
    
    if user['inventory'].get('beer', 0) <= 0:
        return await message.answer("🍻 У тебе немає пива. Сходи в магазин!")
        
    user['inventory']['beer'] -= 1
    
    luck = random.randint(1, 3)
    if luck == 1:
        win = 50
        user['balance'] += win
        txt = "🍺 Ти випив пива і знайшов 50 зубів під кришечкою! Оце фарт!"
    elif luck == 2:
        txt = "🍺 Ти випив пива і відчув себе тигром! (Шанс на перемогу в наступній бійці збільшено - просто текст для приколу)"
    else:
        user['balance'] = max(0, user['balance'] - 10)
        txt = "🤢 Пиво було прострочене... Ти витратив 10 зубів на ліки від живота."
        
    save_users(user_stats)
    await message.answer(txt)

@dp.message(Command("inventory", "inv"))
async def show_inventory(message: types.Message):
    uid = str(message.from_user.id)
    user = get_user_data(uid)
    
    # Перевіряємо, чи є взагалі інвентар у базі
    if 'inventory' not in user or not user['inventory']:
        return await message.answer("🎒 Твій інвентар порожній. Сходи в /shop!")

    inv = user['inventory']
    text = "🎒 <b>Твій інвентар:</b>\n\n"
    
    # Словник для гарних назв
    items_map = {
        'knuckles': "👊 Кастети",
        'armor': "🛡️ Броніки",
        'gold_jaw': "✨ Золоті щелепи",
        'beer': "🍺 Пивко"
    }
    
    found_items = False
    for item_key, count in inv.items():
        if count > 0:
            name = items_map.get(item_key, item_key)
            text += f"▪️ {name}: <b>{count}</b> шт.\n"
            found_items = True
            
    if not found_items:
        text = "🎒 Твій інвентар порожній. Все пропив чи віджали? 😂"

    await message.answer(text, parse_mode="HTML")

# Обробка покупок
@dp.callback_query(lambda c: c.data.startswith('buy_'))
async def process_buy(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    user = get_user_data(uid)
    
    # Витягуємо назву предмета
    item = callback.data.replace("buy_", "")
    
    # Це виведе назву в чорне вікно (термінал) VS Code. Перевір, що там пише!
    print(f"--- СПРОБА КУПІВЛІ: {item} ---") 

    prices = {
        'knuckles': 50,
        'armor': 100,
        'gold_jaw': 500, # Ця назва має бути ідентичною до тієї, що в кнопці!
        'beer': 30
    }
    
    price = prices.get(item)
    
    if price is None:
        return await callback.answer(f"❌ Предмет '{item}' не знайдено!", show_alert=True)

    if user['balance'] < price:
        return await callback.answer("❌ Мало зубів! Іди набий ще.", show_alert=True)

    # Перевірка інвентаря
    if 'inventory' not in user:
        user['inventory'] = {}
    if item not in user['inventory']:
        user['inventory'][item] = 0

    user['balance'] -= price
    user['inventory'][item] += 1
    
    save_users(user_stats)
    
    await callback.message.edit_text(f"✅ Ти купив предмет: <b>{item}</b>!\n💰 Залишок: {user['balance']} зубів.", parse_mode="HTML")
    await callback.answer("Успішно куплено!")


# --- 3. СТАТИСТИКА, БАЛАНС ТА ТОП ---
@dp.message(Command("balance"))
async def show_balance(message: types.Message):
    user = get_user_data(message.from_user.id)
    balance = user['balance']
    
    await message.answer(f"💰 **Твій баланс:** {balance} зубів\n📦 Кастетів: {user['inventory']['knuckles']} | Броніків: {user['inventory']['armor']}", parse_mode="Markdown")

@dp.message(Command("my_stats"))
async def show_stats(message: types.Message):
    uid = message.from_user.id
    s = get_user_data(uid)
    rank = get_rank(uid, s['wins']) # Додали uid сюди

    res = (
        f"📊 <b>Твій послужний список:</b>\n"
        f"🆔 Твій ID: <code>{uid}</code>\n" # Вивів ID, щоб ти його бачив
        f"🎖 Твій статус: <b>{rank}</b>\n\n"
        f"💰 Баланс: {s['balance']} зубів\n"
        f"🏆 Перемог: {s['wins']}\n"
        f"💀 Смертей: {s['deaths']}\n"
    )
    await message.answer(res, parse_mode="HTML")

@dp.message(Command("top"))
async def show_top(message: types.Message):
    if not user_stats:
        return await message.answer("🤷‍♂️ Поки що район пустий.")

    sorted_users = sorted(user_stats.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
    top_text = "🏆 <b>ТОП-10 ОЛІГАРХІВ РАЙОНУ:</b>\n\n"
    
    for i, (uid, stats) in enumerate(sorted_users, 1):
        name = "Анонім"
        try:
            user_info = await message.bot.get_chat(int(uid))
            name = user_info.full_name
        except Exception:
            name = f"Юзер {uid}"

        # Отримуємо емодзі юзера, якщо немає — ставимо пусте місце або стандартний значок
        user_emoji = stats.get('emoji', '👤')
        rank = get_rank(uid, stats.get('wins', 0))
        
        # Додаємо емодзі біля імені
        top_text += f"{i}. {user_emoji} <b>{name}</b> — 💰 {stats['balance']}\n   └ Статус: <i>{rank}</i>\n\n"

    await message.answer(top_text, parse_mode="HTML")


# --- 4. КАЗИНО ТА ІГРИ З КНОПКАМИ ---
@dp.message(Command("slots"))
async def play_slots(message: types.Message):
    uid = str(message.from_user.id)
    user = get_user_data(uid)
    
    bet = 10 # Ставка
    if user['balance'] < bet:
        return await message.answer(f"❌ У тебе немає {bet} зубів на ставку!")

    user['balance'] -= bet
    msg = await message.answer_dice(emoji="🎰")
    
    # Чекаємо анімацію
    await asyncio.sleep(2)
    score = msg.dice.value
    
    # ЛОГІКА ШАНСІВ (на основі значень Telegram Dice)
    
    # 1. СУПЕР ДЖЕКПОТ (777) - Шанс 1/64
    if score == 64:
        win = 500
        user['balance'] += win
        await message.answer(f"🎰 <b>ДЖЕКПОТ, НАХУЙ! 💰\nБатя насипав тобі +{win} зубів!", parse_mode="HTML")
    
    # 2. ВЕЛИКИЙ ВИГРАШ (Три однакові бари або ягоди) - Шанс ~5%
    elif score in [1, 22, 43]:
        win = 50
        user['balance'] += win
        await message.answer(f"💵 Опа, три в ряд!</b>\nЧітко насипало: +{win} зубів.", parse_mode="HTML")
    
    # 3. СЕРЕДНІЙ ВИГРАШ (Дві сімки або хороші комбінації) - Додаємо нові числа
    # Ці числа в Телеграмі часто виглядають як "майже три в ряд" або дві сімки
    elif score in [11, 16, 32, 48, 53]: 
        win = 25
        user['balance'] += win
        await message.answer(f"✨ Непогано! Дві однакові випало.\nЗабирай +{win} зубів.", parse_mode="HTML")

    # 4. ВТІШНИЙ ПРИЗ (Повертаємо ставку + трохи зверху) - Шанс ~15%
    # Додаємо ще чисел, щоб юзер не зливався занадто швидко
    elif score in [2, 5, 10, 15, 20, 25, 30, 35, 40, 45]:
        win = 15
        user['balance'] += win
        await message.answer(f"🤏 ХУЙНЯ, але приємно.\nВиграш: +{win} зубів (чистими +5).")

    # 5. ПРОГРАШ
    else:
        save_users(user_stats) # Зберігаємо мінус
        await message.answer("🤡 ХАХА ЄБАТЬ ТИ ЄБАНЬКО. Автомат тебе НАЄБАВ.\nТвої 10 зубів тепер ПРОЙОБАНІ.", parse_mode="HTML")
    
    save_users(user_stats)

@dp.message(Command("bet"))
async def bet_game(message: types.Message):
    uid = str(message.from_user.id)
    user = get_user_data(uid)
    
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("❓ Пиши: <code>/bet [сума]</code>", parse_mode="HTML")
    
    try:
        amount = int(args[1])
    except:
        return await message.answer("❌ Введи число!")

    if amount < 10 or amount > 500:
        return await message.answer("❌ Ставка має бути від 10 до 500 зубів.")

    if user['balance'] < amount:
        return await message.answer("❌ У тебе немає стільки зубів!")

    # ШАНСИ: 1-47 (виграш), 48-100 (програш)
    # Це 47% на перемогу. Казино завжди трохи в плюсі.
    luck = random.randint(1, 100)
    
    if luck <= 47:
        user['balance'] += amount
        txt = f"💰 ПЕРЕМОГА!\nТи подвоїв свою ставку і забрав {amount * 2} зубів!"
    else:
        user['balance'] -= amount
        txt = f"📉 ПРОГРАШ\nФортуна гарячо єбала тебе. Ти проєбав {amount} зубів."

    save_users(user_stats)
    await message.answer(txt, parse_mode="HTML")

@dp.message(Command("dice"))
async def play_dice(message: types.Message):
    user = get_user_data(message.from_user.id)
    if user['balance'] < 10: return await message.answer("❌ Треба 10 зубів.")
    user['balance'] -= 10
    msg = await message.answer_dice(emoji="🎲")
    await asyncio.sleep(2)
    if msg.dice.value >= 4:
        user['balance'] += 20
        await message.answer(f"🎲 Випало {msg.dice.value}. +20 зубів!")
    else:
        await message.answer(f"🎲 Випало {msg.dice.value}. Просрав 10 зубів.")

@dp.message(Command("bowling"))
async def play_bowling(message: types.Message):
    user = get_user_data(message.from_user.id)
    if user['balance'] < 10: return await message.answer("❌ Кулі платні. 10 зубів.")
    user['balance'] -= 10
    msg = await message.answer_dice(emoji="🎳")
    await asyncio.sleep(2)
    if msg.dice.value == 6:
        user['balance'] += 30
        await message.answer("🎳 СТРАЙК! +30 зубів!")
    else:
        await message.answer(f"🎳 Збив {msg.dice.value}. -10 зубів.")

@dp.message(Command("fight"))
async def start_fight(message: types.Message):
    builder = InlineKeyboardBuilder()
    # Розставляємо кнопки по дві в ряд для краси
    builder.row(
        types.InlineKeyboardButton(text="👊 В щелепу", callback_data="hit_jaw"),
        types.InlineKeyboardButton(text="🦶 Лоу-кік", callback_data="hit_leg")
    )
    builder.row(
        types.InlineKeyboardButton(text="🥚 Вєбати по яйцям", callback_data="hit_nuts"),
        types.InlineKeyboardButton(text="🤡 Сплюнути під ноги", callback_data="hit_spit")
    )
    builder.row(
        types.InlineKeyboardButton(text="💨 Тікати", callback_data="run_away")
    )
    
    
    await message.answer("<b>Ти на кого батон кришиш? Вибирай дію:</b>", reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.message(Command("roulette"))
async def start_roulette(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💀 Тиснути на гачок", callback_data="pull_trigger"))
    await message.answer("Ну шо, заграємо в лотерею для дебілів? 🔫", reply_markup=builder.as_markup())

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

@dp.message(Command("knp"))
async def play_knp(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="✊ Камінь", callback_data="knp_rock"),
        types.InlineKeyboardButton(text="✋ Папір", callback_data="knp_paper"),
        types.InlineKeyboardButton(text="✌️ Ножиці", callback_data="knp_scissors")
    )
    await message.answer("Обери свій жест:", reply_markup=builder.as_markup())

@dp.message(Command("duel"))
async def start_duel(message: types.Message):
    if not message.reply_to_message:
        return await message.answer("⚠️ Треба відповісти на повідомлення опонента!")
    opponent, challenger = message.reply_to_message.from_user, message.from_user
    if opponent.id == challenger.id: return await message.answer("🤡 Сам себе пиздити зібрався?")
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⚔️ ПРИЙНЯТИ ВИКЛИК", callback_data=f"accept_{opponent.id}_{challenger.id}"))
    await message.answer(f"🚨 **КІПІШ!** 🚨\n\n{challenger.first_name} визиває {opponent.first_name} на стрілку!", reply_markup=builder.as_markup())


# --- 5. ОБРОБКА КНОПОК ---
@dp.callback_query(lambda c: c.data.startswith('f_'))
async def handle_fight_action(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    user = get_user_data(uid)
    action = callback.data.split('_')[1]
    
    # Створюємо різні тексти для різних дій
    if action == "lowkick":
        txt = "🦶 Ти прописав чіткий лоу-кік! Опонент зашкутильгав."
    elif action == "eggs":
        txt = "🥚 Підступний удар по яйцям! Опонент в сльозах."
    elif action == "run":
        txt = "🏃 Ти дав драпака так швидко, що аж п'яти блищали!"
    else:
        txt = "🤔 Ти зробив щось дивне..."

    # Щоб не було помилки "message is not modified", 
    # ми додаємо рандомне число або час, щоб текст завжди був трохи іншим
    import random
    txt += f"\n\n🕒 Сила удару: {random.randint(1, 100)}%"

    try:
        await callback.message.edit_text(txt, parse_mode="HTML")
    except Exception as e:
        # Якщо текст таки збігся, просто ігноруємо помилку
        await callback.answer()

    # ДУЕЛЬ
from aiogram.exceptions import TelegramBadRequest # Додай це в імпорти на початку файлу

@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    data = callback.data
    uid = callback.from_user.id
    txt = None  

    # 1. ПВП БІЙКА (ПРИЙНЯТТЯ ВИКЛИКУ)
    if data.startswith("accept_"):
        parts = data.split("_")
        opponent_id = int(parts[1])
        challenger_id = int(parts[2])
        
        if uid != opponent_id:
            return await callback.answer("❌ Це не тебе викликали!", show_alert=True)
        
        winner_id = random.choice([opponent_id, challenger_id])
        loser_id = opponent_id if winner_id == challenger_id else challenger_id
        
        update_stat(winner_id, "wins", 1)
        update_stat(winner_id, "balance", 50)
        update_stat(loser_id, "balance", -50)

        w_data = get_user_data(str(winner_id))
        if 'daily_tasks' not in w_data: w_data['daily_tasks'] = {'hits_count': 0, 'wins_today': 0}
        if 'completed_tasks' not in w_data: w_data['completed_tasks'] = []

        w_data['daily_tasks']['hits_count'] += 1 
        w_data['daily_tasks']['wins_today'] += 1
        
        if w_data['daily_tasks']['wins_today'] >= 3 and "wins_3" not in w_data['completed_tasks']:
            w_data['completed_tasks'].append("wins_3")
            w_data['balance'] += 100
            try:
                await bot.send_message(winner_id, "🎉 <b>КВЕСТ ВИКОНАНО!</b>\n3 перемоги! +100 зубів!", parse_mode="HTML")
            except: pass
        
        user_stats[str(winner_id)] = w_data
        save_users(user_stats)

        try:
            w_chat = await bot.get_chat(winner_id)
            l_chat = await bot.get_chat(loser_id)
            w_name, l_name = w_chat.first_name, l_chat.first_name
        except:
            w_name, l_name = "Боєць 1", "Боєць 2"

        txt = f"💥 <b>{w_name}</b> розмазав <b>{l_name}</b>!\n🏆 Переможець забирає 50 зубів!"

    # 2. ГРА КАМІНЬ НОЖИЦІ ПАПІР (Додано!)
    elif data.startswith("knp_"):
        user_choice = data.split("_")[1] # отримуємо rock, paper або scissors
        bot_choice = random.choice(["rock", "paper", "scissors"])
        
        choices_art = {"rock": "✊ Камінь", "paper": "✋ Папір", "scissors": "✌️ Ножиці"}
        
        if user_choice == bot_choice:
            result_text = "🤝 <b>Нічия!</b>"
        elif (user_choice == "rock" and bot_choice == "scissors") or \
             (user_choice == "paper" and bot_choice == "rock") or \
             (user_choice == "scissors" and bot_choice == "paper"):
            result_text = "🎉 <b>Ти виграв!</b> (+10 зубів)"
            update_stat(uid, "balance", 10)
        else:
            result_text = "☹️ <b>Ти програв!</b> (-5 зубів)"
            update_stat(uid, "balance", -5)
        
        txt = f"Твій вибір: {choices_art[user_choice]}\nВибір бота: {choices_art[bot_choice]}\n\n{result_text}"

    # 3. ІНШІ КНОПКИ
    elif data == "some_other_button":
        txt = "Дія виконана!"

    # --- ФІНАЛЬНА ВІДПРАВКА ---
    if txt:
        try:
            await callback.message.edit_text(txt, parse_mode="HTML")
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass # Ігноруємо, якщо текст не змінився
            else:
                print(f"Помилка Telegram: {e}")
        except Exception as e:
            print(f"Помилка: {e}")
    
    # Завжди відповідаємо на колбек
    try:
        await callback.answer()
    except:
        pass

    # 2. БІЙКА З БОТОМ
    if data in ["hit_jaw", "hit_leg", "hit_nuts", "hit_spit", "run_away"]:
        user = get_user_data(uid)
        reset_daily_tasks(user) # Скидаємо квести, якщо новий день
        
        is_victory = False # Технічна мітка для квесту

        # 1. ПЕРЕВІРКА НА КАСТЕТ
        if user['inventory']['knuckles'] > 0 and data != "run_away":
            user['inventory']['knuckles'] -= 1
            user['wins'] += 1
            user['balance'] += 50
            is_victory = True # Кастет - це завжди перемога
            txt = "🥊 <b>ТИ ДІСТАВ КАСТЕТ!</b>\nЗ таким девайсом шансів у бота не було. Бот лежить, ти святкуєш! +50 зубів."
            # (Тут не робимо return відразу, щоб код нижче зарахував квест)
        
        bonus = 0
        if user.get('inventory', {}).get('gold_jaw', 0) > 0:
         bonus = 2 * user['inventory']['gold_jaw']
         user['balance'] += bonus
    # Повідом про бонус гравцеві:
    # "Твоя золота щелепа вибила додатково {bonus} зубів!"

        # 2. ЛОГІКА ВТЕЧІ
        elif data == "run_away":
            if random.randint(1, 100) > 40:
                txt = "🏃‍♂️ Ти накивав п'ятами так швидко, що аж кросівки засвистіли. Бот не наздогнав."
            else:
                user['balance'] -= 15
                txt = "🤡 Ти хотів втекти, але зачепився за бордюр. Бот наздогнав і прописав пенделя під сраку. -15 зубів."

        # 3. УДАР ПО ЯЙЦЯМ
        elif data == "hit_nuts":
            user['daily_tasks']['hits_count'] += 1 # Зараховуємо спробу удару
            if random.randint(1, 100) <= 25: 
                user['wins'] += 1
                user['balance'] += 40
                is_victory = True
                txt = "🥚 ОПА! ПРЯМО В ЦІЛЬ!\nБот впав на коліна і заспівав тонким голосом. +40 зубів."
            else:
                user['balance'] -= 30
                txt = "🤡 Бот встиг згрупуватися. Твоя нога зустрілася з його коліном. -30 зубів."

        # 4. УДАР В ЩЕЛЕПУ
        elif data == "hit_jaw":
            user['daily_tasks']['hits_count'] += 1
            if random.randint(1, 100) <= 30:
                user['wins'] += 1
                user['balance'] += 25
                is_victory = True
                txt = "💥 Вдалий хук! Бот трохи поплив. +25 зубів."
            else:
                user['balance'] -= 20
                txt = "🤡 Ти махнув по повітрю, бот заїхав тобі в дихало. -20 зубів."
                
        # 5. ЛОУ-КІК
        elif data == "hit_leg":
            user['daily_tasks']['hits_count'] += 1
            if random.randint(1, 100) <= 35:
                user['wins'] += 1
                user['balance'] += 15
                is_victory = True
                txt = "🦶 Чітко підбив ногу. Бот похитнувся. +15 зубів."
            else:
                user['balance'] -= 15
                txt = "👟 Бот відійшов, ти ледь не сів на шпагат. -15 зубів."

        # 6. СПЛЮНУТИ
        elif data == "hit_spit":
            user['toxic_hits'] = user.get('toxic_hits', 0) + 1
            user['daily_tasks']['hits_count'] += 1 # Навіть плювок — це активність
            txt = "💦 Ти плюнув. Бот витерся твоїм же рукавом. Ситуація — гімно."

        # --- ПЕРЕВІРКА КВЕСТІВ ПІСЛЯ ДІЇ ---
        
        # Квест 1: Нанести 5 ударів
        if user['daily_tasks']['hits_count'] >= 5 and "hits" not in user['completed_tasks']:
            user['completed_tasks'].append("hits")
            user['balance'] += 50
            txt += "\n\n🎉 <b>КВЕСТ ВИКОНАНО!</b>\nНаніс 5 ударів: +50 зубів!"

        # Квест 2: Виграти 3 рази
        if is_victory:
            user['daily_tasks']['wins_today'] += 1
            if user['daily_tasks']['wins_today'] >= 3 and "wins" not in user['completed_tasks']:
                user['completed_tasks'].append("wins")
                user['balance'] += 100
                txt += "\n\n🎉 <b>КВЕСТ ВИКОНАНО!</b>\n3 перемоги за день: +100 зубів!"

        save_users(user_stats)
        if txt:
         await callback.message.edit_text(txt, parse_mode="HTML")
        await callback.answer()
 
    # КНП
    elif data.startswith("rsp_"):
        if user['balance'] < 10: return await callback.answer("❌ Мало бабок!", show_alert=True)
        user['balance'] -= 10
        user_choice = data.split("_")[1]
        bot_choice = random.choice(["rock", "scissors", "paper"])
        trans = {"rock": "🪨 Камінь", "scissors": "✂️ Ножиці", "paper": "📄 Папір"}
        
        if user_choice == bot_choice:
            user['balance'] += 10
            txt = f"🤝 Обидва викинули {trans[bot_choice]}. Нічия!"
        elif (user_choice == "rock" and bot_choice == "scissors") or \
             (user_choice == "scissors" and bot_choice == "paper") or \
             (user_choice == "paper" and bot_choice == "rock"):
            user['wins'] += 1
            user['balance'] += 20
            txt = f"🤬 Мій {trans[bot_choice]} програв твому {trans[user_choice]}. Забирай свої +20 зубів і йди нахуй тварь!"
        else:
            txt = f"😂Підарас! Мій {trans[bot_choice]} їбе твій {trans[user_choice]}! -10 зубів."

    await callback.message.edit_text(txt)
    await callback.answer()


# --- 6. ТОКСИЧНІ ВІДПОВІДІ ---
@dp.message()
async def toxic_replies(message: types.Message):
    if not message.text: return
    text = message.text.lower()

    fixed_replies = {
        "привіт": "Йо 😎", "ціна": "100 грн 💰", "піздец": "+++", "сука": "Сука то твоя мать",
        "йди нахуй": "інваліда пропускаю", "гандон": "Гандон в тебе на хуї", "блять": "не пизди на голову"
    }
    if text in fixed_replies: return await message.answer(fixed_replies[text])

    bad_words = ["хуй", "підар", "пизди", "пиздиш", "сучка", "шлюха", "дебіл", "ідіот", "пздц", "Fuck", "Shit", "Bitch", "дибіл", "хуйло", "підарас", "їбав", "дурак", "їбанько", "пізд", "єба", "йоба", "сука", "бля", "гандон", "лох", "чмо", "уїбан", "виродок", "даун", "підор", "завали", "маму їбав", "їбать", "мразь", "курва"]
    brutal_responses = [
        "Ти, помилка п'яної акушерки, закрий своє хлібало!",
        "Я твою родословну до п'ятого коліна на хую вертів, біосміття.",
        "Твоя мати реально шкодує, що не зробила аборт.",
        "Ще раз відкриєш свою пащу — я тебе так роз'їбу, що тебе рідна собака не впізнає!",
        "Ти — просто підар єбаний, генетичний відхід. Пиздуй нахуй!",
        "Чуєш, ти, виблядок недоношений, я твій рот їбав, переїбав і навиворіт вивертав!",
        "Ти, сука, пизда лиса, я твою родословну на хую вертів. Завали своє єбало немите!"
        "Чуєш ти, сука єбана, піздопройобіще недоношене, завали своє гниле єбало, поки я тобі в пельку не насрав так, що ти захлинешся власним лайном, виблядок ти йобаний!"
        "Якого хуя ти мені тут виписуєш, підор ти гнойовий, залупа ти кінська, йди нахуй звідси, поки я тобі твої криві ноги в дупу не запхав, щоб ти ними моргав, уїбан єбучий!"
        "Ти, блять, помилка природи, залупочес йобаний, твій рот — це зливний бачок для моєї сечі, так що закрий свою пащу, поки я туди не розрядився, гнидо немита!"
        "Слухай сюди, курва ти обригана, піздолиз недороблений, я твою мамку вчора так жарив, що в неї аж зуби посипалися, ти, виродок єбаний, шматок обісцяного матраца!"
        "Завали єбало, блять, шмара ти копієчна, я твій мозок через дупу висцу, якщо ти ще хоч раз щось гавкнеш в мій бік, виблядок ти йобаний, гниль піднігтьова!"
        "Якого, сука, хуя ти до мене лізеш, ти, піздокрил йобаний, залупа ти з вухами? Твоє місце біля параші, так що пиздуй туди і не відсвічуй своїм рилом обриганим!"
        "Чуєш ти, обісцяний валянок, хуєпльот йобаний, завали свій фонтан, бо я тобі зараз так в'їбу, що в тебе срака з ротом місцями поміняються, курва ти недоєбана!"
        "Ти що, блять, безсмертний став, уїбан ти недороблений, шматок пізди собачої? Я тебе живцем закопаю в тій ямі, де твоє нікчемне життя прогнило, сука ти йобана!"
        "Пиздуй нахуй, сука, поки я тобі твої яйця на вуха не натягнув, щоб ти чув, як вони тріщать під моїм гнітом, виблядок ти йобаний, шматок гівна недобитий!"
        "Чуєш ти, сука обригана, піздопройобіще єбане, залупоголовий виблядок недоношеної шмари, я твій рот, блять, єбав, переєбав, вивертав і на хую вертів, ти, гандон штопаний, спермоглот недороблений, підор гнойовий, уїбан кончений, шматок обісцяного матраца, завали своє гниле, смердюче хлібало, поки я тобі, гнидопаст йобаний, твої криві копита в дупу не забив, щоб ти ними моргав, курва ти привокзальна, спермобак обриганий, жертва невдалого аборту, піздокрил хуєсосний, я твою родословну до десятого коліна в кожну дірку штрикав, ти, виродок єбучий, шматок лайна собачого, залупочес немитий, я твій мозок через сраку висцу, якщо ти ще хоч раз, сука, гавкнеш, ти, недолюдок підорський, обісцяний валянок, хуєпльот недоєбаний, я тебе живцем у параші втоплю, шльондра ти дефіцитна, гниль піднігтьова, мудило горохове, піздолиз обісраний, я твій дім труба шатав, твою мамку в кіно водив і там же на ікла давав, ти, залупа кінська, виблядок обриганий, чепушило ти підпарканне, пиздуй нахуй малими кроками, поки я тобі твій єбальник не розвальцював до розмірів каналізаційного люка, ти, гівно залежале, підормот йобаний, задрот піздоголовий, шмара ти копієчна, я тебе так роз'їбу, що тебе рідна собака не впізнає, коли ти будеш свої кишки по району збирати, сука ти кончена, піздобол, уєбан, гавно, залупа!"
    ]

    if any(word in text for word in bad_words):
        update_stat(message.from_user.id, "toxic_hits")
        await message.answer(random.choice(brutal_responses))


# --- ЗАПУСК ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

