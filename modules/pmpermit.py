# For The-TG-Bot v3
# Syntax (.approve, .block)


import asyncio
import json
from modules.sql.pmpermit_sql import is_approved, approve, disapprove, get_all_approved
from telethon.tl import functions, types

client.storage.PM_WARNS = {}
client.storage.PREV_REPLY_MESSAGE = {}
BAALAJI_TG_USER_BOT = "```My Master hasn't approved you to PM.```"
TG_COMPANION_USER_BOT = "```Wait for my masters response.\nDo not spam his pm if you do not want to get blocked.```"
THETGBOT_USER_BOT_WARN_ZERO = "```Blocked! Thanks for the spam.```"
THETGBOT_USER_BOT_NO_WARN = "\
```Bleep blop! This is a client. Don't fret.\
\nMy master hasn't approved you to PM.\
\nPlease wait for my master to look in, he mostly approves PMs.\
\nAs far as I know, he doesn't usually approve retards though.\
\nIf you continue sending messages you will be blocked.```\
"


@client.on(register(incoming=True, func=lambda e: e.is_private))
async def monito_p_m_s(event):
    sender = await event.get_sender()
    current_message_text = event.message.message.lower()
    if current_message_text == BAALAJI_TG_USER_BOT or \
            current_message_text == TG_COMPANION_USER_BOT or \
            current_message_text == THETGBOT_USER_BOT_NO_WARN:
        # userbot's should not reply to other userbot's
        # https://core.telegram.org/bots/faq#why-doesn-39t-my-bot-see-messages-from-other-bots
        return False
    if Config.ANTI_PM_SPAM and not sender.bot:
        chat = await event.get_chat()
        if not is_approved(chat.id) and chat.id != client.uid:
            logger.info(chat.stringify())
            logger.info(client.storage.PM_WARNS)
            if chat.id in Config.SUDO_USERS:
                await event.edit("Oh wait, that looks like my master!")
                await event.edit("Approving..")
                approve(chat.id, "SUDO_USER")
            if chat.id not in client.storage.PM_WARNS:
                client.storage.PM_WARNS.update({chat.id: 0})
            if client.storage.PM_WARNS[chat.id] == Config.MAX_PM_FLOOD:
                r = await event.reply(THETGBOT_USER_BOT_WARN_ZERO)
                await asyncio.sleep(3)
                await client(functions.contacts.BlockRequest(chat.id))
                if chat.id in client.storage.PREV_REPLY_MESSAGE:
                    await client.storage.PREV_REPLY_MESSAGE[chat.id].delete()
                client.storage.PREV_REPLY_MESSAGE[chat.id] = r
                return
            r = await event.reply(f"{THETGBOT_USER_BOT_NO_WARN}\n`Messages remaining: {int(Config.MAX_PM_FLOOD - client.storage.PM_WARNS[chat.id])} out of {int(Config.MAX_PM_FLOOD)}`")
            client.storage.PM_WARNS[chat.id] += 1
            if chat.id in client.storage.PREV_REPLY_MESSAGE:
                await client.storage.PREV_REPLY_MESSAGE[chat.id].delete()
            client.storage.PREV_REPLY_MESSAGE[chat.id] = r


@client.on(register("approve ?(.*)"))
async def approve_p_m(event):
    if event.fwd_from:
        return
    reason = event.pattern_match.group(1)
    chat = await event.get_chat()
    if Config.ANTI_PM_SPAM:
        if event.is_private:
            if not is_approved(chat.id):
                if chat.id in client.storage.PM_WARNS:
                    del client.storage.PM_WARNS[chat.id]
                if chat.id in client.storage.PREV_REPLY_MESSAGE:
                    await client.storage.PREV_REPLY_MESSAGE[chat.id].delete()
                    del client.storage.PREV_REPLY_MESSAGE[chat.id]
                approve(chat.id, reason)
                await event.edit("PM accepted.")
                await asyncio.sleep(3)
                await event.delete()


@client.on(register("block ?(.*)"))
async def approve_p_m(event):
    if event.fwd_from:
        return
    reason = event.pattern_match.group(1)
    chat = await event.get_chat()
    if Config.ANTI_PM_SPAM:
        if event.is_private:
            if is_approved(chat.id):
                disapprove(chat.id)
                await event.edit("Blocked PM.")
                await asyncio.sleep(3)
                await client(functions.contacts.BlockRequest(chat.id))


@client.on(register("approvedpms"))
async def approve_p_m(event):
    if event.fwd_from:
        return
    approved_users = get_all_approved()
    APPROVED_PMs = "Current Approved PMs\n"
    for a_user in approved_users:
        if a_user.reason:
            APPROVED_PMs += f"* [{a_user.chat_id}](tg://user?id={a_user.chat_id}) for {a_user.reason}\n"
        else:
            APPROVED_PMs += f"* [{a_user.chat_id}](tg://user?id={a_user.chat_id})\n"
    if len(APPROVED_PMs) > Config.MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(APPROVED_PMs)) as out_file:
            out_file.name = "approved.pms.text"
            await client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="Current Approved PMs",
                reply_to=event
            )
            await event.delete()
    else:
        await event.edit(APPROVED_PMs)


Config.HELPER.update({
    "pmpermit": "\
```.approve```\
\nUsage: Approve a user in PMs.\
\n\n```.block```\
\nUsage: Block a user from your PMs.\
"
})
