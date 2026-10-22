import telebot
TOKEN = "8943164489:AAHfFqb9_5lukOU2CCY8FEd9mxC3hdm8Ff4"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def id_sender(m):
    bot.send_message(m.chat.id, f"Your Chat ID is: {m.chat.id}\nCopy this number send to me!")

bot.infinity_polling()
