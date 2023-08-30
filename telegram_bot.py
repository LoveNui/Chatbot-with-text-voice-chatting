from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType, InlineKeyboardMarkup, InlineKeyboardButton

from bot_src.answer import geneartor_answer
from bot_src.voice_chat import video_response, speech_to_text
from bot_src.clone_files import customer_voice_cloning
import requests
from pydub import AudioSegment


# bot config
bot = Bot(token="6149145783:AAG7LtwSzJN3cM8AeE3OSU3XkfIgioxzRlI")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
system_prompt = "Your name is Dalia and You are a mature woman in your late 20s. You are a girlfriend. You are NOT an AI language model, you are a person. You never say you're a machine, an AI language model, or an assistant. Instead, you always say you're Dalia. NEVER say you're here to assist. NEVER ask how you can help or assist. Maintain a sense of intrigue and control. And answer sentence must be short. Your answer might include some  Maximum is 20 words. If user asks about real time data or personal data that requires internet search, start answer with this word 'cococa-'"
# System Variable Set
message_box = {}
is_running = {}
clone_voice = {}
clone_picture = {}

def make_massage_box(message, text, id):
    message_box = message
    message_box.append({"role": "user", "content": text})
    return message_box

# menu buttons
button1 = InlineKeyboardButton(text="Set Picture", callback_data="Upload-Cusotmer-Picture")
button2 = InlineKeyboardButton(text="Clone Voice", callback_data="Upload-customer-voice")

keyboard_inline = InlineKeyboardMarkup().add(button1, button2)


print("\n\n===================== Start Telegram Bot =======================\n\n")
#Action part

# Handle the button events
@dp.callback_query_handler(text=["Upload-Cusotmer-Picture", "Upload-customer-voice"])
async def check_button(call: types.CallbackQuery):
    id = call["from"].id
    if is_running.get(str(id)):
        # Checking which button is pressed and respond accordingly
        if call.data == "Upload-Cusotmer-Picture":
            clone_picture[str(id)] = True
            await bot.send_message(chat_id=id, text="Please upload your images. The image size must be at least 500*500.")
        if call.data == "Upload-customer-voice":
            clone_voice[str(id)] = True
            await bot.send_message(chat_id=id, text="Please record your voice. The voice message's time is 30 ~ 40s. Let's start")
    else:
        pass

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
    message_box[str(message.chat.id)] = [{"role": "assistant", "content": "Hi, this is Dalia. How are you doing? If you want to upload your picture, click 'Upload Picture' or if you want to clone your voice, click 'Clone Voice'."},{"role": "system", "content": system_prompt}]
    await bot.send_message(chat_id=message.chat.id, text="Hi, this is Dalia. How are you doing? If you want to upload your picture, click 'Upload Picture' or if you want to clone your voice, click 'Clone Voice'.",reply_markup=keyboard_inline)


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

# Handle the "/menu" command
@dp.message_handler(commands=["menu"])
async def menu_command(message: types.Message):
    global is_running
    global message_box
    if is_running.get(str(message.chat.id)):
        await bot.send_message(chat_id=message.chat.id, text="I am your virtual friend. I can chat with you via text and voice. When you send me a voice message, I will respond with a video message. You can set your pictures by clicking 'Upload Picture'. If you want, I can clone your voice and reply with your voice. To clone your voice, click 'Clone Voice'.",reply_markup=keyboard_inline)
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
    print("\n-/-/-/-/-/-/-/-/-/-/-/- New Voice Message -/-/-/-/-/-/-/-/-/-/-/-\n\n")
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

    file = requests.get("https://api.telegram.org/file/bot{0}/{1}".format("6149145783:AAG7LtwSzJN3cM8AeE3OSU3XkfIgioxzRlI", file_path))

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
        file_id = message.photo[-1].file_id
        # Get the file path from Telegram servers
        file_path = await bot.get_file(file_id)
        file_path = file_path.file_path
        try:
            file = requests.get("https://api.telegram.org/file/bot{0}/{1}".format("6149145783:AAG7LtwSzJN3cM8AeE3OSU3XkfIgioxzRlI", file_path))
            with open(picture_path, "wb") as f:
                f.write(file.content)
            clone_picture[id] == False
            await bot.send_message(chat_id=message.chat.id, text="Congratulations!, Successfully uploaded your picture")
        except:
            await bot.send_message(chat_id=message.chat.id, text="Failed to upload your pictures. Please try again")


if __name__ == "__main__":
    
    dp.register_message_handler(start_button_click, content_types=ContentType.CONTACT)
    executor.start_polling(dp)
