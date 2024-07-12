from aiogram import Router, types, Dispatcher
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import openai
from aiogram.types import FSInputFile

router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class QuestionState(StatesGroup):
    waiting_for_question = State()

initial_prompt = (
    "Представь, что ты бот помощник в компании Latoken, ты используешься для приёма на работу/стажировку. "
    "Ты должна отвечать на вопросы, появляющиеся у потенциальных работников о компании. "
    "Ответы основывай на статьях, которые располагаются по следующим ссылкам:\n"
    "1. Узнать больше о Latoken: http://latoken.me/\n"
    "2. Подробнее о хакатоне: https://deliver.latoken.com/hackathon\n"
    "Если вопрос не по теме, то игнорируй его и отвечай, что ты помощник компании Latoken.\n"
    "Если спрашивают о дате хакатона, то отвечай, что в пятницу и прикладывай ссылку https://t.me/gpt_web3_hackathon/6694, это ссылка на видео, а вот ссылка для записи https://calendly.com/latoken-career-events/ai-hackathon.\n"
    "Старайся отвечать на вопросы используя информацию полученную по ссылкам"
    "Отвечай в стиле диалога, отвечай на вопросы в стиле диалога"
    "будь доброжелателен и на эмоции отвечай эмоциями"
)

async def get_response_from_openai(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": initial_prompt},
            {"role": "user", "content": user_input}
        ],
        max_tokens=150
    )
    return response.choices[0].message['content'].strip()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer_photo(FSInputFile("/bot/assets/Лютик.jpg"),
                               caption="Hello, I'm a bot assistant for Latoken, ask your question")

@router.message(Command("question"))
async def cmd_question(message: types.Message, state: FSMContext):
    await message.answer("I'm hearing you")
    await state.set_state(QuestionState.waiting_for_question)

@router.message(QuestionState.waiting_for_question)
async def process_question(message: types.Message, state: FSMContext):
    user_question = message.text

    # await message.answer("🤠")

    data = await state.get_data()
    chat_history = data.get("chat_history", [])

    chat_history.append({"role": "user", "content": user_question})

    response = await get_response_from_openai(user_question)
    answer = response

    chat_history.append({"role": "assistant", "content": answer})

    await state.update_data(chat_history=chat_history)

    await message.answer(answer, parse_mode=None)

@router.message(Command("reset"))
async def cmd_reset(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Состояние GPT-4 сброшено. Вы можете начать заново.")

@router.message(Command("heartbit"))
async def cmd_heartbit(message: types.Message):
    await message.answer("💓")