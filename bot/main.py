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
import re

import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler


#my bot
bot = Bot(token="6635906742:AAE30y2pQOVWP6p0SRAj-KOjNDutAJ-b8ME")
BOT_USERNAME: Final = '@instagram_up_down_bot'


obj = []
# Member class
class Member:
   def __init__(self, name, balance):
      self.name = name
      self.balance = balance
    
   def update_balance(self, name, amount):
        if self.name == name:
            self.balance += amount
            return self.balance
        else:
            return "Member not found."
   
   def __str__(self) -> str:
      return self.name.capitalize()+" : "+str(self.balance)
   
   def return_name(self) -> str:
      return self.name.capitalize()

#buttons
start_keyboard = [['Add expense', 'Balances 🌐'], ['People','Activity']]
people_keyboard = [['Add people', 'Show People'], ['Main menu']]
cancel_keyboard = [['Cancel']]
main_menu_keyboard = [['Main menu']]

##################################
#Command methods answers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  markup = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)
  await update.message.reply_text('سلام به ربات اسپلیت وایز خوش آمدید.', reply_markup=markup)

async def add_expenses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  markup = ReplyKeyboardMarkup(cancel_keyboard, resize_keyboard=True)
  await update.message.reply_text('Write on this format: Lender price to Borrower for X (X is the thing that he/she bought).', reply_markup=markup)
    #Arash 250 to ali for pizza
  
async def balances_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  markup = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)
  balances_answer = ''
  for member in obj:
    balances_answer+=str(member)+"\n"
  await update.message.reply_text(balances_answer, reply_markup=markup)

async def people_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = ReplyKeyboardMarkup(people_keyboard, resize_keyboard=True)
    await update.message.reply_text('What do u want to do?', reply_markup=markup)


async def add_people_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = ReplyKeyboardMarkup(cancel_keyboard, resize_keyboard=True)
    await update.message.reply_text('Please enter the name of the new person:', reply_markup=markup)

    # Set the conversation handler state to wait for the person's name
    context.user_data['conversation_state'] = 'WAITING_FOR_PERSON_NAME'


async def show_people_command(update: Update, context: CallbackContext):
    member_names = ''
    for member in obj:
       member_names+=member.name.capitalize()+"\n"

    await update.message.reply_text(member_names)

#********************************************************************************
async def activity_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
  await update.message.reply_text('تکمیل نشده', reply_markup=markup)
#********************************************************************************


async def home_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
  markup = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)
  await update.message.reply_text('⬅️', reply_markup=markup)
  # await update.message.reply_text('صفحه اصلی', )

async def invalid_message_command(update: Update):
   markup = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)
   await update.message.reply_text('Not a valid command. Choose beetwen key options', reply_markup=markup)  


##################################
#other methods
async def process_new_person_name(update: Update, context: CallbackContext, name: str):
    # name converted to lowercase for saving 

    # member object
    obj.append(Member(name.lower(), 0))


    # Reset the conversation handler state
    context.user_data['conversation_state'] = None

    # print(people)

    markup = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)
    # Send a confirmation message
    await update.message.reply_text('Person added: ' + name + '. Done!', reply_markup=markup) 




data = []
async def split_add_expense(update: Update, input_expense):
    markup = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)
    
    splitted_expense = input_expense.split()
    lender = splitted_expense[0].lower()
    borrower = splitted_expense[3].lower()
    price = float(splitted_expense[1]) 

    # Find the lender and borrower in the obj list
    lender_member = None
    borrower_member = None
    for member in obj:
        if member.name == lender:
            lender_member = member
        elif member.name == borrower:
            borrower_member = member

    # Check if both lender and borrower are found
    if lender_member and borrower_member:
        lender_member.update_balance(lender, price)
        borrower_member.update_balance(borrower, -price)
        await update.message.reply_text('Expense added.', reply_markup=markup)
    else:
        await update.message.reply_text("Lender or borrower not found. There is a problem on your add expense message.", reply_markup=markup)

      


#Handle message  
async def handle_message(update: Update, context: CallbackContext):
  if update.effective_chat.type == 'private':
    user_message = update.message.text
    print(f'Received message: {user_message}')
    
    # Check the conversation state
    conversation_state = context.user_data.get('conversation_state')
    
    #regex for checking adding expenses
    pattern = r"^(\w+)\s+(\d+)\s+to\s+(\w+)\s+for\s+(\w+)$"

    if conversation_state == 'WAITING_FOR_PERSON_NAME':
        # Process the person's name
        await process_new_person_name(update, context, user_message)

    else:
        if user_message == 'Add expense':
            await add_expenses_command(update, context)
        elif user_message == 'Balances 🌐':
            await balances_command(update, context)
        elif user_message == 'People':
            await people_command(update, context)
        elif user_message == 'Add people':
            await add_people_command(update, context)
        elif user_message == 'Show People':
            await show_people_command(update, context)
        elif user_message == 'Activity':
            await activity_command(update, context)     
        
        elif user_message == 'Main menu' or user_message == 'Cancel':
            await home_command(update, context)  
        
        
        else:
            if re.match(pattern, user_message, re.IGNORECASE):
              await split_add_expense(update, user_message)
              print('chris')
            else:
              await invalid_message_command(update)
            

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