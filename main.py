import asyncio
import random
from aiogram import Bot, Dispatcher, types, executor
from supabase import create_client

# 🔑 الإعدادات
SUPABASE_URL = "https://snlcbtgzdxsacwjipggn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNubGNidGd6ZHhzYWN3amlwZ2duIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDU3NDMzMiwiZXhwIjoyMDg2MTUwMzMyfQ.v3SRkONLNlQw5LWhjo03u0fDce3EvWGBpJ02OGg5DEI"
BOT_TOKEN = "8587471594:AAEB0cRP3lrEFfP-vGTRC1B4sHhMCxYF6LM"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 📚 بنك الأسئلة التجريبي
QUESTIONS_BANK = [
    {"q": "ما هو اسم البنت التي يحبها ياسر؟", "a": "العنود"},
    {"q": "ما هي عاصمة اليمن؟", "a": "صنعاء"},
    {"q": "ما هي العملة الرقمية الأولى في العالم؟", "a": "بيتكوين"},
    {"q": "من هو صاحب لقب 'عميد الأدب العربي'؟", "a": "طه حسين"},
    {"q": "ما هو أكبر كوكب في المجموعة الشمسية؟", "a": "المشتري"}
]

# ⚖️ ميزان الإجابة (التنقية الذكية)
def clean_text(text):
    if not text: return ""
    text = str(text).lower().strip()
    repls = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ة': 'ه', 'ى': 'ي'}
    for k, v in repls.items():
        text = text.replace(k, v)
    return text.replace(" ", "")

# 🛰️ رادار الرصد العالمي
@dp.message_handler(lambda m: not m.text.startswith('/'))
async def answer_monitor(m: types.Message):
    try:
        # فحص حالة المسابقة من سوبابيس
        res = supabase.table("global_system").select("*").eq("id", 1).single().execute()
        data = res.data
        
        if data and data['is_active']:
            user_ans = clean_text(m.text)
            correct_ans = clean_text(data['answer'])
            
            if user_ans == correct_ans:
                # 🏆 إيقاف المسابقة فوراً وتسجيل الفوز
                supabase.table("global_system").update({
                    "is_active": False,
                    "winner_name": m.from_user.full_name,
                    "winner_id": m.from_user.id
                }).eq("id", 1).execute()
                
                await m.reply(f"🎯 **كفو يا بطل!**\nإجابتك ({m.text}) صحيحة.\nلقد حصلت على **10 نقاط** في نظام الرصد! 🚀")
    except: pass

# 🚀 أمر تشغيل المسابقة (اختيار عشوائي)
@dp.message_handler(commands=['quiz'])
async def start_quiz(m: types.Message):
    # اختيار سؤال عشوائي من الخمسة
    item = random.choice(QUESTIONS_BANK)
    
    # تحديث سوبابيس (تفعيل الرادار)
    supabase.table("global_system").update({
        "is_active": True,
        "question": item['q'],
        "answer": item['a'],
        "start_time": "now()"
    }).eq("id", 1).execute()
    
    await m.answer(f"🔥 **تحدي جديد انطلق!**\n\nالسؤال: **{item['q']}**\n\n⏳ لديك **20 ثانية** للإجابة!")

    # محاكي وقت الانتظار
    for _ in range(4): # 4 دورات كل دورة 5 ثواني = 20 ثانية
        await asyncio.sleep(5)
        chk = supabase.table("global_system").select("is_active").eq("id", 1).single().execute()
        if not chk.data['is_active']: return

    # إذا انتهى الوقت
    supabase.table("global_system").update({"is_active": False}).eq("id", 1).execute()
    await m.answer(f"⌛ **انتهى الوقت!**\nلم يجاوب أحد.. الإجابة كانت: **{item['a']}**")

if __name__ == '__main__':
    print("🚀 المختبر الخماسي يعمل الآن.. أرسل /quiz")
    executor.start_polling(dp, skip_updates=True)
