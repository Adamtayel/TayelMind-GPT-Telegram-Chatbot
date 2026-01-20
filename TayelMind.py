
# pip install python-telegram-bot openai nest_asyncio
import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters

import nest_asyncio
nest_asyncio.apply()  # لو شغال على Jupyter/Notebook

from telegram.ext import ApplicationBuilder, MessageHandler, filters
from openai import OpenAI

# tokens

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API")
# 2️⃣ تهيئة OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)
company_info = {
    "name": "TayelMind",
    "description": (
        "شركة متخصصة في تطوير تطبيقات الذكاء الاصطناعي، "
        "وتعمل في مجالات Chatbots، Machine Learning، "
        "Deep Learning، و Data Science."
    )
}

# handle message functions
async def handle_message(update, context):
    user_msg = update.message.text.lower()


    if "اسمك" in user_msg or "what is your name" in user_msg:
        await update.message.reply_text(
            "أنا Kirov، المساعد الرسمي لشركة TayelMind."
        )

    elif "الشركة" in user_msg or "tayelmind" in user_msg:
        await update.message.reply_text(
            f"TayelMind هي {company_info['description']}"
        )

    elif "المطور" in user_msg or "مين عملك" in user_msg or "who made you" in user_msg:
        await update.message.reply_text(
            "تم تطويري بواسطة Adam Tayel (آدم طايل)."
        )

    else:
        # أي رسالة أخرى → GPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""
انت بوت اسمه Kirov.
انت المساعد الرسمي لشركة {company_info['name']}.

وصف الشركة:
{company_info['description']}

تم تطويرك بواسطة:
Adam Tayel (آدم طايل)

وظيفتك مساعدة المستخدمين والرد على أسئلتهم بطريقة لطيفة واحترافية.
جاوب دايمًا بالعربي إلا لو المستخدم طلب غير كده.
"""
                },
                {"role": "user", "content": user_msg}
            ]
        )

        await update.message.reply_text(
            response.choices[0].message.content
        )
# turn on bot
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    await app.run_polling()

# deploy

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

