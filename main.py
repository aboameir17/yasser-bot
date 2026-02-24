import asyncio, os, httpx, logging
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, executor
from aiohttp import web

# --- [ الإعدادات - مفاتيحك الملكية ] ---
API_TOKEN = "8587471594:AAEDUgePR4dToTkxeJkrhFL3sWo0nFUY1yU"
GROQ_API_KEY = "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"
GEMINI_API_KEY = "AIzaSyBB6hSieJutCAx1jdZSi_h6kUfERIVV1C4"

# إعداد المحركات
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# --- [ دالة محرك جورب (Groq) ] ---
async def get_groq_hint(word):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": f"أعطني لغزاً ذكياً جداً عن كلمة ({word}) بدون ذكر اسمها."}],
        "temperature": 0.6
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, json=payload, headers=headers, timeout=15.0)
            text = res.json()['choices'][0]['message']['content'].strip()
            return f"🐺 <b>〔 تـلـمـيـح جـورب - Groq 〕</b>\n━━━━━━━━━━━━━━\n📜 <i>{text}</i>\n━━━━━━━━━━━━━━"
    except: return "⚠️ محرك جورب (Groq) واجه مشكلة."

# --- [ دالة محرك الاختبار (Gemini) ] ---
async def get_gemini_hint(word):
    try:
        response = await asyncio.to_thread(gemini_model.generate_content, f"لغز غامض وذكي جداً عن {word} بدون ذكر الكلمة.")
        text = response.text.strip()
        return f"💎 <b>〔 تـلـمـيـح اخـتـبـار - Gemini 〕</b>\n━━━━━━━━━━━━━━\n📜 <i>{text}</i>\n━━━━━━━━━━━━━━"
    except: return "⚠️ محرك الاختبار (Gemini) واجه مشكلة."

# --- [ معالجة الرسائل - تشغيل الاثنين معاً ] ---

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    await m.answer("🚀 <b>مرحباً بك في سباق العمالقة!</b>\n\nأرسل أي كلمة الآن، وسيقوم <b>Gemini</b> و <b>Groq</b> بتوليد تلميحاتهما في نفس الوقت!")

@dp.message_handler()
async def duel_mode(m: types.Message):
    word = m.text.strip()
    
    # رسالة انتظار أولية
    status_msg = await m.answer(f"⏳ جاري استنفار الذكاء الاصطناعي لـ (<b>{word}</b>)...")

    # تشغيل الدالتين في نفس الوقت (Concurrent execution)
    results = await asyncio.gather(
        get_gemini_hint(word),
        get_groq_hint(word)
    )

    # حذف رسالة الانتظار
    await status_msg.delete()

    # إرسال النتائج
    for result in results:
        await m.answer(result)

# --- [ إعدادات الويب للبقاء حياً لـ Render ] ---
async def handle_ping(request): return web.Response(text="Active")

if __name__ == '__main__':
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app); loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.setup())
    port = int(os.environ.get("PORT", 10000))
    loop.create_task(web.TCPSite(runner, '0.0.0.0', port).start())
    
    print("✅ نظام السباق المزدوج شغال.. انطلق يا ياسر!")
    executor.start_polling(dp, skip_updates=True)
