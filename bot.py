import telebot, json, time, schedule, threading, os
from gradio_client import Client
from flask import Flask

TOKEN = os.environ['TOKEN']
CHAT_ID = int(os.environ['CHAT_ID'])
HF = "https://arissuga-xauusd-ai-analyzer.hf.space/"
last_signal = ""
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home(): return "Bot XAU Running"

def cek_hf():
    for i in range(3):
        try:
            client = Client(HF, timeout=60)
            return json.loads(client.predict(api_name="/analyze"))
        except: time.sleep(15)
    return {"signal":"ERROR","reason":"HF Timeout"}

def kirim_signal():
    global last_signal
    d = cek_hf()
    signal = d.get("signal", "ERROR")
    if signal in ["BUY","SELL"] and signal != last_signal:
        rr = abs(d['tp']-d['entry'])/abs(d['sl']-d['entry'])
        txt = f"🚨 *{signal} XAUUSD* - H1 Entry\n\nEntry: `${d['entry']}`\nSL: `${d['sl']}`\nTP: `${d['tp']}`\nRR: `1:{round(rr,2)}`\nConfidence: `{d['confidence']}%`\n\n*Reason:* _{d['reason']}_"
        bot.send_message(CHAT_ID, txt, parse_mode="Markdown")
        last_signal = signal
    elif signal == "NO TRADE": 
        last_signal = "NO TRADE"
    else:
        bot.send_message(CHAT_ID, f"⚠️ ERROR\n{d.get('reason','Unknown')}")

@bot.message_handler(commands=['xau','start'])
def xau_cmd(msg):
    bot.reply_to(msg, "Cek H1... Tunggu 30 detik")
    threading.Thread(target=kirim_signal).start()

def run_schedule():
    schedule.every().hour.at(":01").do(kirim_signal)
    while True: schedule.run_pending(); time.sleep(1)

threading.Thread(target=lambda: app.run(host='0.0.0.0',port=int(os.environ.get("PORT", 10000)))).start()
threading.Thread(target=run_schedule).start()
print("Bot aktif")
bot.polling(non_stop=True)
