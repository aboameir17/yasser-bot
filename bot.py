import asyncio
import httpx
from aiogram import Bot, Dispatcher, types, executor

# --- [ الإعدادات الجديدة ] ---
API_TOKEN = "8587471594:AAEDUgePR4dToTkxeJkrhFL3sWo0nFUY1yU"
GROQ_API_KEY = "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"

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# دالة توليد التلميح الذكي (الملكية)
async def generate_smart_hint(word):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": f"أعطني لغزاً ذكياً وقصيراً عن كلمة ({word}) دون ذكرها."}],
        "temperature": 0.6
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
    except:
        return "فشل الاتصال بالذكاء الاصطناعي"

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("🚀 **بوت اختبار التلميحات يعمل!**\nارسل لي أي كلمة وسأعطيك تلميحاً ذكياً لها.")

@dp.message_handler()
async def handle_all_messages(message: types.Message):
    word = message.text
    await message.answer(f"🔄 جاري تفكير الذكاء الاصطناعي في كلمة: {word}...")
    hint = await generate_smart_hint(word)
    
    res = (
        f"💎 <b>〔 تـلـمـيـح ذكـي نـادر 〕</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"📜 <b>الوصف:</b> <i>{hint}</i>\n"
        f"━━━━━━━━━━━━━━"
    )
    await message.answer(res)

if __name__ == '__main__':
    print("✅ البوت شغال الآن.. اذهب لتلجرام وجربه!")
    executor.start_polling(dp, skip_updates=True)
