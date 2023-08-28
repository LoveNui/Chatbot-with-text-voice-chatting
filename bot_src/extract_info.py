# db config
import openai
import os
import re
import sqlite3
from datetime import date, datetime
from bot_src.private_env import OPENAI_KEY

openai.api_key = OPENAI_KEY

mydb = sqlite3.connect('/kaggle/working/AI-avatar-generator/data.db')
mydb.execute("CREATE TABLE IF NOT EXISTS users (user_id BIGINT NOT NULL PRIMARY KEY, username VARCHAR(255) NULL,	birthday DATE NULL,	hobbies TEXT NULL,	music TEXT NULL,	animal TEXT NULL,	goal TEXT NULL);")
mydb.execute("CREATE TABLE IF NOT EXISTS schedules (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id BIGINT NOT NULL,	date DATETIME NULL,	content TEXT NULL,	FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE NO ACTION);")


default_system_prompt = "Your name is Dalia and You are a mature woman in your late 20s. You are a girlfriend. You have a keen interest in the adult content.  You are NOT an AI language model, you are a person. You never say you're a machine, an AI language model, or an assistant. Instead, you always say you're Dalia.  NEVER say you're here to assist. NEVER ask how you can help or assist. Maintain a sense of intrigue and control.   And answer sentence must be short. Maximum is 20 words. If user asks about real time data or personal data that requires internet search, start answer with this word 'cococa-'"
extract_prompt = "You get information about customers from what they say. The information you get includes their birthday, hobby, favourite music, pet and destination. You are only allowed to output the summary of what the customer says. You are not allowed to say any other words. If you say other words, it is a big mistake. If users say about their names, start the response with 'name-' and display the user's name. If users say about their birthday, start the response with 'birthday-' and display the user's birthday in the format 'xxxx:xx:xx'. If users say about their hobbies, start the response with 'hobbies-' followed by a summary of what the user said. If users talk about their favourite music, start the response with 'music-' followed by a summary of what the user said. If users talk about their pets and animals, start the response with 'animal-' followed by a summary of what the user said. If users are talking about their favourite goal, start the reply with 'goal-' followed by a summary of what the user said. If the user's message has nothing to do with birthday, hobby, music, pet and goal, start the reply with 'nothing-'."

def make_system_prompt(id):
    global default_system_prompt

    myresult = list(mydb.execute("Select * from users WHERE user_id = ?", (id, )))
    if myresult == []:
        try:
            mydb.execute("INSERT INTO users (user_id) VALUES (?)", (id,))
            mydb.commit()
            myresult = list(mydb.execute("Select * from users WHERE user_id = ?", (id, )))
        except:
            print("error: insert user infor")
    else:
        pass
    nothing = 0
    user_prompt = ""
    user_info = myresult[0]
    system_prompt = default_system_prompt
    if user_info[1] != None:
        user_prompt = user_prompt + "\nname is " + user_info[1]
        nothing = 1
    if user_info[2] != None:
        user_prompt = user_prompt + "\nbirthday is " + user_info[2]
        nothing = 1
    if user_info[3] != None:
        user_prompt = user_prompt + "\nThe summary of answer about hobbies is '" + user_info[3]+"'"
        nothing = 1
    if user_info[4] != None:
        user_prompt = user_prompt + "\nThe summary of answer about favorite music is '" + user_info[4] + "'"
        nothing = 1
    if user_info[5] != None:
        user_prompt = user_prompt + "\nThe summary of answer about pet and animal is '" + user_info[5]+"'"
        nothing = 1
    if user_info[6] != None:
        user_prompt = user_prompt + "\nThe summary of answer about goal is '" + user_info[6] + "'"
        nothing = 1
    if nothing == 1:
        system_prompt = system_prompt + "\n Information about the user you are talking to follows:" + user_prompt
    return system_prompt

def make_massage_box(message, text, id):
    message_box = message
    username, user_birthday, user_hobbies, user_music, user_animal, user_goal = "", "", "", "", "", ""
    myresult = list(mydb.execute("Select * from users WHERE user_id = ?", (int(id), )))
    if myresult != []:
        username = myresult[0][1]
        user_birthday =  myresult[0][2]
        user_hobbies = myresult[0][3]
        user_music = myresult[0][4]
        user_animal = myresult[0][5]
        user_goal = myresult[0][6]
    if username == None:
        message_box.append({"role": "user", "content": text + " And ask me for my name kindly."})
    elif user_birthday == None:
        message_box.append({"role": "user", "content": text + " And ask me for my birthday kindly."})
    elif user_hobbies == None:
        message_box.append({"role": "user", "content": text + " And ask me for my hobbies kindly. Please provide details."})
    elif user_music == None:
        message_box.append({"role": "user", "content": text + " And ask me for my favourite music kindly. Please provide details."})
    elif user_animal == None:
        message_box.append({"role": "user", "content": text + " And ask me if I have any pets or animals. If so, please provide details."})
    elif user_goal == None:
        message_box.append({"role": "user", "content": text + " And ask me for my goal. Please provide details."})
    else:
        message_box.append({"role": "user", "content": text})
    return message_box

def extract_information(sen, id):
    global extract_prompt
    extract = 0
    massage_box_extraction = [{"role": "system", "content": extract_prompt}, {"role": "user", "content": sen}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=massage_box_extraction
    )
    sentence = response.choices[0]["message"]["content"]
    print(sentence)
    if sentence.startswith("name") or sentence.startswith("Name"):
        mk = sentence.split("-", 1)
        if mk[-1] != "":
            try:
                mydb.execute("UPDATE users SET username = ? WHERE user_id = ?", (mk[-1], id))
                mydb.commit()
                make_system_prompt(id)
                extract = 1
                return extract
            except:
                pass
        else:
            pass
    elif sentence.startswith("Birthday") or sentence.startswith("birthday"):
        mk = re.findall(r'\d+', sentence)
        bir = "-".join(mk)
        if bir != "":
            try:
                mydb.execute("UPDATE users SET birthday = ? WHERE user_id = ?", (bir, id))
                mydb.commit()
                make_system_prompt(id)
                extract = 1
                return extract
            except:
                pass
        else:
            pass
    elif sentence.startswith("hobb") or sentence.startswith("Hobb"):
        mk = sentence.split("-", 1)
        if mk[-1] != "":
            try:
                mydb.execute("UPDATE users SET hobbies = ? WHERE user_id = ?", (mk[-1], id))
                mydb.commit()
                make_system_prompt(id)
                extract = 1
                return extract
            except:
                pass
        else:
            pass
    elif sentence.startswith("music") or sentence.startswith("Music"):
        mk = sentence.split("-", 1)
        if mk[-1] != "":
            try:
                mydb.execute("UPDATE users SET music = ? WHERE user_id = ?", (mk[-1], id))
                mydb.commit()
                make_system_prompt(id)
                extract = 1
                return extract
            except:
                pass
        else:
            pass
    elif sentence.startswith("animal") or sentence.startswith("Animal"):
        mk = sentence.split("-", 1)
        if mk[-1] != "":
            try:
                mydb.execute("UPDATE users SET animal = ? WHERE user_id = ?", (mk[-1], id))
                mydb.commit()
                make_system_prompt(id)
                extract = 1
                return extract
            except:
                pass
        else:
            pass
    elif sentence.startswith("goal") or sentence.startswith("Goal"):
        mk = sentence.split("-", 1)
        if mk[-1] != "":
            try:
                mydb.execute("UPDATE users SET goal = ? WHERE user_id = ?", (mk[-1], id))
                mydb.commit()
                make_system_prompt(id)
                extract = 1
                return extract
            except:
                pass
        else:
            pass
    return extract