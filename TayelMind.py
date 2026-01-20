import os
import asyncio
import threading
from flask import Flask 
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from openai import OpenAI
import nest_asyncio

nest_asyncio.apply()

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Kirov Bot is Alive!"

def run_flask():
    # Use Render port
    port = int(os.environ.get("PORT", 10000)) 
    app_flask.run(host='0.0.0.0', port=port)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API")

if not OPENAI_API_KEY:
    print("Warning: OPENAI_API environment variable is not set!")
    client = None
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

company_info = {
    "name": "TayelMind",
    "description": (
        "شركة متخصصة في تطوير تطبيقات الذكاء الاصطناعي، "
        "وتعمل في مجالات Chatbots، Machine Learning، "
        "Deep Learning، و Data Science."
    )
}

# Handle incoming messages
async def handle_message(update, context):
    if not update.message or not update.message.text:
        return
    
    # Get user details
    user = update.message.from_user
    user_name = user.first_name
    user_id = user.id
    username = f"@{user.username}" if user.username else "No Username"
    user_msg = update.message.text
    
    # Print user info in Render logs
    print(f"--- New Message from {user_name} ({username}) ID: {user_id} ---")
    print(f"Text: {user_msg}")

    user_msg_lower = user_msg.lower()

    # Predefined responses
    if "اسمك" in user_msg_lower or "what is your name" in user_msg_lower:
        await update.message.reply_text("أنا Kirov، المساعد الرسمي لشركة TayelMind.")
    elif "الشركة" in user_msg_lower or "tayelmind" in user_msg_lower:
        await update.message.reply_text(f"TayelMind هي {company_info['description']}")
    elif "المطور" in user_msg_lower or "مين عملك" in user_msg_lower or "who made you" in user_msg_lower:
        await update.message.reply_text("تم تطويري بواسطة Adam Tayel (آدم طايل).")
    else:
        # AI Response
        if client is None:
            await update.message.reply_text("عذراً، نظام الذكاء الاصطناعي غير متصل حالياً.")
            return

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"انت بوت اسمه Kirov. انت المساعد الرسمي لشركة {company_info['name']}. وصف الشركة: {company_info['description']}. تم تطويرك بواسطة: Adam Tayel. جاوب بالعربي."
                },
                {"role": "user", "content": user_msg}
            ]
        )
        await update.message.reply_text(response.choices[0].message.content)

# Start the bot
async def main_bot():
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found!")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is starting...")
    
    # run_polling with close_loop=False to avoid RuntimeError
    await app.run_polling(close_loop=False)

if __name__ == "__main__":
    # Run Flask in a separate thread
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Run Telegram Bot
    try:
        asyncio.run(main_bot())
    except Exception as e:
        print(f"Error occurred: {e}")