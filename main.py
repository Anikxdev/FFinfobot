import os
import requests
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration from environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_URL = "https://nr-codex-info.vercel.app/get?uid="

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when user sends /start"""
    await update.message.reply_text(
        "🎮 Free Fire ID Lookup Bot 🎮\n\n"
        "Send me a Free Fire ID to get player information!"
    )

async def handle_ffid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle FF ID requests"""
    user_input = update.message.text.strip()
    
    # Validate input
    if not user_input.isdigit():
        await update.message.reply_text("❌ Please enter a valid numeric Free Fire ID!")
        return
    
    logger.info(f"Fetching data for FF ID: {user_input}")
    
    try:
        # Fetch data from API
        response = requests.get(f"{API_URL}{user_input}", timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Format and send response
        formatted = format_player_data(data)
        await update.message.reply_text(formatted)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API Error: {str(e)}")
        await update.message.reply_text("⚠️ Couldn't fetch player data. Please try again later.")
    except Exception as e:
        logger.exception("Unexpected error:")
        await update.message.reply_text("⚠️ An unexpected error occurred. Please try again.")

def format_timestamp(ts: str) -> str:
    """Convert Unix timestamp to readable date"""
    try:
        return datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        return "N/A"

def format_player_data(data: dict) -> str:
    """Format JSON response into readable message"""
    acc = data.get('AccountInfo', {})
    social = data.get('socialinfo', {})
    guild = data.get('GuildInfo', {})
    pet = data.get('petInfo', {})
    profile = data.get('AccountProfileInfo', {})
    
    # Basic info
    result = [
        f"🎮 *Free Fire Player Stats* 🎮",
        f"🆔 *ID:* `{social.get('accountId', 'N/A')}`",
        f"👤 *Name:* {acc.get('AccountName', 'N/A')}",
        f"📝 *Status:* {social.get('signature', 'N/A')}",
        f"🌐 *Region:* {acc.get('AccountRegion', 'N/A')}",
        f"⭐ *Level:* {acc.get('AccountLevel', 'N/A')}",
        f"❤ *Likes:* {acc.get('AccountLikes', 'N/A')}",
        "",
        f"🏆 *Battle Royale Rank:* {acc.get('BrMaxRank', 'N/A')}",
        f"📊 *BR Points:* {acc.get('BrRankPoint', 'N/A')}",
        ""
    ]
    
    # Guild info
    if guild.get('GuildName'):
        result.extend([
            f"🏰 *Guild Info*",
            f"• Name: {guild.get('GuildName', 'N/A')}",
            f"• Owner: {guild.get('GuildOwner', 'N/A')}",
            f"• Members: {guild.get('GuildMember', 'N/A')}",
            ""
        ])
    
    # Pet info
    if pet:
        result.extend([
            f"🐾 *Pet Info*",
            f"• ID: {pet.get('id', 'N/A')}",
            f"• Level: {pet.get('level', 'N/A')}",
            f"• Skill: {pet.get('selectedSkillId', 'N/A')}",
            ""
        ])
    
    # Timestamps
    result.extend([
        f"🕒 *Created:* {format_timestamp(acc.get('AccountCreateTime', ''))}",
        f"⏱ *Last Login:* {format_timestamp(acc.get('AccountLastLogin', ''))}",
        "",
        f"🔫 *Equipped Weapons:* {', '.join(map(str, acc.get('EquippedWeapon', []))}",
        f"👕 *Equipped Outfit:* {', '.join(map(str, profile.get('EquippedOutfit', []))}"
    ])
    
    return "\n".join(result)

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ffid))
    
    # Run the bot
    logger.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
