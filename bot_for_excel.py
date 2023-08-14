"""
API for telegram
"""
import json
import aiofiles as aiofiles

from google_sheet_excel import *
from keys import bot_token, username_technical_officer, userid_technical_officer, puzzle_code_page_support

from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from telegram import Bot

bot = Bot(token=bot_token)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    print(user.mention_html())
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(f"Привет! Я бот-помощник - {puzzle_code_page_support}. \n"
                                    "Я могу выполнить следующие команды: \n"
                                    "/start - Начать взаимодействие с ботом или сбросить данные. \n"
                                    "/help - Отобразить список доступных команд и их описания. \n"
                                    "/info - Получить информацию. \n"
                                    "/support - Если нужен помощь, отправь команду, к тебе выйдет сотрудник. \n"
                                    "/TagStudents - Отметить студентов на уроке.\n"
                                    f"Если нужен помощью смело напиши {username_technical_officer}")


# отметить учеников на уроке
async def tag_students(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """tag students in class"""
    # читаем ФИО из Excel
    students = obj.read_excel_file()

    keyboard: list = []
    # students_dict:dict = dict()
    for student in students['values'][1:]:
        #  создаем кнопки с ФИО
        keyboard.append(
            [
                InlineKeyboardButton(rf"{student[1]}", callback_data=rf"{student[0]}"),
            ],
        )
        # #  подготваливаем данные для записи в файл
        # students_dict[student[0]] = "Не был на уроке"

    #  создаем кнопку записать
    keyboard.append(
        [
            InlineKeyboardButton(rf"Записать", callback_data=rf"Записать"),
        ],
    )

    # создаем новый  файл 'data.json'
    async with aiofiles.open('data.json', mode="w") as file:
        await file.write(json.dumps({}, indent=4, ensure_ascii=False))
    # pprint(keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


# обработка нажати на кнопки с ФИО
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    try:
        # читаем из файл ФИО
        async with aiofiles.open('data.json', mode="r") as file:
            content = await file.read()
            data = json.loads(content)
        pprint(data)
        if query.data == "Записать":
            write_data = await obj.add_new_rows_in_excel()
            await query.edit_message_text(text=f"Selected option: {query.data}")
        else:
            data.update({rf"{query.data}": "На уроке", })
            # записываем новые данные в файл 'data.json'
            async with aiofiles.open('data.json', mode="w") as file:
                await file.write(json.dumps(data, indent=4, ensure_ascii=False))

    except:
        await query.message.reply_text(
            rf"произашло техническая ошибка, отметье учеников по ссылке в google excel")
        # Отправка сообщения при технической ошибке
        await bot.send_message(chat_id=rf'{userid_technical_officer}',
                               text="Привет! При отметке учеников произашло ошибка! file_name: bot_for_excel.py in "
                                    "line 52-70")

    '''
    # читаем из файл ФИО
    async with aiofiles.open('data.json', mode="r") as file:
        content = await file.read()
        data = json.loads(content)

    try:
        print(query.data)
        if query.data in data:
            data[query.data] = 'На уроке'
            pprint(data)
        elif query.data == 'Записать':
            # записываем новые данные в файл 'data.json'
            async with aiofiles.open('data.json', mode="w") as file:
                await file.write(json.dumps(data, indent=4, ensure_ascii=False))
            await query.edit_message_text(text=f"Selected option: {query.data}")

    except: await query.message.reply_text(rf"произашло техническая ошибка, напишите {username_technical_officer} или 
    заполните по ссылке в файле") # Отправка сообщения await query.message.reply_text(chat_id=rf'{
    userid_technical_officer}', text="Привет! При отметке учеников произашло ошибка! file_name: bot_for_excel.py in 
    line 52-70") '''


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(rf"Неверный запрос, повторите запрос или обратитесь к {username_technical_officer}")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("TagStudents", tag_students))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
