import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

# Load bot token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Your API endpoint
API_URL = "https://nr-codex-info.vercel.app/get?uid="

# /get command handler
async def get_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("⚠️ Invalid format! Use: /get <uid>")
        return

    uid = context.args[0]
    processing_msg = await update.message.reply_text("🔄 Please wait...")

    try:
        response = requests.get(API_URL.format(uid), timeout=10)
        data = response.json()

        if data.get("status") != "success":
            await processing_msg.edit_text("❌ No data found for this UID.")
            return

        info = data.get("data", {})

        reply = f"""\
🎮 Player Information:
👤 Name: {info.get('name', 'N/A')}
⭐ Level: {info.get('level', 'N/A')}
❤️ Likes: {info.get('likes', 'N/A')}
🆔 UID: {info.get('uid', 'N/A')}
🌍 Server: {info.get('server', 'N/A')}
📝 Bio: {info.get('bio', 'N/A')}

📆 Account Created: {info.get('account_created', 'N/A')}
🎫 Booyah Pass Level: {info.get('booyah_pass_level', 'N/A')}

🔰 Guild Information:
🏷️ Guild Name: {info.get('guild_name', 'N/A')}
🏆 Guild Level: {info.get('guild_level', 'N/A')}
👥 Guild Members: {info.get('guild_members', 'N/A')}

🔗 Credits: {data.get("credits", 'N/A')}
"""
        await processing_msg.edit_text(reply)

    except Exception as e:
        await processing_msg.edit_text(f"⚠️ Error: {str(e)}")

# Main function
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("get", get_command))
    print("🤖 Bot is running...")
    app.run_polling()
