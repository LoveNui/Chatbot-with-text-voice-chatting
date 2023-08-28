from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType

from bot_src.extract_info import make_system_prompt, extract_information, make_massage_box
from bot_src.answer import geneartor_answer
from bot_src.voice_chat import video_response, speech_to_text
import requests



# bot config
bot = Bot(token="6686346858:AAGIFlAJJI8HwBvRMQ_ilvGeFvwMFd8mQDc")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# System Variable Set
message_box = {}
is_running = {}

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
    message_box[str(message.chat.id)] = [{"role": "system",
                    "content": system_prompt},
                   {"role": "assistant", "content": "Hi, My name is Dalia. How is it going?"}]
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


# # Handle incoming messages
# @dp.message_handler()
# async def handle_message(message: types.Message):
#     print("-/-/-/-/-/-/-/-/-/-/-/- New Message -/-/-/-/-/-/-/-/-/-/-/-")
#     global is_running
#     text = message.text
#     id = str(message.chat.id)
#     system_prompt = make_system_prompt(id)
#     message_box[id] = make_massage_box(message_box[id], text, id)
#     print("---------------------- Message Box -------------------------")
#     print(message_box[id])
#     print("----------------------- user infor extraction -------------------------")
#     extract_information(text, id)
#     if is_running.get(id):
#         print("---------------------- making answer ------------------------")
#         answer, message_box[id] = geneartor_answer(message=message_box[id], system_prompt=system_prompt, text=text)
#         print(answer)
#         await bot.send_message(chat_id=message.chat.id, text=answer)
    

@dp.message_handler()
async def handle_message(message: types.Message):
    print("-/-/-/-/-/-/-/-/-/-/-/- New Message -/-/-/-/-/-/-/-/-/-/-/-")
    global is_running
    text = message.text
    id = str(message.chat.id)
    system_prompt = make_system_prompt(id)
    message_box[id] = make_massage_box(message_box[id], text, id)
    print("---------------------- Message Box -------------------------")
    print(message_box[id])
    print("----------------------- user infor extraction -------------------------")
    extract_information(text, id)
    if is_running.get(id):
        print("---------------------- making answer ------------------------")
        answer = geneartor_answer(message=message_box[id], system_prompt=system_prompt, text=text)
        print(answer)
        result = video_response(answer, id)
        with open(result, "rb") as video_file:
            await bot.send_video(chat_id=message.chat.id, video = video_file, duration=0)


# Handle the voice message
@dp.message_handler(content_types=['voice'])
async def handle_voice(message: types.Message):
    global is_running
    id = str(message.chat.id)
    
    # Get the file path from Telegram servers
    file_path = await bot.get_file(file_id)
    file_path = file_path.file_path

    file = requests.get("https://api.telegram.org/file/bot{0}/{1}".format("6359746469:AAHsiSHmdFWD4XxzDvYmWvAgM5IO35dUe7c", file_path))

    # Save the file to disk
    voice_message = f'./voice_message/{id}.ogg'
    with open(voice_message, "wb") as f:
        f.write(file.content)

    text = speech_to_text(id)
    
    system_prompt = make_system_prompt(id)
    message_box[id] = make_massage_box(message_box[id], text, id)
    if is_running:
        answer = geneartor_answer(message=message_box[id], system_prompt=system_prompt, text=text)
        result = video_response(answer, id)
        with open(result, "rb") as video_file:
            await bot.send_video(chat_id=message.chat.id, video = video_file, duration=0)



if __name__ == "__main__":
    
    dp.register_message_handler(start_button_click, content_types=ContentType.CONTACT)
    executor.start_polling(dp)
