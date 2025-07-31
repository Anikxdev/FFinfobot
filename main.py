import os
import requests
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Bot Configuration
TOKEN = os.environ.get("TOKEN")  # Use environment variable for Render
API_URL = "https://nr-codex-info.vercel.app/get?uid="

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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
    
    logging.info(f"Fetching data for FF ID: {user_input}")
    
    try:
        # Fetch data from API
        response = requests.get(f"{API_URL}{user_input}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Format and send response
        formatted = format_player_data(data)
        await update.message.reply_text(formatted)
        
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"⚠️ API Error: {str(e)}")
    except ValueError:
        await update.message.reply_text("⚠️ Invalid response from server")
    except KeyError:
        await update.message.reply_text("⚠️ Missing data in API response")

def format_timestamp(ts: str) -> str:
    """Convert Unix timestamp to readable date"""
    try:
        return datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return "N/A"

def format_player_data(data: dict) -> str:
    """Format JSON response into readable message"""
    acc = data.get('AccountInfo', {})
    social = data.get('socialinfo', {})
    guild = data.get('GuildInfo', {})
    pet = data.get('petInfo', {})
    
    # Format pet info if available
    pet_info = ""
    if pet:
        pet_info = (
            f"🐾 Pet: ID {pet.get('id', 'N/A')} (Lvl {pet.get('level', 'N/A')})\n"
            f"🔮 Pet Skill: {pet.get('selectedSkillId', 'N/A')}\n"
        )
    
    # Format guild info
    guild_info = "🏰 Guild: None"
    if guild.get('GuildName'):
        guild_info = (
            f"🏰 Guild: {guild.get('GuildName', 'N/A')}\n"
            f"👑 Owner: {guild.get('GuildOwner', 'N/A')}\n"
            f"👥 Members: {guild.get('GuildMember', 'N/A')}"
        )
    
    return (
        f"🎮 Free Fire Player Stats 🎮\n\n"
        f"🆔 ID: {social.get('accountId', 'N/A')}\n"
        f"👤 Name: {acc.get('AccountName', 'N/A')}\n"
        f"📝 Status: {social.get('signature', 'N/A')}\n"
        f"🌐 Region: {acc.get('AccountRegion', 'N/A')}\n"
        f"⭐ Level: {acc.get('AccountLevel', 'N/A')}\n"
        f"❤ Likes: {acc.get('AccountLikes', 'N/A')}\n\n"
        
        f"🏆 Battle Royale Rank: {acc.get('BrMaxRank', 'N/A')}\n"
        f"📊 BR Points: {acc.get('BrRankPoint', 'N/A')}\n\n"
        
        f"{guild_info}\n\n"
        
        f"{pet_info}\n"
        f"🕒 Created: {format_timestamp(acc.get('AccountCreateTime', ''))}\n"
        f"⏱ Last Login: {format_timestamp(acc.get('AccountLastLogin', ''))}"
    )

if __name__ == '__main__':
    # Create Bot Application
    app = Application.builder().token(TOKEN).build()
    
    # Register Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ffid))
    
    # Run Bot
    logging.info("Bot is running...")
    app.run_polling()
