from aiogram import Router, types, Dispatcher, Bot
from aiogram.filters import Command, Text, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import openai
from aiogram.types import FSInputFile
import os

MAX_TOKENS = 4096
ADMIN_ID = os.getenv("ADMIN") 

router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class QuestionState(StatesGroup):
    waiting_for_question = State()

class TestState(StatesGroup):
    question_1 = State()
    question_2 = State()
    question_3 = State()
    question_4 = State()
    question_5 = State()
    question_6 = State()
    question_7 = State()
    question_8 = State()
    question_9 = State()
    question_10 = State()
    question_11 = State()

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
    "https://coda.io/@latoken/latoken-talent/culture-139 если ответ на вопрос находится по этой ссылке, то используй форму RAG для ответа, знай, что по ссылке находится culture deck компании"
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

@router.message(Command("reset"), StateFilter("*"))
async def cmd_reset(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Контекст сброшен")

@router.message(Command("heartbit"), StateFilter("*"))
async def cmd_heartbit(message: types.Message):
    await message.answer("💓")

@router.message(Command("test"), StateFilter("*"))
async def cmd_test(message: types.Message, state: FSMContext):
    await message.answer("Какие из этих материалов вы прочитали?\n1. О Хакатоне deliver.latoken.com/hackathon\n2. О Латокен deliver.latoken.com/about\n3. Большая часть из #nackedmanagement coda.io/@latoken/latoken-talent/nakedmanagement-88")
    await state.set_state(TestState.question_1)

@router.message(TestState.question_1)
async def process_test_question_1(message: types.Message, state: FSMContext):
    await state.update_data(answer_1=message.text)
    await message.answer("Какой призовой фонд на Хакатоне?\n1. 25,000 Опционов\n2. 100,000 Опционов или 10,000 LA\n3. Только бесценный опыт")
    await state.set_state(TestState.question_2)

@router.message(TestState.question_2)
async def process_test_question_2(message: types.Message, state: FSMContext):
    await state.update_data(answer_2=message.text)
    await message.answer("Что от вас ожидают на хакатоне в первую очередь?\n1. Показать мои способности узнавать новые технологии\n2. Показать работающий сервис\n3. Продемонстрировать навыки коммуникации и командной работы")
    await state.set_state(TestState.question_3)

@router.message(TestState.question_3)
async def process_test_question_3(message: types.Message, state: FSMContext):
    await state.update_data(answer_3=message.text)
    await message.answer("Что из этого является преимуществом работы в Латокен?\n1. Быстрый рост через решение нетривиальных задач\n2. Передовые технологии AIxWEB3\n3. Глобальный рынок, клиенты в 200+ странах\n4. Возможность совмещать с другой работой и хобби\n5. Самая успешная компания из СНГ в WEB3\n6. Удаленная работа, но без давншифтинга\n7. Оплата в твердой валюте, без привязки к банкам\n8. Опционы с 'откешиванием' криптолетом\n9. Комфортная среда для свободы творчества")
    await state.set_state(TestState.question_4)

@router.message(TestState.question_4)
async def process_test_question_4(message: types.Message, state: FSMContext):
    await state.update_data(answer_4=message.text)
    await message.answer("Каковы Ваши зарплатные ожидания в USD?")
    await state.set_state(TestState.question_5)

@router.message(TestState.question_5)
async def process_test_question_5(message: types.Message, state: FSMContext):
    await state.update_data(answer_5=message.text)
    await message.answer("Какое расписание Хакатона корректнее?\n1. Пятница: 18:00 Разбор задач. Суббота: 18:00 Демо результатов, 19-00 объявление победителей, интервью и офферы\n2. Суббота: 12:00 Презентация компании, 18:00 Презентации результатов проектов")
    await state.set_state(TestState.question_6)

@router.message(TestState.question_6)
async def process_test_question_6(message: types.Message, state: FSMContext):
    await state.update_data(answer_6=message.text)
    await message.answer("Каковы признаки 'Wartime CEO' согласно крупнейшему венчурному фонду a16z?\n1. Сосредотачивается на общей картине и дает сотрудникам принимать детальные решения\n2. Употребляет ненормативную лексику, кричит, редко говорит спокойным тоном\n3. Терпит отклонения от плана, если они связаны с усилиями и творчеством\n4. Не терпит отклонений от плана\n5. Обучает своих сотрудников для обеспечения их удовлетворенности и карьерного развития\n6. Тренерует сотрудников, так чтобы им не прострелили зад на поле боя")
    await state.set_state(TestState.question_7)

@router.message(TestState.question_7)
async def process_test_question_7(message: types.Message, state: FSMContext):
    await state.update_data(answer_7=message.text)
    await message.answer("Что Латокен ждет от каждого члена команды?\n1. Спокойной работы без излишнего стресса\n2. Вникания в блокеры вне основного стека, чтобы довести свою задачу до прода\n3. Тестирование продукта\n4. Субординацию, и не вмешательство чужие дела\n5. Вежливость и корректность в коммуникации\n6. Измерение результатов\n7. Демонстрацию результатов в проде каждую неделю")
    await state.set_state(TestState.question_8)

@router.message(TestState.question_8)
async def process_test_question_8(message: types.Message, state: FSMContext):
    await state.update_data(answer_8=message.text)
    await message.answer("Представьте вы на выпускном экзамене. Ваш сосед слева просит вас передать ответы от соседа справа. Вы поможете?\n1. Да\n2. Да, но если преподаватель точно не увидит\n3. Да, но только если мне тоже помогут\n4. Нет\n5. Нет, если мне не дадут посмотреть эти ответы\n6. Нет, если это может мне повредить")
    await state.set_state(TestState.question_9)

@router.message(TestState.question_9)
async def process_test_question_9(message: types.Message, state: FSMContext):
    await state.update_data(answer_9=message.text)
    await message.answer("Кирпич весит килограмм и еще пол-кирпича. Сколько весит кирпич?\n1. 1 кг\n2. 1.5 кг\n3. 2 кг\n4. 3 кг")
    await state.set_state(TestState.question_10)

@router.message(TestState.question_10)
async def process_test_question_10(message: types.Message, state: FSMContext):
    await state.update_data(answer_10=message.text)
    await message.answer("Напишите ваши 'за' и 'против' работы в Латокен? Чем подробнее, тем лучше - мы читаем.")
    await state.set_state(TestState.question_11)

@router.message(TestState.question_11)
async def process_test_question_11(message: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(answer_11=message.text)
    data = await state.get_data()
    
    # Запись ответов в файл
    user_name = message.from_user.username or message.from_user.full_name
    file_name = f"{user_name}.txt"
    with open(file_name, "w") as file:
        file.write(f"Ответы пользователя {user_name}:\n")
        file.write(f"1. {data['answer_1']}\n")
        file.write(f"2. {data['answer_2']}\n")
        file.write(f"3. {data['answer_3']}\n")
        file.write(f"4. {data['answer_4']}\n")
        file.write(f"5. {data['answer_5']}\n")
        file.write(f"6. {data['answer_6']}\n")
        file.write(f"7. {data['answer_7']}\n")
        file.write(f"8. {data['answer_8']}\n")
        file.write(f"9. {data['answer_9']}\n")
        file.write(f"10. {data['answer_10']}\n")
        file.write(f"11. {data['answer_11']}\n")
    
    # Отправка файла администратору
    await bot.send_document(ADMIN_ID, FSInputFile(file_name))
    
    # Удаление файла после отправки
    os.remove(file_name)
    
    await message.answer("Спасибо за прохождение теста! Ваши ответы были отправлены администратору.")
    await state.clear()