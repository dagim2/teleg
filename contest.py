import telebot
from telebot import types
import os

API_TOKEN = '7220128060:AAG85w8zxA1t2sagr15iiElAUHSiiJVst7s'
bot = telebot.TeleBot(API_TOKEN)

users = {}
uploads = {}
registration_states = {}
upload_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(row_width=2)
    register_btn = types.KeyboardButton('Register')
    profile_btn = types.KeyboardButton('Profile')
    upload_btn = types.KeyboardButton('Upload Files')
    status_btn = types.KeyboardButton('Check Status')
    markup.add(register_btn, profile_btn, upload_btn, status_btn)
    bot.send_message(chat_id, "Welcome! Please choose an option:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Register') 
def register(message): 
    chat_id = message.chat.id 
    if chat_id in users: 
        bot.send_message(chat_id, "You are already registered.") 
    else: 
        bot.send_message(chat_id, "Please provide your username.") 
        registration_states[chat_id] = 'username' 
        bot.register_next_step_handler(message, register_username) 

def register_username(message): 
    chat_id = message.chat.id 
    if registration_states.get(chat_id) == 'username': 
        username = message.text 
        bot.send_message(chat_id, "Please provide your email.") 
        registration_states[chat_id] = 'email' 
        bot.register_next_step_handler(message, register_email, username) 

def register_email(message, username): 
    chat_id = message.chat.id 
    if registration_states.get(chat_id) == 'email': 
        email = message.text 
        users[chat_id] = {'username': username, 'email': email} 
        registration_states.pop(chat_id, None) 
        bot.send_message(chat_id, "You are now registered!") 
        
@bot.message_handler(func=lambda message: message.text == 'Profile') 
def profile(message): 
    chat_id = message.chat.id 
    if chat_id in registration_states: 
        bot.send_message(chat_id, "You are currently in the registration process. Please complete it first.") 
    elif chat_id in users: 
        bot.send_message(chat_id, f"Username: {users[chat_id]['username']}\nEmail: {users[chat_id]['email']}") 
    else: bot.send_message(chat_id, "You are not registered. Please use the 'Register' button to sign up.") 

@bot.message_handler(func=lambda message: message.text == 'Upload Files') 
def upload_files(message): 
    chat_id = message.chat.id 
    if chat_id in users: 
        bot.send_message(chat_id, "Please enter the competiotion title:") 
        upload_states[chat_id] = 'awaiting_title'
        bot.register_next_step_handler(message, receive_competition_title)
    else: 
        bot.send_message(chat_id, "You need to register first. Please use the 'Register' button to sign up.") 
        registration_states[chat_id] = 'username' 
        bot.register_next_step_handler(message, register_username) 

def receive_competition_title(message):
    chat_id = message.chat.id
    if upload_states.get(chat_id) == 'awaiting_title':
        title = message.text
        upload_states[chat_id] = {'title': title}
        bot.send_message(chat_id, "Now, please upload your ZIP file.")
    else:
        bot.send_message(chat_id, "Please enter a valid competition title.")        
        
@bot.message_handler(content_types=['document']) 
def handle_docs(message): 
    chat_id = message.chat.id 
    if chat_id in users and message.document.mime_type == 'application/zip': 
        if chat_id in upload_states and 'title' in upload_states[chat_id]:
            title = upload_states[chat_id]['title']
            file_info = bot.get_file(message.document.file_id) 
            downloaded_file = bot.download_file(file_info.file_path) 
        
            # Ensure the 'uploads' directory exists 
            if not os.path.exists('uploads'): 
                os.makedirs('uploads') 
            
            file_name = f"{title}_{message.document.file_name}"
            file_path =  os.path.join('uploads', file_name)
            with open(file_path, 'wb') as new_file: 
                new_file.write(downloaded_file) 
            
            uploads[chat_id] = file_name 
            bot.reply_to(message, "File uploaded successfully!") 
            #clear the state after upload
            upload_states.pop(chat_id, None)
        else:
            bot.reply_to(message, "Please enter the competition title first by selecting 'Upload Files'.")
    else: 
        bot.reply_to(message, "Only ZIP files are allowed or you need to register first.") 
    
@bot.message_handler(func=lambda message: message.text == 'Check Status') 
def check_status(message): 
    chat_id = message.chat.id 
    if chat_id in users: 
        if chat_id in uploads: 
            # Replace this logic with actual status check 
            bot.send_message(chat_id, "Your submission is under review.") 
        
        else: 
            bot.send_message(chat_id, "No submissions found.") 
    else: 
        bot.send_message(chat_id, "You need to register first. Please use the 'Register' button to sign up.") 
        registration_states[chat_id] = 'username' 
        bot.register_next_step_handler(message, register_username) 
        
ADMIN_CHAT_ID = '6286579149' 

@bot.message_handler(commands=['admin']) 
def admin_panel(message): 
    chat_id = message.chat.id 
    if str(chat_id) == ADMIN_CHAT_ID: 
        markup = types.ReplyKeyboardMarkup(row_width=2) 
        view_users_btn = types.KeyboardButton('View Users') 
        view_uploads_btn = types.KeyboardButton('View Uploads') 
        announce_btn = types.KeyboardButton('Announce') 
        markup.add(view_users_btn, view_uploads_btn, announce_btn) 
        bot.send_message(chat_id, "Admin Panel", reply_markup=markup) 
        
@bot.message_handler(func=lambda message: message.text == 'View Users' and str(message.chat.id) == ADMIN_CHAT_ID) 
def view_users(message): 
    chat_id = message.chat.id 
    user_list = "Registered Users:\n" 
    for user_id, user_info in users.items(): 
        user_list += f"ID: {user_id}, Username: {user_info['username']}, Email: {user_info['email']}\n" 
    bot.send_message(chat_id, user_list) 
    
@bot.message_handler(func=lambda message: message.text == 'View Uploads' and str(message.chat.id) == ADMIN_CHAT_ID) 
def view_uploads(message): 
    chat_id = message.chat.id 
    upload_list = "User Uploads:\n" 
    for user_id, file_name in uploads.items(): 
        upload_list += f"ID: {user_id}, File: {file_name}\n" 
    bot.send_message(chat_id, upload_list) 
    
@bot.message_handler(func=lambda message: message.text == 'Announce' and str(message.chat.id) == ADMIN_CHAT_ID) 
def announce(message): 
    chat_id = message.chat.id 
    bot.send_message(chat_id, "Please enter the announcement message.") 
    bot.register_next_step_handler(message, send_announcement) 
    
def send_announcement(message): 
    announcement = message.text 
    for user_id in users.keys(): 
        bot.send_message(user_id, f"Announcement: {announcement}") 
    bot.send_message(ADMIN_CHAT_ID, "Announcement sent to all users.") 
    
bot.polling()
