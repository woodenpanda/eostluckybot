# -*- coding: utf-8 -*-
#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import requests
import random
import time
import logging
from typing import Dict
from telegram import ParseMode
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove,InputMediaPhoto,InputMediaAnimation, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    PicklePersistence,
    CallbackContext,
)
import shlex, json
import subprocess
from subprocess  import PIPE
import os
def do_cmd(command):
    nowtime = os.popen(command)
    return nowtime.read()

def unlock():
    do_cmd('cleos wallet unlock -n xxxxx --password PWxxxx')

def is_acaount(acc):
    try:
        info2 = do_cmd("cleos -u https://eos-mainnet.token.im get account " + acc)
        return ('owner' in info2 and 'error' not in info2)
    except:
        return False


def sendhb_online(lucky_guys,context):
    jsonFileName =  'trx' + str(random.randint(0,99999))
    m1  = '''cleos -u https://eos.dfuse.eosnation.io push transaction '{   "delay_sec": 0,   "max_cpu_usage_ms": 0,   "actions": ['''
    m2 = '''{       "account": "eosio.token",       "name": "transfer",       "data": {         "from": "eoscnadmin.e",         "to": "receieveAccount",         "quantity": "eosAmount EOS",         "memo": "senderMemo"       },       "authorization": [         {           "actor": "eoscnadmin.e",           "permission": "active"         }       ]     },'''
    m3 = ''' ] }' -p eoscnadmin.e@active --expiration 604800 --json --dont-broadcast --skip-sign >jsonFileName.json '''
    mss2 = ''
    for id in lucky_guys:
        receieveAccount = context.bot_data['userDict'][id]['address']
        eosAmount = float(lucky_guys[id])/10000.0
        eosAmount = str(format(eosAmount, '.4f'))
        tmp = m2
        tmp = tmp.replace('receieveAccount',receieveAccount)
        tmp = tmp.replace('eosAmount',eosAmount)
        tmp = tmp.replace('senderMemo','')
        mss2+=tmp
    ms = m1 + mss2 + m3.replace('jsonFileName',jsonFileName)
    unlock()
    print(ms)
    print(do_cmd(ms))
    tr = 'cleos -u https://eos.dfuse.eosnation.io push transaction ./jsonFileName.json'.replace('jsonFileName',jsonFileName)
    print(do_cmd(tr))



messageDict = {}
adminDict = {'@stevencoco':5,'@woodenpanda':8,'@bigoneeos':1,'@eoscnzj':1,'@Beatricewang':1,'@v998n':1,'@Vikin_Zhang':1}
threshold = 3
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)




def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = []

    for key, value in user_data.items():
        facts.append(f'{key} - {value}')

    return "\n".join(facts).join(['\n', '\n'])



def addhb(update: Update, context: CallbackContext) -> None:
    prehb = context.bot_data['prehb'] if context.bot_data.get('prehb') else {}
    prehb['actived'] = False
    if update.message.from_user.name not in adminDict or prehb['actived'] == True:
        return None
    reply_text = "???????????????????????????????????????"
    prehb = {}
    prehb['proposer'] = update.message.from_user
    prehb['amount'] = int(context.args[0])
    amount = prehb['amount']
    prehb['amount_left'] = amount
    prehb['lucky_guys'] = {}
    prehb['balance'] = float(context.args[1])
    balance = prehb['balance']
    prehb['rest_balance']= int(prehb['balance']*10000)
    prehb['full_balance']= int(prehb['balance']*10000)
    prehb['approvelist'] = []
    prehb['approveweight'] = 0
    prehb['actived'] = False
    context.bot_data['prehb'] = prehb

    reply_text = (
        f'?????????????????????????????????: {amount}??????????????????{balance} EOS'
        '???????????? /approve'
        )
        
    keyboard = [
        [InlineKeyboardButton("??????", callback_data='approve')],
    ]
    
    markup = InlineKeyboardMarkup(keyboard)


    update.message.reply_text(reply_text)

 





def button(update: Update,  context: CallbackContext) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer('?????????')
    # print(str(query.from_user.id))
    # str(query.from_user.id)
    keyboard = [
        [InlineKeyboardButton("?????????", callback_data='3')],
    ]
    
    
    prehb = context.bot_data['prehb'] if context.bot_data.get('prehb') else {}
    text = ''
    if context.bot_data['userDict'][query.from_user.id].get('address') and query.from_user.id not in prehb['lucky_guys'] and  prehb['amount_left'] > 0  :
        if prehb['amount_left'] == 1:
            lucky_balance = prehb['rest_balance']

        else:
            lucky_balance = random.randint(1,  int(prehb['rest_balance']/ prehb['amount_left'] * 2)) 
        
        if lucky_balance == 0:
            lucky_balance = 1
        prehb['amount_left'] -= 1
        prehb['rest_balance'] -= lucky_balance

        prehb['lucky_guys'][query.from_user.id] = lucky_balance

    facts = []
    amount_left = prehb['amount_left'] 
    amount = prehb['amount'] 
    rest_balance = prehb['rest_balance']/10000.0
    full_balance = prehb['full_balance']/10000.0
    facts.append( f"????????????:{amount_left}/{amount}???\n????????????:{rest_balance}/{full_balance} EOS\n")
    for id in prehb['lucky_guys']:
        full_name = context.bot_data['userDict'][id]['full_name']
        lb = prehb['lucky_guys'][id]
        facts.append(f"{full_name} - {lb/10000.0} EOS\n")
    text = "".join(facts)
    reply_markup = InlineKeyboardMarkup(keyboard)
    if prehb['amount_left'] == 0:
        query.edit_message_text(text+'\n???????????????')
    else:
        query.edit_message_text(text,reply_markup=reply_markup)
    if prehb['amount_left'] == 0 and prehb['actived'] == True:
        context.bot_data['prehb']['actived'] = False
        sendhb_online(prehb['lucky_guys'],context)
    print(prehb)

def rain(update: Update, _: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("?????????", callback_data='3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('??????????????????', reply_markup=reply_markup)


def approve(update: Update, context: CallbackContext) -> None:
    prehb = context.bot_data['prehb'] if context.bot_data.get('prehb') else {}
    if update.message.from_user.name in adminDict and update.message.from_user.name not in prehb['approvelist']:

        prehb['approvelist'].append(update.message.from_user.name)
        prehb['approveweight'] += adminDict[update.message.from_user.name]
        approveweight = prehb['approveweight']
        approvelist = prehb['approvelist']
        context.bot_data['prehb'] = prehb
        text = f'{approveweight}/{threshold}'+f'????????????:{approvelist}'
        balance = float(do_cmd("cleos -u https://eos.dfuse.eosnation.io get currency balance eosio.token eoscnadmin.e EOS").split(' EOS')[0])
        if approveweight > threshold:
            text += '???????????????????????? '
        if balance < prehb['full_balance']/10000.0:
            text += f',??????????????????{balance} EOS,?????????????????????'
        if approveweight > threshold and balance > prehb['full_balance']/10000.0 and prehb['actived'] == False:
            prehb['actived'] = True
            text += f',??????????????????{balance} EOS,??????????????????'

        print(prehb)
        update.message.reply_text(text )

def address(update: Update, context: CallbackContext) -> None:
    if context.bot_data.get('userDict'):
        userDict = context.bot_data['userDict']
    else:
        userDict = {}
    if len(context.args[0])<14 and is_acaount(context.args[0]):
        userInfo = {}
        userInfo['name'] = update.message.from_user.name
        userInfo['full_name'] = update.message.from_user.full_name
        userInfo['id'] = update.message.from_user.id 
        userInfo['address'] = context.args[0]
        userInfo['balance'] = 0
        userDict[userInfo['id']]  = userInfo
        context.bot_data['userDict'] = userDict
        update.message.reply_text(f'{userInfo}' )
    else:
        update.message.reply_text(f'????????????????????????????????????eos??????????????????????????????' )


def main() -> None:
    # Create the Updater and pass it your bot's token.
    persistence = PicklePersistence(filename='conversationbot')
    updater = Updater("133333378:AAxxxxxxxxxxxxxxxxxxnPU", persistence=persistence)


    updater.dispatcher.add_handler(CommandHandler('rain', rain))
    
    updater.dispatcher.add_handler(CommandHandler('approve', approve))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))


    updater.dispatcher.add_handler(CommandHandler('addhb', addhb))
    updater.dispatcher.add_handler(CommandHandler('address', address))


    

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
