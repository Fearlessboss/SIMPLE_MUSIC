# -----------------------------------------------
# 🔸 SIMPLE MUSIC Project
# 🔹 Developed & Maintained by: Simple Boy (https://github.com/Simple-Boy-1k)
# 📅 Copyright © 2026 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by Simple_Boy_1k
# -----------------------------------------------
import re
import random
import config
from SIMPLE_MUSIC import app
from config import BOT_USERNAME
from SIMPLE_MUSIC.utils.Simple_ban import admin_filter
from SIMPLE_MUSIC.mongo.filtersdb import *
from SIMPLE_MUSIC.utils.filters_func import GetFIlterMessage, get_text_reason, SendFilterMessage
from SIMPLE_MUSIC.utils.senoritadb import user_admin
from pyrogram import filters, enums
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

STYLES = [
    enums.ButtonStyle.PRIMARY,
    enums.ButtonStyle.SUCCESS,
    enums.ButtonStyle.DANGER
]

def _get_style(style_val):
    if getattr(config, "BUTTON_COLOUR", False):
        return {"style": style_val}
    return {}

@app.on_message(filters.command("filter") & admin_filter)
@user_admin
async def _filter(client, message):
    chat_id = message.chat.id 
    if message.reply_to_message and not len(message.command) == 2:
        await message.reply("You need to give the filter a name!")  
        return 
    
    filter_name, filter_reason = get_text_reason(message)
    if message.reply_to_message and not len(message.command) >= 2:
        await message.reply("You need to give the filter some content!")
        return

    # Clean and lowercase string for database uniformity
    filter_name = filter_name.strip().lower()

    content, text, data_type = await GetFIlterMessage(message)
    await add_filter_db(chat_id, filter_name=filter_name, content=content, text=text, data_type=data_type)
    await message.reply(f"Saved filter '`{filter_name}`'.")


@app.on_message(~filters.bot & filters.group, group=4)
async def FilterCheckker(client, message):
    if not message.text:
        return
    
    text = message.text.strip().lower()
    chat_id = message.chat.id
    
    # FIX 1: Agar text exact ya sirf "bye" se start/end ho raha hai, toh filter check skip ho jayega.
    # Isse default bye wala automatic reply is file se trigger nahi hoga.
    if text == "bye" or text.startswith("bye ") or text.endswith(" bye"):
        return

    ALL_FILTERS = await get_filters_list(chat_id)
    if not ALL_FILTERS or len(ALL_FILTERS) == 0:
        return

    for filter_ in ALL_FILTERS:
        if (
            message.command
            and message.command[0] == 'filter'
            and len(message.command) >= 2
            and message.command[1].lower() == filter_.lower()
        ):
            return
            
        pattern = r"( |^|[^\w])" + re.escape(filter_.lower()) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            filter_name, content, text, data_type = await get_filter(chat_id, filter_)
            await SendFilterMessage(
                message=message,
                filter_name=filter_,
                content=content,
                text=text,
                data_type=data_type
            )

@app.on_message(filters.command('filters') & filters.group)
async def _filters(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title 
    if message.chat.type == enums.ChatType.PRIVATE:
        chat_title = 'local'
    FILTERS = await get_filters_list(chat_id)
    
    if not FILTERS or len(FILTERS) == 0:
        await message.reply(f'No filters in {chat_title}.')
        return

    filters_list = f'List of filters in {chat_title}:\n'
    for filter_ in FILTERS:
        filters_list += f'- `{filter_}`\n'
    
    await message.reply(filters_list)


@app.on_message(filters.command('stopall') & admin_filter)
async def stopall(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title 
    user = await client.get_chat_member(chat_id, message.from_user.id)
    if not user.status == ChatMemberStatus.OWNER:
        return await message.reply_text("Only Owner Can Use This!!") 

    r1, r2 = random.choices(STYLES, k=2)
    KEYBOARD = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Delete all filters', callback_data='custfilters_stopall', **_get_style(r1))],
        [InlineKeyboardButton(text='Cancel', callback_data='custfilters_cancel', **_get_style(r2))]]
    )

    await message.reply(
        text=(f'Are you sure you want to stop **ALL** filters in {chat_title}? This action is irreversible.'),
        reply_markup=KEYBOARD
    )


@app.on_callback_query(filters.regex("^custfilters_"))
async def stopall_callback(client, callback_query: CallbackQuery):  
    chat_id = callback_query.message.chat.id 
    query_data = callback_query.data.split('_')[1]  

    user = await client.get_chat_member(chat_id, callback_query.from_user.id)
    if not user.status == ChatMemberStatus.OWNER:
        return await callback_query.answer("Only Owner Can Use This!!", show_alert=True) 
    
    if query_data == 'stopall':
        await stop_all_db(chat_id)
        await callback_query.edit_message_text(text="I've deleted all chat filters.")
    elif query_data == 'cancel':
        await callback_query.edit_message_text(text='Cancelled.')


# FIX 2: Stopfilter function ko robust banaya gaya hai taaki MongoDB me case-matching fail na ho
@app.on_message(filters.command(['stopfilter', 'stop']) & admin_filter)
@user_admin
async def stop(client, message):
    chat_id = message.chat.id
    
    # Agar sirf /stopfilter likha ho bina naam ke
    if len(message.command) < 2:
        await message.reply('Please specify a filter name. Example: `/stopfilter bye`')
        return
    
    # Jo naam user ne type kiya use space clean aur lower-case karo
    filter_name = " ".join(message.command[1:]).strip().lower()
    
    # DB se saare saved filters ki list nikalo
    current_filters = await get_filters_list(chat_id)
    
    if not current_filters:
        await message.reply("You haven't saved any filters in this group yet!")
        return
        
    # Case-insensitive dhoondhne ke liye temp list
    current_filters_lowercase = [f.lower() for f in current_filters]

    if filter_name not in current_filters_lowercase:
        await message.reply(f"You haven't saved any filter on word `{filter_name}` yet!")
        return
    
    # Database me jis exact format me save tha (Capital/Small letter), wo real name nikalo
    actual_name = current_filters[current_filters_lowercase.index(filter_name)]
    
    try:
        # DB se delete command execute karein
        await stop_db(chat_id, actual_name)
        await message.reply(f"I've successfully stopped `{actual_name}`.")
    except Exception as e:
        await message.reply(f"Error while deleting filter from database: {e}")
