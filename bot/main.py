from typing import Final
from typing import Final
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import (
  Updater,
  CommandHandler,
  CallbackContext,
  MessageHandler,
  filters
)

import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler



#my bot
bot = Bot(token="6635906742:AAE30y2pQOVWP6p0SRAj-KOjNDutAJ-b8ME")
BOT_USERNAME: Final = '@instagram_up_down_bot'

#buttons
start_keyboard = [['Add expense', 'Balances 🌐'], ['People','Activity']]
people_keyboard = [['Add people', 'Main menu']]
cancel_keyboard = [['Cancel']]
main_menu_keyboard = [['Main menu']]

#Command answers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  markup = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)
  await update.message.reply_text('سلام به ربات اسپلیت وایز خوش آمدید.', reply_markup=markup)


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  markup = ReplyKeyboardMarkup(cancel_keyboard, resize_keyboard=True)
  await update.message.reply_text('کی به کی داده؟', reply_markup=markup)
    #Arash 250 to ali
  


async def balances_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  markup = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)
  ali_balance = await calculate_balance('Ali')
  arash_balance = await calculate_balance('arash')
  await update.message.reply_text(f"Ali's balance: {ali_balance}  \nArash's balance: {arash_balance}", reply_markup=markup)
  
#   ali_balance = await calculate_balance('Ali')
#   print("Ali's balance:", ali_balance)

#   # Calculate Arash's balance
#   arash_balance = await calculate_balance('arash')
#   print("Arash's balance:", arash_balance)


async def people_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = ReplyKeyboardMarkup(people_keyboard, resize_keyboard=True)
    await update.message.reply_text('What do u want to do?', reply_markup=markup)


async def add_people_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = ReplyKeyboardMarkup(cancel_keyboard, resize_keyboard=True)
    await update.message.reply_text('Please enter the name of the new person:', reply_markup=markup)

    # Set the conversation handler state to wait for the person's name
    context.user_data['conversation_state'] = 'WAITING_FOR_PERSON_NAME'


async def process_new_person_name(update: Update, context: CallbackContext, name: str):
    # Add the new person to your data structure or database
    # Here, I'll assume you have a list called 'people'
    people = context.user_data.get('people', [])
    people.append(name)
    context.user_data['people'] = people

    # Reset the conversation handler state
    context.user_data['conversation_state'] = None

    print(people)

    markup = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)
    # Send a confirmation message
    await update.message.reply_text('Person added: ' + name + '. Done!', reply_markup=markup)  

async def activity_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
  await update.message.reply_text('تکمیل نشده', reply_markup=markup)


async def home_command(update: Update):
  markup = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)
  await update.message.reply_text('⬅️')
  await update.message.reply_text('صفحه اصلی', reply_markup=markup)


data = []
async def split_add_expense(update: Update, input_expense):
  splitted_expense = input_expense.split()
  lender = splitted_expense[0]
  borrower = splitted_expense[-1]
  price = splitted_expense[1]

  transaction = {
        'lender': lender,
        'price': float(price),
        'borrower': borrower
    }
  
  data.append(transaction)
  
  await home_command(update)

async def calculate_balance(user):
    balance = 0.0

    for transaction in data:
        if transaction['lender'] == user:
            balance += transaction['price']
            
        if transaction['borrower'] == user:
            balance -= transaction['price']
        
    return balance  

#Handle message  
async def handle_message(update: Update, context: CallbackContext):
  if update.effective_chat.type == 'private':
    user_message = update.message.text
    print(f'Received message: {user_message}')
    
    # Check the conversation state
    conversation_state = context.user_data.get('conversation_state')

    if conversation_state == 'WAITING_FOR_PERSON_NAME':
            # Process the person's name
            await process_new_person_name(update, context, user_message)

    else:
        if user_message == 'Add expense':
            await add_command(update, context)
        elif user_message == 'Balances 🌐':
            await balances_command(update, context)
        elif user_message == 'People':
            await people_command(update, context)
        elif user_message == 'Add people':
            await add_people_command(update, context)
        elif user_message == 'Activity':
            await activity_command(update, context)     
        
        elif user_message == 'Main menu' or user_message == 'Cancel':
            await start_command(update, context)  
        
        else:
            print('chris')
            await split_add_expense(update, user_message)

# Error handler
async def error(update: Update, context: CallbackContext):
  print(f'Update {update} caused error {context.error}')





def main():
  app = Application.builder().token(bot.token).build()
  
  #Commands
  app.add_handler(CommandHandler('start', start_command))

  # Messages
  app.add_handler(MessageHandler(filters.TEXT, handle_message))

  # Log all errors
  app.add_error_handler(error)


  print('Polling...')
  # Run the bot
  app.run_polling(poll_interval=1)
  



if __name__ == '__main__':
  main()