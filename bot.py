import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Налаштування логів
logging.basicConfig(level=logging.INFO)

TOKEN = "8246610126:AAHh6B6c89VaD_g9XSHBQwJNRHgPWVJJAa4"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Сховище статистики
user_stats = {}

# --- ДОПОМІЖНІ ФУНКЦІЇ ---
def get_user_data(uid):
    if uid not in user_stats:
        # Додали "inventory" для магазину
        user_stats[uid] = {"wins": 0, "deaths": 0, "toxic_hits": 0, "balance": 100, "inventory": {"knuckles": 0, "armor": 0}}
    
    # Заглушка для старих гравців, щоб код не впав, якщо в них ще нема інвентарю
    if "inventory" not in user_stats[uid]:
        user_stats[uid]["inventory"] = {"knuckles": 0, "armor": 0}
        
    return user_stats[uid]

def update_stat(uid, key, amount=1):
    user = get_user_data(uid)
    user[key] += amount

def get_rank(wins):
    if wins >= 100: return "👑 Смотрящий за районом"
    if wins >= 50:  return "🦅 Авторитет"
    if wins >= 25:  return "👊 Боєць"
    if wins >= 10:  return "👟 Пацан"
    if wins >= 5:   return "🤏 Шнирь"
    return "🤡 Тєрпіла"


# --- 1. БАЗОВІ КОМАНДИ ---
@dp.message(CommandStart())
async def start(message: types.Message):
    get_user_data(message.from_user.id)
    await message.answer("Привіт 👋 Я працюю! Напиши /help, щоб побачити, на що я здатний.")

@dp.message(Command("help"))
async def help_command(message: types.Message):
    help_text = (
        "❓ **Шо ти вилупився? Ось список команд:**\n\n"
        "🛒 **ЧОРНИЙ РИНОК:**\n"
        "🏪 `/shop` — Купити кастет, бронік або пиво\n\n"
        "🎮 **ІГРИ ТА КАЗИНО:**\n"
        "👊 `/fight` — Махач на районі\n"
        "🔫 `/roulette` — Львівська рулетка\n"
        "✌️ `/rsp` — Камінь, ножиці, папір\n"
        "🎰 `/slots` — Однорукий бандит (ставка: 10 зубів)\n"
        "🎲 `/dice` — Кинути кубик (ставка: 10 зубів)\n"
        "🎳 `/bowling` — Збити кеглі (ставка: 10 зубів)\n"
        "⚔️ `/duel` — Визвати на дуель (відповісти на повідомлення)\n\n"
        "📊 **ІНФО:**\n"
        "💰 `/balance` — Глянути свої фінанси\n"
        "📈 `/my_stats` — Твої успіхи\n"
        "🏆 `/top` — ТОП-5 найбагатших на районі\n"
    )
    try:
        await message.answer(help_text, parse_mode="Markdown")
    except Exception:
        await message.answer(help_text.replace("*", "").replace("`", ""))


# --- 2. МАГАЗИН (/shop) ---
@dp.message(Command("shop"))
async def open_shop(message: types.Message):
    user = get_user_data(message.from_user.id)
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🥊 Кастет (200 зубів)", callback_data="buy_knuckles"))
    builder.row(types.InlineKeyboardButton(text="🦺 Бронік (500 зубів)", callback_data="buy_armor"))
    builder.row(types.InlineKeyboardButton(text="🍺 Пиво (50 зубів)", callback_data="buy_beer"))
    
    text = (
        "🛒 **Місцевий Барига на зв'язку.**\n\n"
        f"💰 Твої бабки: {user['balance']} зубів\n\n"
        "📦 **В наявності:**\n"
        "🥊 **Кастет** — 100% перемога в наступній бійці з ботом.\n"
        "🦺 **Бронік** — Рятує життя в рулетці від 1 кулі.\n"
        "🍺 **Пиво Львівське Різдвяне** — Просто попити пивка (+1 до авторитету).\n\n"
        "Шо треба? Купуй або пиздуй звідси:"
    )
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")


# --- 3. СТАТИСТИКА, БАЛАНС ТА ТОП ---
@dp.message(Command("balance"))
async def show_balance(message: types.Message):
    user = get_user_data(message.from_user.id)
    balance = user['balance']
    
    await message.answer(f"💰 **Твій баланс:** {balance} зубів\n📦 Кастетів: {user['inventory']['knuckles']} | Броніків: {user['inventory']['armor']}", parse_mode="Markdown")

@dp.message(Command("my_stats"))
async def show_stats(message: types.Message):
    s = get_user_data(message.from_user.id)
    rank = get_rank(s['wins'])

    res = (
        f"📊 **Твій послужний список, {message.from_user.first_name}:**\n"
        f"🎖 Твій статус: `{rank}`\n\n"
        f"💰 Баланс: {s['balance']} зубів\n"
        f"📦 Кармани: 🥊x{s['inventory']['knuckles']} | 🦺x{s['inventory']['armor']}\n"
        f"🏆 Перемог у бійках: {s['wins']}\n"
        f"💀 Смертей у рулетці: {s['deaths']}\n"
        f"🤬 Принижень від бота: {s['toxic_hits']}\n"
    )
    await message.answer(res, parse_mode="Markdown")

@dp.message(Command("top"))
async def show_top(message: types.Message):
    if not user_stats:
        return await message.answer("🤷‍♂️ Поки що ніхто не виходив на зв'язок.")

    sorted_users = sorted(user_stats.items(), key=lambda x: x[1]['balance'], reverse=True)[:5]
    top_text = "🏆 **ТОП-5 ОЛІГАРХІВ РАЙОНУ:**\n\n"
    for i, (uid, stats) in enumerate(sorted_users, 1):
        try:
            user_info = await bot.get_chat(uid)
            name = user_info.first_name
        except:
            name = f"ID:{uid}"
        
        rank = get_rank(stats['wins'])
        top_text += f"{i}. {name} — 💰{stats['balance']} зубів ({rank})\n"

    await message.answer(top_text)


# --- 4. КАЗИНО ТА ІГРИ З КНОПКАМИ ---
@dp.message(Command("slots"))
async def play_slots(message: types.Message):
    user = get_user_data(message.from_user.id)
    if user['balance'] < 10:
        return await message.answer("❌ У тебе немає 10 зубів на ставку!")
    user['balance'] -= 10
    msg = await message.answer_dice(emoji="🎰")
    await asyncio.sleep(2)
    score = msg.dice.value
    if score == 64:
        user['balance'] += 500
        await message.answer("🎰 ДЖЕКПОТ, СУКА! 💰 +500 зубів!")
    elif score in [1, 22, 43]:
        user['balance'] += 30
        await message.answer("💵 Опа, шось насипало. +30 зубів.")
    else:
        await message.answer("🤡 ЛОХ! Автомат тебе роззув. -10 зубів.")

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
    builder.row(types.InlineKeyboardButton(text="👊 В щелепу", callback_data="hit_jaw"))
    builder.row(types.InlineKeyboardButton(text="🦶 Лоу-кік", callback_data="hit_leg"))
    builder.row(types.InlineKeyboardButton(text="💨 Тікати", callback_data="run_away"))
    await message.answer("Ти на кого батон кришиш? Вибирай дію:", reply_markup=builder.as_markup())

@dp.message(Command("roulette"))
async def start_roulette(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💀 Тиснути на гачок", callback_data="pull_trigger"))
    await message.answer("Ну шо, заграємо в лотерею для дебілів? 🔫", reply_markup=builder.as_markup())

@dp.message(Command("rsp"))
async def start_rsp(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🪨 Камінь", callback_data="rsp_rock"))
    builder.row(types.InlineKeyboardButton(text="✂️ Ножиці", callback_data="rsp_scissors"))
    builder.row(types.InlineKeyboardButton(text="📄 Папір", callback_data="rsp_paper"))
    await message.answer("Давай на пальцях! (Ставка 10 зубів). Вибирай:", reply_markup=builder.as_markup())

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
@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    uid = callback.from_user.id
    data = callback.data
    user = get_user_data(uid)

    # ОБРОБКА ПОКУПОК У МАГАЗИНІ
    if data.startswith("buy_"):
        item = data.split("_")[1]
        if item == "knuckles":
            if user['balance'] >= 200:
                user['balance'] -= 200
                user['inventory']['knuckles'] += 1
                return await callback.answer("✅ Ти купив Кастет! Наступна бійка за тобою.", show_alert=True)
            else: return await callback.answer("❌ Бомж! Тобі не вистачає зубів на кастет.", show_alert=True)
        elif item == "armor":
            if user['balance'] >= 500:
                user['balance'] -= 500
                user['inventory']['armor'] += 1
                return await callback.answer("✅ Ти купив Бронік! Тепер рулетка не така страшна.", show_alert=True)
            else: return await callback.answer("❌ Грошей нема! Іди грай в слоти.", show_alert=True)
        elif item == "beer":
            if user['balance'] >= 50:
                user['balance'] -= 50
                user['wins'] += 1 # Даємо +1 перемогу за понти
                return await callback.answer("🍺 Ти випив Жигулівського і ригнув. +1 до авторитету.", show_alert=True)
            else: return await callback.answer("❌ Навіть на пиво не заробив. Фу.", show_alert=True)

    # ДУЕЛЬ
    if data.startswith("accept_"):
        parts = data.split("_")
        opponent_id, challenger_id = int(parts[1]), int(parts[2])
        if uid != opponent_id: return await callback.answer("❌ Це не тебе викликали!", show_alert=True)
        
        winner = random.choice([opponent_id, challenger_id])
        loser = opponent_id if winner == challenger_id else challenger_id
        update_stat(winner, "wins")
        update_stat(winner, "balance", 50)
        update_stat(loser, "balance", -50)
        w_name = (await bot.get_chat(winner)).first_name
        l_name = (await bot.get_chat(loser)).first_name
        txt = f"💥 {w_name} розмазав {l_name}! {w_name} забирає 50 зубів у лоха!"
        await callback.message.edit_text(txt)
        return await callback.answer()

    # БІЙКА З БОТОМ (ІЗ КАСТЕТОМ)
    if data in ["hit_jaw", "hit_leg"]:
        if user['inventory']['knuckles'] > 0:
            user['inventory']['knuckles'] -= 1
            user['wins'] += 1
            user['balance'] += 50
            txt = "🥊 **ТИ ДІСТАВ КАСТЕТ!** Удар в щелепу... Бот у нокауті! Ти переміг на ізі! Кастет зламався. +50 зубів."
        elif random.randint(1, 100) > 50:
            user['wins'] += 1
            user['balance'] += 20
            txt = "💥 Красава! Ти його вирубив. +20 зубів і +1 перемога."
        else:
            user['balance'] -= 10
            txt = "🤡 Тобі натягнули око на сраку. Відпочивай. -10 зубів."
    elif data == "run_away":
        txt = "🏃‍♂️ Ти втік як остання шмара."

    # РУЛЕТКА (З БРОНІКОМ)
    elif data == "pull_trigger":
        if random.randint(1, 6) == 1:
            if user['inventory']['armor'] > 0:
                user['inventory']['armor'] -= 1
                txt = "💥 **БАБАХ!** ... Але куля застрягла у твоєму БРОНІКУ! Ти вижив, сука. Бронік розірвало вхлам."
            else:
                user['deaths'] += 1
                txt = "💥 БАБАХ! Твої мізки на стіні. Земля тобі гівном."
        else:
            txt = "🛡 *Клац.* Тобі пощастило, виродок. Живий."

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
            txt = f"🤬 Мій {trans[bot_choice]} програв твому {trans[user_choice]}. Забирай свої +20 зубів!"
        else:
            txt = f"😂 ЛОХ! Мій {trans[bot_choice]} б'є твій {trans[user_choice]}! -10 зубів."

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

    bad_words = ["хуй", "пздц", "пізд", "єба", "йоба", "сука", "бля", "гандон", "лох", "чмо", "уїбан", "виродок", "даун", "підор", "завали", "маму їбав", "їбать", "мразь", "курва"]
    brutal_responses = [
        "Ти, помилка п'яної акушерки, закрий своє хлібало!",
        "Я твою родословну до п'ятого коліна на хую вертів, біосміття.",
        "Твоя мати реально шкодує, що не зробила аборт.",
        "Ще раз відкриєш свою пащу — я тебе так роз'їбу, що тебе рідна собака не впізнає!",
        "Ти — просто підар єбаний, генетичний відхід. Пиздуй нахуй!",
        "Чуєш, ти, виблядок недоношений, я твій рот їбав, переїбав і навиворіт вивертав!",
        "Ти, сука, пизда лиса, я твою родословну на хую вертів. Завали своє єбало немите!"
    ]

    if any(word in text for word in bad_words):
        update_stat(message.from_user.id, "toxic_hits")
        await message.answer(random.choice(brutal_responses))


# --- ЗАПУСК ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())
