import os
import asyncio
import threading
from flask import Flask # للتعامل مع Render
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from openai import OpenAI
import nest_asyncio

nest_asyncio.apply()

# --- 1. جزء الـ Flask عشان Render ميقفلش البوت ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Kirov Bot is Alive!"

def run_flask():
    # Render بيحتاج يفتح Port عشان يعتبر الخدمة ناجحة
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# --- 2. إعدادات التوكنات ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API")

# إضافة حماية بسيطة عشان الكود ميعملش Error لو المفتاح مش موجود محلياً
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

# --- 3. وظائف معالجة الرسائل ---
async def handle_message(update, context):
    user_msg = update.message.text.lower()

    if "اسمك" in user_msg or "what is your name" in user_msg:
        await update.message.reply_text("أنا Kirov، المساعد الرسمي لشركة TayelMind.")
    elif "الشركة" in user_msg or "tayelmind" in user_msg:
        await update.message.reply_text(f"TayelMind هي {company_info['description']}")
    elif "المطور" in user_msg or "مين عملك" in user_msg or "who made you" in user_msg:
        await update.message.reply_text("تم تطويري بواسطة Adam Tayel (آدم طايل).")
    else:
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

# --- 4. تشغيل البوت ---
async def main_bot():
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found!")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is starting...")
    # استخدام initialize و start_polling لضمان استقرار العمل في الخلفية
    await app.initialize()
    await app.start_polling()
    
    # حلقة لانهائية لإبقاء البوت حياً
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    # تشغيل Flask في Thread منفصل (الخدعة اللي بتخلي Render يسيب البوت شغال)
    threading.Thread(target=run_flask, daemon=True).start()
    
    # تشغيل بوت تليجرام
    try:
        asyncio.run(main_bot())
    except KeyboardInterrupt:
        print("Bot stopped.")