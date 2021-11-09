from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from gmailWork import *
TOKEN = ""
email, subject, my_message,test_name = range(4)
info=""

def start_gmail(update, context):
    update.message.reply_text(text="Hello!")
    with open('photos.txt','w'): pass
    service, user_email = credentials_service()

def new_message(update, context):
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Receiver of email:',)
    return email
def email_handler(update,context):
    context.user_data[email] = update.message.text
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Subject of email:',)
    return subject
def subject_handler(update,context):
    context.user_data[subject] = update.message.text
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Text of email:',)
    return my_message
def message_handler(update,context):
    context.user_data[my_message] = update.message.text
    update.message.reply_text(f'''
    Succesfully saved!\nTo: {context.user_data[email]}\nSubject: {context.user_data[subject]}\nMessage: {context.user_data[my_message]} ''')
    service_gmail, service_drive, service_docs, user_email = credentials_service()
    SendMessage(service_gmail, user_email, context.user_data[email], context.user_data[subject],
                context.user_data[my_message])
    update.message.reply_text(text="Email sent!")
    return ConversationHandler.END

def get_photos(update,context):
    file = update.message.photo[-1].get_file()
    file.download()
    update.message.reply_text("Image received")
    with open('photos.txt', 'a') as token:
        token.write(file['file_path']+"\n")
    return file['file_path']

def generate_test(update,context):
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Document-test name:',
    )
    return test_name
def test_name_handler(update,context):
    service_gmail, service_drive, service_docs,user_email  = credentials_service()
    context.user_data[test_name] = update.message.text
    file, file_id = create_doc(service_drive, context.user_data[test_name])
    insert_img_file(service_docs, file_id)
    with open('link.txt', 'w') as token:
        token.write(file.get('webViewLink'))
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Email:',
    )
    return email
def subject_handler_for_test_func(update, context):
    context.user_data[subject] = update.message.text
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Text of email:',
    )
    return my_message
def message_handler_for_test_func(update, context):
    with open('link.txt', 'r') as token:
        link=token.readline()
    context.user_data[my_message] = update.message.text +"\n"+link
    update.message.reply_text(f'''
    Succesfully saved!\nTo: {context.user_data[email]}\nSubject: {context.user_data[subject]}\nMessage: {context.user_data[my_message]} 
    ''')
    service_gmail,service_drive,service_docs, user_email = credentials_service()
    SendMessage(service_gmail, user_email, context.user_data[email], context.user_data[subject], context.user_data[my_message])
    update.message.reply_text(text="Email sent!")
    return ConversationHandler.END

def get_mes(update,context):
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Напишіть через кому кількість бажаних листів,true або false(якщо хочете знайти за конкретним email-true),email:',
    )
    return info
def parse_info(update,context):
    inf = update.message.text.split(",")
    service_gmail, service_drive, service_docs, user_email = credentials_service()
    m_list= GetMessage(service_gmail,inf[0],inf[2],inf[1])
    update.message.reply_text("Successfully!")
    for mes in m_list:
        update.message.reply_text(mes)
    return ConversationHandler.END
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('new_message', new_message)],
        states={
            email: [MessageHandler(Filters.text, email_handler, pass_user_data=True)],
            subject: [MessageHandler(Filters.text, subject_handler,pass_user_data=True)],
            my_message: [MessageHandler(Filters.text, message_handler, pass_user_data=True)]
        },
        fallbacks=[
        ],
    )
    conv_handler1 = ConversationHandler(
        entry_points=[CommandHandler('generate_and_send_test', generate_test)],
        states={
            test_name: [MessageHandler(Filters.text, test_name_handler, pass_user_data=True)],
            email: [MessageHandler(Filters.text, email_handler, pass_user_data=True)],
            subject: [MessageHandler(Filters.text, subject_handler_for_test_func, pass_user_data=True)],
            my_message: [MessageHandler(Filters.text, message_handler_for_test_func, pass_user_data=True)]
        },
        fallbacks=[
        ],
    )
    conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler('get_messages',get_mes)],
        states={
            info: [MessageHandler(Filters.text, parse_info, pass_user_data=True)]
        },
        fallbacks=[
        ],
    )

    dp.add_handler(conv_handler)
    dp.add_handler(conv_handler1)
    dp.add_handler(conv_handler2)
    dp.add_handler(CommandHandler('start_gmail', start_gmail))
    dp.add_handler(MessageHandler(Filters.photo, get_photos))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()