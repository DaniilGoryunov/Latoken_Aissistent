from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
import openai

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer_photo(FSInputFile("/bot/assets/Лютик.jpg"),
                               caption="Hello, I'm a bot assistant for Latoken, ask your question")

@router.message(Command("question"))
async def cmd_question(message: types.Message):
    user_question = message.text[len("/question "):]  # Извлекаем текст вопроса
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",  # Укажите нужную вам модель
        messages=[{"role": "user", "content": user_question}]
    )
    answer = response.choices[0].message['content'].strip()
    await message.answer(answer)