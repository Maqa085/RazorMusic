# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic
import asyncio
import re
from pyrogram import errors, filters, types
from anony import anon, app, db, lang, queue, tg, yt
from anony.helpers import admin_check, buttons, can_manage_vc
@app.on_callback_query(filters.regex("cancel_dl") & ~app.bl_users)
@lang.language()
async def cancel_dl(_, query: types.CallbackQuery):
    await query.answer()
    await tg.cancel(query)
@app.on_callback_query(filters.regex("close_menu"))
async def close_menu_handler(_, query):
    try:
        # Düyməyə basan adamın adını götürürük
        user_name = query.from_user.mention
        # Əsas menyu mesajını silirik
        await query.message.delete()
        # Bildiriş mesajını göndəririk və bir dəyişənə bərabər edirik
        notification = await query.message.reply_text(f"📋 Menyu {user_name}
Tərəfindən Bağlandı.")
        # 4 saniyə gözləyirik
        await asyncio.sleep(4)
        # Bildiriş mesajını silirik
        await notification.delete()
    except Exception as e:
        # Mesaj artıq silinibsə və ya icazə yoxdursa xəta konsola düşür
        print(f"Bağla düyməsi xətası: {e}")
@app.on_callback_query(filters.regex(r"song_download"))
async def song_download_callback(_, query):
    data = query.data.split()
    mode = data[1] # mp3 və ya video
    vidid = data[2]
    url = f"https://www.youtube.com/watch?v={vidid}"
    await query.edit_message_caption("📥 Yüklənir... Xahiş edirik gözləyin.")    # Yükləmə qovluğu yoxdursa yaradırıq
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    # Yükləmə ayarları
    ydl_opts = {
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'cookiefile': config.COOKIE_FILE if hasattr(config, "COOKIE_FILE") else None,
        'quiet': True
    }
    if mode == "mp3":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts.update({'format': 'best'})
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if mode == "mp3":
                file_path = file_path.rsplit(".", 1)[0] + ".mp3"
        await query.edit_message_caption("📤 Göndərilir...")
        if mode == "mp3":
            await query.message.reply_audio(
                audio=file_path,
                title=info.get('title', 'Musiqi'),
                performer=f"@{app.username}", # Sənətçi yerinə Bot Username
                caption=f"✅   @{app.username} vasitəsilə yükləndi"
            )
        else:
            await query.message.reply_video(
                video=file_path,
                caption=f"🎬 <b>{info.get('title', 'Video')}</b>\n\n✅   @{app.username} vasitəsilə yükləndi"
            )
        # Orijinal menyu mesajını silirik
        await query.message.delete()
    except Exception as e:
        await query.message.reply_text(f"❌   Yükləmə xətası: {e}")
    # Faylı serverdən silirik ki, yaddaş dolmasın
    if os.path.exists(file_path):
        os.remove(file_path)
@app.on_callback_query(filters.regex("controls") & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _controls(_, query: types.CallbackQuery):
    args = query.data.split()
    action, chat_id = args[1], int(args[2])
    qaction = len(args) == 4
    user = query.from_user.mention
    if not await db.get_call(chat_id):
        try:
            return await query.answer(query.lang["not_playing"], show_alert=True)
        except errors.QueryIdInvalid:
            try:
                await query.message.delete()
            except Exception:
                pass
            return
    if action == "status":
        return await query.answer()
    await query.answer(query.lang["processing"], show_alert=True)
    if action == "pause":
        if not await db.playing(chat_id):
            return await query.answer(
                query.lang["play_already_paused"], show_alert=True
            )
        await anon.pause(chat_id)
        if qaction:
            return await query.edit_message_reply_markup(
                reply_markup=buttons.queue_markup(chat_id, query.lang["paused"], False)
            )
        status = query.lang["paused"]
        reply = query.lang["play_paused"].format(user)
    elif action == "resume":
        if await db.playing(chat_id):
            return await query.answer(query.lang["play_not_paused"], show_alert=True)
        await anon.resume(chat_id)
        if qaction:
            return await query.edit_message_reply_markup(
                reply_markup=buttons.queue_markup(chat_id, query.lang["playing"], True)
            )
        reply = query.lang["play_resumed"].format(user)
    elif action == "skip":
        await anon.play_next(chat_id)
        status = query.lang["skipped"]
        reply = query.lang["play_skipped"].format(user)
    elif action == "force":
        pos, media = queue.check_item(chat_id, args[3])
        if not media or pos == -1:
            return await query.edit_message_text(query.lang["play_expired"])
        m_id = queue.get_current(chat_id).message_id
        queue.force_add(chat_id, media, remove=pos)
        try:
            await app.delete_messages(
                chat_id=chat_id, message_ids=[m_id, media.message_id], revoke=True
            )
            media.message_id = None
        except Exception:
            pass
        msg = await app.send_message(chat_id=chat_id, text=query.lang["play_next"])
        if not media.file_path:
            media.file_path = await yt.download(media.id, video=media.video)
        media.message_id = msg.id
        return await anon.play_media(chat_id, msg, media)
    elif action == "replay":
        media = queue.get_current(chat_id)
        media.user = user
        await anon.replay(chat_id)
        status = query.lang["replayed"]
        reply = query.lang["play_replayed"].format(user)
    elif action == "stop":
        await anon.stop(chat_id)
        status = query.lang["stopped"]
        reply = query.lang["play_stopped"].format(user)
    try:
        if action in ["skip", "replay", "stop"]:
            await query.message.reply_text(reply, quote=False)
            await query.message.delete()
        else:
            mtext = re.sub(
                r"\n\n<blockquote>.*?</blockquote>",
                "",
                query.message.caption.html or query.message.text.html,
                flags=re.DOTALL,
            )
            keyboard = buttons.controls(
                chat_id, status=status if action != "resume" else None
            )
        await query.edit_message_text(
            f"{mtext}\n\n<blockquote>{reply}</blockquote>", reply_markup=keyboard
        )
    except Exception:
        pass
@app.on_callback_query(filters.regex("help") & ~app.bl_users)
@lang.language()
async def _help(_, query: types.CallbackQuery):
    data = query.data.split()
    if len(data) == 1:
        return await query.answer(url=f"https://t.me/{app.username}?start=help")
    if data[1] == "back":
        return await query.edit_message_text(
            text=query.lang["help_menu"], reply_markup=buttons.help_markup(query.lang)
        )
    elif data[1] == "close":
        try:
            await query.message.delete()
            return await query.message.reply_to_message.delete()
        except Exception:
            return
    await query.edit_message_text(
        text=query.lang[f"help_{data[1]}"],
        reply_markup=buttons.help_markup(query.lang, True),
    )
@app.on_callback_query(filters.regex("settings") & ~app.bl_users)
@lang.language()
@admin_check
async def _settings_cb(_, query: types.CallbackQuery):
    cmd = query.data.split()
    if len(cmd) == 1:
        return await query.answer()
    await query.answer(query.lang["processing"], show_alert=True)
    chat_id = query.message.chat.id
    _admin = await db.get_play_mode(chat_id)
    _delete = await db.get_cmd_delete(chat_id)
    _language = await db.get_lang(chat_id)
    if cmd[1] == "delete":
        _delete = not _delete
        await db.set_cmd_delete(chat_id, _delete)
    elif cmd[1] == "play":
        await db.set_play_mode(chat_id, _admin)
        _admin = not _admin
    await query.edit_message_reply_markup(
        reply_markup=buttons.settings_markup(
            query.lang,
            _admin,
            _delete,
            _language,
            chat_id,
        )
        )
