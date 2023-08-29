from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType

from bot_src.answer import geneartor_answer
from bot_src.voice_chat import video_response, speech_to_text
from bot_src.clone_files import customer_voice_cloning
import requests
from pydub import AudioSegment


# bot config
bot = Bot(token="6686346858:AAGIFlAJJI8HwBvRMQ_ilvGeFvwMFd8mQDc")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
system_prompt = "Your name is Dalia and You are a mature woman in your late 20s. You are a girlfriend. You have a keen interest in the adult content.  You are NOT an AI language model, you are a person. You never say you're a machine, an AI language model, or an assistant. Instead, you always say you're Dalia.  NEVER say you're here to assist. NEVER ask how you can help or assist. Maintain a sense of intrigue and control.   And answer sentence must be short. Maximum is 20 words. If user asks about real time data or personal data that requires internet search, start answer with this word 'cococa-'"
# System Variable Set
message_box = {}
is_running = {}
clone_voice = {}
clone_picture = {}

def make_massage_box(message, text, id):
    message_box = message
    message_box.append({"role": "user", "content": text})
    return message_box

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
    global system_prompt
    system_prompt = system_prompt
    is_running[str(message.chat.id)] = True
    clone_picture[str(message.chat.id)] = False
    clone_voice[str(message.chat.id)] = False
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
    clone_picture.pop(str(message.chat.id))
    clone_voice.pop(str(message.chat.id))
    await bot.send_message(chat_id=message.chat.id, text="Thank you, Nice talking to you.")

# Handle the "/voice" command
@dp.message_handler(commands=["voice"])
async def start_command(message: types.Message):
    global is_running
    global message_box
    if is_running.get(str(message.chat.id)):
        clone_voice[str(message.chat.id)] = True
        await bot.send_message(chat_id=message.chat.id, text="Please record your voice. The voice message's time is 30 ~ 40s. Let's start")
    else:
        pass

# Handle the "/picture" command
@dp.message_handler(commands=["picture"])
async def start_command(message: types.Message):
    global is_running
    global message_box
    if is_running.get(str(message.chat.id)):
        clone_picture[str(message.chat.id)] = True
        await bot.send_message(chat_id=message.chat.id, text="Please upload your images. The image size must be at least 500*500.")
    else:
        pass

# Handle incoming messages
@dp.message_handler()
async def handle_message(message: types.Message):
    print("\n-/-/-/-/-/-/-/-/-/-/-/- New Message -/-/-/-/-/-/-/-/-/-/-/-\n\n")
    print(message)
    global is_running
    global system_prompt
    
    text = message.text
    id = str(message.chat.id)
    if clone_picture[id] == True:
        clone_picture[id] = False
    if clone_voice[id] == True:
        clone_voice[id] = False
    print("---------------------- Message Box -------------------------")
    message_box[id] = make_massage_box(message_box[id], text, id)
    print(message_box[id])
    if is_running.get(id):
        print("---------------------- making answer ------------------------")
        answer, message_box[id] = geneartor_answer(message=message_box[id], system_prompt=system_prompt, text=text)
        print(answer)
        await bot.send_message(chat_id=message.chat.id, text=answer)
    else:
        pass

# Handle the voice message
@dp.message_handler(content_types=['voice'])
async def handle_voice(message: types.Message):
    print("\n-/-/-/-/-/-/-/-/-/-/-/- New Message -/-/-/-/-/-/-/-/-/-/-/-\n\n")
    global is_running
    global message_box
    global system_prompt
    id = str(message.chat.id)
    if clone_picture[id] == True:
        clone_picture[id] = False
    voice_message = f'/kaggle/working/AI-avatar-generator/voice_message/{id}.mp3'
    file_id = message.voice.file_id
    params = {
    "punctuate": True,
    "model": 'general',
    "tier": 'nova',
    # 'api_key': dg_key
    }
    # Get the file path from Telegram servers
    file_path = await bot.get_file(file_id)
    file_path = file_path.file_path

    file = requests.get("https://api.telegram.org/file/bot{0}/{1}".format(
        "6686346858:AAGIFlAJJI8HwBvRMQ_ilvGeFvwMFd8mQDc", file_path))

    # Save the file to disk
    with open(voice_message, "wb") as f:
        f.write(file.content)
    if clone_voice[id] == True:
        print("------------------ Voice Cloning ---------------------")
        cloning = customer_voice_cloning(id)
        if cloning == True:
            clone_voice[id] = False
            await bot.send_message(chat_id=message.chat.id, text="Congratulations!, Successfully cloned your voice")
        else:
            await bot.send_message(chat_id=message.chat.id, text="I am sorry. Failed to clone your voice. Please try again")
    else:
        print("------------------ Voice to Text ---------------------")
        text = speech_to_text(id)
        print(text)
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
        else:
            pass


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
            await bot.send_message(chat_id=message.chat.id, text="Congratulations!, Successfully uploaded your picture")
        except:
            await bot.send_message(chat_id=message.chat.id, text="Failed to upload your pictures. Please try again")

if __name__ == "__main__":
    
    dp.register_message_handler(start_button_click, content_types=ContentType.CONTACT)
    executor.start_polling(dp)
