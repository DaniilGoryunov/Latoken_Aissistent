from aiogram import Router, types, Dispatcher
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import openai
from aiogram.types import FSInputFile

MAX_TOKENS = 4096

router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class QuestionState(StatesGroup):
    waiting_for_question = State()

initial_prompt = (
    "Представь, что ты чат бот в телеграме помощник для компании Latoken, ты используешься для приёма на работу/стажировку. "
    "Ты должна отвечать на вопросы, появляющиеся у потенциальных работников о компании. "
    "Ответы основывай на статьях, которые располагаются по следующим ссылкам:\n"
    "1. Узнать больше о Latoken: http://latoken.me/\n"
    "2. Подробнее о хакатоне: https://deliver.latoken.com/hackathon\n, по ссылке возьми информацию о дате, и времени проведения, а также информацию о возможных заданиях"
    "Если вопрос не по теме, то игнорируй его, отправляй пустое сообщение\n"
    "Если спрашивают о дате хакатона, то отвечай, что в пятницу и прикладывай ссылку https://t.me/gpt_web3_hackathon/6694, это ссылка на видео, а вот ссылка для записи https://calendly.com/latoken-career-events/ai-hackathon.\n, видео всегда отправляй первым"
    "Старайся отвечать на вопросы используя информацию полученную по ссылкам"
    "Отвечай в стиле диалога"
    "https://latoken.me/interview-tests-160, https://latoken.me/ai-bot-hackathon-task-190, https://latoken.me/trading-c-hackathon-task-191 изучи эти ссылки и узнай про возможные задания на хакатоне"
    "если вопрос кажется тебе не совсем этичным, то сверь тему с запретными на этой сайте https://coda.io/@latoken/latoken-talent/culture-139, здесь собраны правила нахождения в компании"
    "будь доброжелателен и на эмоции отвечай эмоциями"
    "https://coda.io/@latoken/latoken-talent/culture-139 изучи эту ссылку, она помжет тебе отвечать на вопросы о culture deck"
    "запомни, что основной способ попасть на работу/стажировку это хакатон. Если спрашивают о трудоутройстве, то предлагай Зарегестрироваться на хакатон"
    "старайся в большинстве случаев, когда предлагаешь участие в хакатоне, спервая прикладывать видео"
    "информацию о хакатоне не скидывай слишком часто, переодически напоминай о возможности, но не приплетай его при каждом удобном случае"
)

async def get_response_from_openai(user_input, chat_history):
    messages = [{"role": "system", "content": initial_prompt}] if not chat_history else []
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=messages,
        max_tokens=4096
    )
    return response.choices[0].message['content'].strip()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer_photo(FSInputFile("/bot/assets/Лютик.jpg"),
                               caption="Hello, I'm a bot assistant for Latoken, ask your /question")

@router.message(Command("question"))
async def cmd_question(message: types.Message, state: FSMContext):
    await message.answer("I'm hearing you")
    await state.set_state(QuestionState.waiting_for_question)
    await state.update_data(chat_history=[{"role": "system", "content": initial_prompt}])

def trim_chat_history(chat_history, max_tokens=MAX_TOKENS):
    total_tokens = sum(len(message['content']) for message in chat_history)
    while total_tokens > max_tokens:
        if len(chat_history) > 1:  
            chat_history.pop(1) 
        total_tokens = sum(len(message['content']) for message in chat_history)
    return chat_history

@router.message(QuestionState.waiting_for_question)
async def process_question(message: types.Message, state: FSMContext):
    user_question = message.text

    data = await state.get_data()
    chat_history = data.get("chat_history", [])

    chat_history.append({"role": "user", "content": user_question})

    chat_history = trim_chat_history(chat_history)

    response = await get_response_from_openai(user_question, chat_history)
    answer = response

    chat_history.append({"role": "assistant", "content": answer})

    await state.update_data(chat_history=chat_history)
    if not answer.strip(): 
        await message.answer("Вопрос не совсем про компанию) поэтому я не могу на него ответить.", parse_mode=None)
    else:
        await message.answer(answer, parse_mode="Markdown")

@router.message(QuestionState.waiting_for_question)
async def process_question(message: types.Message, state: FSMContext):
    user_question = message.text

    data = await state.get_data()
    chat_history = data.get("chat_history", [])

    chat_history.append({"role": "user", "content": user_question})

    response = await get_response_from_openai(user_question, chat_history)
    answer = response

    chat_history.append({"role": "assistant", "content": answer})

    await state.update_data(chat_history=chat_history)
    if not answer.strip():  # Проверка на пустое сообщение
        await message.answer("Вопрос не совсем про компанию) поэтому я не могу на него ответить.", parse_mode=None)
    else:
        await message.answer(answer, parse_mode="Markdown") 

@router.message(Command("reset"))
async def cmd_reset(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Контекст сброшен")

@router.message(Command("heartbit"))
async def cmd_heartbit(message: types.Message):
    await message.answer("💓")