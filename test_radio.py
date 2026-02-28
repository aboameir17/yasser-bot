import asyncio
import random
from aiogram import Bot, Dispatcher, types, executor
from supabase import create_client

# 🔑 الإعدادات (نفس بياناتك)
SUPABASE_URL = "https://snlcbtgzdxsacwjipggn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNubGNidGd6ZHhzYWN3amlwZ2duIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDU3NDMzMiwiZXhwIjoyMDg2MTUwMzMyfQ.v3SRkONLNlQw5LWhjo03u0fDce3EvWGBpJ02OGg5DEI"
BOT_TOKEN = "8587471594:AAEB0cRP3lrEFfP-vGTRC1B4sHhMCxYF6LM"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 📚 بنك الأسئلة
QUESTIONS_BANK = [
    {"q": "ما هو اسم البنت التي يحبها ياسر؟", "a": "العنود"},
    {"q": "ما هي عاصمة اليمن؟", "a": "صنعاء"},
    {"q": "ما هي العملة الرقمية الأولى في العالم؟", "a": "بيتكوين"},
    {"q": "من هو صاحب لقب 'عميد الأدب العربي'؟", "a": "طه حسين"},
    {"q": "ما هو أكبر كوكب في المجموعة الشمسية؟", "a": "المشتري"}
]

# ⚖️ تنقية النصوص
def clean_text(text):
    if not text: return ""
    text = str(text).lower().strip()
    repls = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ة': 'ه', 'ى': 'ي'}
    for k, v in repls.items(): text = text.replace(k, v)
    return text.replace(" ", "")

# 🛰️ رادار الرصد (يسمع كل شيء)
@dp.message_handler()
async def global_handler(m: types.Message):
    # 1. تشغيل المسابقة بكلمة "مسابقة"
    if m.text == "مسابقة":
        item = random.choice(QUESTIONS_BANK)
        # تحديث سوبابيس
        supabase.table("global_system").update({
            "is_active": True,
            "question": item['q'],
            "answer": item['a']
        }).eq("id", 1).execute()
        
        await m.answer(f"🔥 **انطلق التحدي!**\n\nالسؤال: **{item['q']}**\n\n⏳ لديك **20 ثانية**!")
        
        # مؤقت 20 ثانية
        await asyncio.sleep(20)
        
        # فحص هل انتهت المسابقة بفوز أحد؟
        chk = supabase.table("global_system").select("is_active").eq("id", 1).single().execute()
        if chk.data['is_active']:
            supabase.table("global_system").update({"is_active": False}).eq("id", 1).execute()
            await m.answer(f"⌛ **انتهى الوقت!**\nالإجابة الصحيحة كانت: **{item['a']}**")
        return

    # 2. رصد الإجابة (إذا كانت المسابقة مفعلة)
    try:
        res = supabase.table("global_system").select("*").eq("id", 1).single().execute()
        if res.data and res.data['is_active']:
            if clean_text(m.text) == clean_text(res.data['answer']):
                supabase.table("global_system").update({
                    "is_active": False,
                    "winner_name": m.from_user.full_name
                }).eq("id", 1).execute()
                await m.reply(f"🎯 **كفو يا بطل!**\nإجابتك صحيحة، فزت بـ 10 نقاط! 🚀")
    except: pass

if __name__ == '__main__':
    print("🚀 البوت شغال الآن.. أرسل كلمة 'مسابقة' في الشات")
    # السطر السحري لحل مشكلة رندر
    executor.start_polling(dp, skip_updates=True, on_startup=lambda _: bot.delete_webhook(drop_pending_updates=True))
