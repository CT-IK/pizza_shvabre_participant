import os
import json

from aiogram import types, Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from states import Game21, Profile
from databases.game21_db import load_games, save_game
from databases.database import save_participant, participant_exists

private_router = Router()

GROUP_ID = int(os.getenv("GROUP_ID"))

#старт
@private_router.message(CommandStart(), F.chat.type == "private")
async def start_cmd(message: types.Message):
    start_message = (
        'Привет участник ША2!\n\n'
        'Используй !заполнить и возвращайся в чат\n\n'
        'Также тебе доступны команды:\n'
        '!анон [текст] - факт, автора которого будут угадывать в чате\n'
        '!игра21 - 2 правды 1 ложь\n\n' 
        'При обнаружении ошибок пишем @Pockemon05'
    )
    await message.answer(start_message)

#anon
@private_router.message(Command('анон', prefix='!'), F.chat.type == "private")
async def anon_cmd(message: types.Message, bot: Bot):
    text = message.text.replace('!анон', '', 1).strip()
    if not text:
        await message.answer("Напиши текст после команды")
        return
    username = message.from_user.username
    fact = text[0].upper() + text[1:]
    send = f'Новый анонимный факт!\n\n"{fact}"\n\nПопробуйте угадать кто это'
    send_message = await bot.send_message(
        chat_id=GROUP_ID,
        text=send
    )
    save_game(send_message.message_id, {
        "type": "anon", 
        "author": username
    })
    await message.answer("Анонимный факт отправлен в группу ✅")

#game21
@private_router.message(F.text == '!игра21', F.chat.type == "private")
async def game_start(message: types.Message, state: FSMContext):
    send = ('Это игра 2 правды 1 ложь\n\n'
            'Напиши первый факт о себе:')
    await message.answer(send)
    await state.set_state(Game21.fact1)

@private_router.message(Game21.fact1, F.chat.type == "private")
async def game_continue1(message: types.Message, state: FSMContext):
    await state.update_data(fact1=message.text)
    await message.answer('Напиши второй факт о себе:')
    await state.set_state(Game21.fact2)

@private_router.message(Game21.fact2, F.chat.type == "private")
async def game_continue2(message: types.Message, state: FSMContext):
    await state.update_data(fact2=message.text)
    await message.answer('Напиши третий факт о себе:')
    await state.set_state(Game21.fact3)

@private_router.message(Game21.fact3, F.chat.type == "private")
async def game_continue3(message: types.Message, state: FSMContext):
    await state.update_data(fact3=message.text)
    await message.answer('Выбери какой факт будет ложным\nНапиши цифрой (1/2/3)')
    await state.set_state(Game21.false_fact)

@private_router.message(Game21.false_fact, F.chat.type == "private")
async def game_continue4(message: types.Message, state: FSMContext, bot: Bot):
    if message.text not in ['1', '2', '3']:
        await message.answer("Пожалуйста, введи только цифру: 1, 2 или 3")
        return
    await state.update_data(false_fact = message.text)
    data = await state.get_data()
    username = message.from_user.username
    send = (
        f'Игра 2 правды 1 ложь от @{username}:\n\n'
        f'1) {data["fact1"]}\n'
        f'2) {data["fact2"]}\n'
        f'3) {data["fact3"]}\n\n'
        'Пишите номер факта, ответом на это сообщение, который считаете ложным'
    )
    send_message = await bot.send_message(
        chat_id=GROUP_ID,
        text=send
    )

    save_game(send_message.message_id, { 
        "type": "game21",
        "false_fact": data["false_fact"],
        "author": username
    })
    
    await message.answer("Факты отправлены в группу") 
    await state.clear()

#обработка ответов
@private_router.message(
    F.chat.id == GROUP_ID,
    F.reply_to_message.from_user.is_bot,
)
async def check_group_answer(message: types.Message, bot: Bot):
    games = load_games()
    reply_id = str(message.reply_to_message.message_id)
    if reply_id not in games:
        return
    game = games[reply_id]

    if game.get("type") == "game21":
        if message.text not in ['1', '2', '3']:
            return
        if message.text == game["false_fact"]:
            winner = message.from_user.username or message.from_user.first_name
            await bot.send_message(
                chat_id=GROUP_ID,
                text=(
                    f'🎉 @{winner} угадал!\n'
                    f'Ложный факт был №{game["false_fact"]}\n'
                    f'Автор: @{game["author"]}'
                )
            )
            games.pop(reply_id)
            with open('databases/active_games.json', 'w', encoding='utf-8') as f:
                json.dump(games, f, ensure_ascii=False, indent=4)

    elif game.get("type") == "anon":
        if message.text.strip() == f"@{game['author']}":
            winner = message.from_user.username or message.from_user.first_name
            await bot.send_message(
                chat_id=GROUP_ID,
                text=(
                    f'🎉 @{winner} угадал автора анонимного факта!\n'
                    f'Автор: @{game["author"]}'
                )
            )
            games.pop(reply_id)
            with open('databases/active_games.json', 'w', encoding='utf-8') as f:
                json.dump(games, f, ensure_ascii=False, indent=4)

    elif game.get("type") == "whois":
        if message.text.strip() == f"@{game['author']}":
            winner = message.from_user.username or message.from_user.first_name
            await bot.send_message(
                chat_id=GROUP_ID,
                text=(
                    f'🎉 @{winner} угадал автора анонимного факта!\n'
                    f'Автор: @{game["author"]}'
                )
            )
            games.pop(reply_id)
            with open('databases/active_games.json', 'w', encoding='utf-8') as f:
                json.dump(games, f, ensure_ascii=False, indent=4)


#профиль
@private_router.message(Command('заполнить', prefix='!'), F.chat.type == "private")
async def prof_start(message: types.Message, state: FSMContext):
    username = message.from_user.username
    if participant_exists(username):
        await message.answer(
            "У вас уже есть профиль в базе!\n"
        )
        return

    await message.answer('Как тебя зовут?')
    await state.set_state(Profile.name)

@private_router.message(Profile.name, F.chat.type == "private")
async def prof_continue1(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Сколько тебе лет?')
    await state.set_state(Profile.age)

@private_router.message(Profile.age, F.chat.type == "private")
async def prof_continue2(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('Когда ты родился?\n(Напиши в формате ДД.ММ.ГГГГ)')
    await state.set_state(Profile.date)

@private_router.message(Profile.date, F.chat.type == "private")
async def prof_continue3(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer('С какого ты факультета?')
    await state.set_state(Profile.faculty)

@private_router.message(Profile.faculty, F.chat.type == "private")
async def prof_continue4(message: types.Message, state: FSMContext):
    await state.update_data(faculty=message.text)
    await message.answer('Какое у тебя хобби?')
    await state.set_state(Profile.hobby)

@private_router.message(Profile.hobby, F.chat.type == "private")
async def prof_continue5(message: types.Message, state: FSMContext):
    await state.update_data(hobby=message.text)
    await message.answer('Около какого метро/станции МЦД живешь сейчас?')
    await state.set_state(Profile.metro)

@private_router.message(Profile.metro, F.chat.type == "private")
async def prof_continue5(message: types.Message, state: FSMContext):
    await state.update_data(metro=message.text)
    await message.answer('В каком городе жил до поступления?')
    await state.set_state(Profile.city)

@private_router.message(Profile.city, F.chat.type == "private")
async def prof_continue6(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer('Напиши необычный факт о себе')
    await state.set_state(Profile.fact)

@private_router.message(Profile.fact, F.chat.type == "private")
async def prof_continue7(message: types.Message, state: FSMContext):
    await state.update_data(fact=message.text)
    await message.answer('Напиши свою любимую фразу/цитату')
    await state.set_state(Profile.phrase)

@private_router.message(Profile.phrase, F.chat.type == "private")
async def prof_continue1(message: types.Message, state: FSMContext):
    await state.update_data(phrase=message.text)
    data = await state.get_data()
    send = (
        'Вот твой профиль:\n\n'
        f'Имя: {data.get("name", "")}\n'
        f'Возраст: {data.get("age", "")}\n'
        f'Дата рождения: {data.get("date", "")}\n'
        f'Факультет: {data.get("faculty", "")}\n'
        f'Хобби: {data.get("hobby", "")}\n'
        f'Метро: {data.get("metro", "")}\n'
        f'Необычный факт: {data.get("fact", "")}\n'
        f'Любимая фраза: {data.get("phrase", "")}\n\n'
        'Если тебя все устраивает напиши "Да", если хочешь переделать напиши "Нет"'
    )
    await message.answer(send)
    await state.set_state(Profile.approval)

@private_router.message(Profile.approval, F.chat.type == "private")
async def prof_approval(message: types.Message, state: FSMContext):
    answer = message.text.lower().strip()
    data = await state.get_data()
    username = message.from_user.username

    if answer == "да":
        data["username"] = username
        save_participant(data)
        await message.answer("Профиль успешно сохранён в базе данных!")
        await state.clear() 
    elif answer == "нет":
        await message.answer("Хорошо, начнём заново. Как тебя зовут?")
        await state.set_state(Profile.name)
    else:
        await message.answer('Пожалуйста, напиши только "Да" или "Нет"')
