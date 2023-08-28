from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType

from bot_src.extract_info import make_system_prompt, extract_information, make_massage_box
from bot_src.answer import geneartor_answer
from bot_src.voice_chat import video_response, speech_to_text
from bot_src.clone_files import customer_voice_cloning
import requests
from pydub import AudioSegment


# bot config
bot = Bot(token="6686346858:AAGIFlAJJI8HwBvRMQ_ilvGeFvwMFd8mQDc")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# System Variable Set
message_box = {}
is_running = {}
clone_voice = {}
clone_picture = {}

print("\n\n===================== Start Telegram Bot =======================\n\n")
#Action part
# Handle the "/start" command
@dp.message_handler(content_types=types.ContentType.CONTACT)
async def start_button_click(message: types.Message):
    pass


# Handle the "/start" command
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    global is_running
    global message_box
    
    system_prompt = make_system_prompt(str(message.chat.id))
    is_running[str(message.chat.id)] = True
    message_box[str(message.chat.id)] = [{"role": "assistant", "content": "Hi, My name is Dalia. How is it going?"},{"role": "system",
                    "content": system_prompt}]
    await bot.send_message(chat_id=message.chat.id, text="Hi, It's Dalia. How is it going?")


# Handle the "/stop" command
@dp.message_handler(commands=["stop"])
async def stop_command(message: types.Message):
    global is_running
    global message_box
    global system_prompt
    is_running.pop(str(message.chat.id))
    message_box.pop(str(message.chat.id))
    await bot.send_message(chat_id=message.chat.id, text="Thank you, Nice talking to you.")

# Handle the "/voice" command
@dp.message_handler(commands=["voice"])
async def start_command(message: types.Message):
    global is_running
    global message_box
    if is_running.get(id):
        clone_voice[id] = True
        await bot.send_message(chat_id=message.chat.id, text="Please record your voice. The voice message's time is 30 ~ 40s. Let's start")

# Handle the "/picture" command
@dp.message_handler(commands=["picture"])
async def start_command(message: types.Message):
    global is_running
    global message_box
    if is_running.get(id):
        clone_picture[id] = True
        await bot.send_message(chat_id=message.chat.id, text="Please record your voice. The voice message's time is 30 ~ 40s. Let's start")

# Handle incoming messages
@dp.message_handler()
async def handle_message(message: types.Message):
    if clone_picture[id] == True:
        clone_picture[id] = False
    if clone_voice[id] == True:
        clone_voice[id] = False
    print("-/-/-/-/-/-/-/-/-/-/-/- New Message -/-/-/-/-/-/-/-/-/-/-/-")
    print(message)
    global is_running
    text = message.text
    id = str(message.chat.id)
    print("----------------------- user infor extraction -------------------------")
    ext, system_prompt = extract_information(text, id)
    print("---------------------- Message Box -------------------------")
    message_box[id] = make_massage_box(message_box[id], text, id)
    print(message_box[id])
    if is_running.get(id):
        print("---------------------- making answer ------------------------")
        answer, message_box[id] = geneartor_answer(message=message_box[id], system_prompt=system_prompt, text=text)
        print(answer)
        await bot.send_message(chat_id=message.chat.id, text=answer)


# Handle the voice message
@dp.message_handler(content_types=['voice'])
async def handle_voice(message: types.Message):
    if clone_picture[id] == True:
        clone_picture[id] = False
    global is_running
    id = str(message.chat.id)
    file_id = message.voice.file_id
    # Get the file path from Telegram servers
    file_path = await bot.get_file(file_id)
    file_path = file_path.file_path
    print("-/-/-/-/-/-/-/-/-/-/-/- New Message -/-/-/-/-/-/-/-/-/-/-/-")
    file = requests.get("https://api.telegram.org/file/bot{0}/{1}".format("6359746469:AAHsiSHmdFWD4XxzDvYmWvAgM5IO35dUe7c", file_path))
    # Save the file to disk
    voice_message = f'/kaggle/working/AI-avatar-generator/voice_message/{id}.mp3'
    with open(voice_message, "wb") as f:
        f.write(file.content)
    if clone_voice[id] == True:
        cloning = customer_voice_cloning(id)
        if cloning == True:
            await bot.send_message(chat_id=message.chat.id, text="Congratulations!, Successfully cloned your voice")
        else:
            await bot.send_message(chat_id=message.chat.id, text="I am sorry. Failed to clone your voice")
    else:
        print("------------------ Voice to Text ---------------------")
        text = speech_to_text(id)
        print(text)
        ext, system_prompt = extract_information(text, id)
        print("---------------------- Message Box -------------------------")
        message_box[id] = make_massage_box(message_box[id], text, id)
        print(message_box[id])
        if is_running.get(id):
            print("---------------------- making answer ------------------------")
            answer, message_box[id] = geneartor_answer(message=message_box[id], system_prompt=system_prompt, text=text)
            print(answer)
            print("---------------------- Genearting Video ------------------------")
            result = video_response(answer, id)
            with open(result, "rb") as video_file:
                await bot.send_video(chat_id=message.chat.id, video = video_file, duration=0)


# Handle the voice message
@dp.message_handler(content_types=['photo'])
async def handle_voice(message: types.Message):
    print("--------------------- Download photos -------------------------")
    global is_running
    id = str(message.chat.id)
    if clone_picture[id] == True:
        picture_path = f'/kaggle/working/AI-avatar-generator/customer_files/customer_picture/{id}.png'
        print(picture_path)
        try:
            await message.photo[-1].download(destination_file=picture_path, make_dirs=False)
            clone_picture[id] == False
        except:
            await bot.send_message(chat_id=message.chat.id, text="Failed to download your pictures. Please try again")

if __name__ == "__main__":
    
    dp.register_message_handler(start_button_click, content_types=ContentType.CONTACT)
    executor.start_polling(dp)
