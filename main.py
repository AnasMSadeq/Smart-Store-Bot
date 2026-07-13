import os
import re
import uuid
import telebot
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from telebot import types
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
SHEET_NAME = "SmartStore_Orders"

if not TOKEN or not ADMIN_ID:
    print("Error: Environment variables missing.")
    exit(1)

bot = telebot.TeleBot(TOKEN)
user_data = {}

PRODUCTS = {
    "p1": {"name": "ساعة ذكية Ultra", "price": 150},
    "p2": {"name": "سماعات لاسلكية Pro", "price": 90},
    "p3": {"name": "شاحن متنقل 20000mAh", "price": 60},
    "p4": {"name": "غطاء حماية آيفون 15", "price": 15},
    "p5": {"name": "حامل هاتف للسيارة", "price": 25},
    "p6": {"name": "كابل شحن سريع Type-C", "price": 10},
    "p7": {"name": "لوحة مفاتيح ميكانيكية", "price": 120},
    "p8": {"name": "فأرة ألعاب لاسلكية", "price": 45},
    "p9": {"name": "شاشة كمبيوتر 24 بوصة", "price": 200},
    "p10": {"name": "كاميرا ويب 1080p", "price": 55}
}

def init_gsheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        print(f"DB Error: {e}")
        return None

db_sheet = init_gsheets()

def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("المنتجات 🛍️", callback_data="catalog"),
        types.InlineKeyboardButton("سلة المشتريات 🛒", callback_data="cart"),
        types.InlineKeyboardButton("الأسئلة الشائعة ❓", callback_data="faq"),
        types.InlineKeyboardButton("خدمة العملاء 📞", callback_data="support")
    )
    return markup

def get_products_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    for p_id, p_info in PRODUCTS.items():
        btn_text = f"{p_info['name']} - {p_info['price']}$"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"add_{p_id}"))
    markup.add(types.InlineKeyboardButton("رجوع للقائمة الرئيسية 🔙", callback_data="main_menu"))
    return markup

def get_cart_menu(cart_items):
    markup = types.InlineKeyboardMarkup(row_width=1)
    if cart_items:
        for i, item in enumerate(cart_items):
            markup.add(types.InlineKeyboardButton(f"❌ حذف {item['name']}", callback_data=f"del_{i}"))
        markup.add(
            types.InlineKeyboardButton("إتمام الطلب ✅", callback_data="checkout"),
            types.InlineKeyboardButton("إفراغ السلة بالكامل 🗑️", callback_data="clear_cart")
        )
    markup.add(types.InlineKeyboardButton("رجوع للقائمة الرئيسية 🔙", callback_data="main_menu"))
    return markup

def get_admin_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("إرسال رسالة مجمعة (بث)", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("إحصائيات النظام", callback_data="admin_stats")
    )
    return markup

def is_valid_name(name):
    return bool(re.match(r"^[A-Za-z\u0600-\u06FF\s]{3,50}$", name))

def is_valid_phone(phone):
    return bool(re.match(r"^\+?[0-9]{9,15}$", phone))

def ensure_user_state(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {'cart': [], 'name': '', 'phone': ''}

def generate_cart_text(cart_items):
    if not cart_items:
        return "سلتك فارغة حالياً 🛒"
    text = "محتويات سلتك:\n\n"
    total = 0
    for i, item in enumerate(cart_items, 1):
        text += f"{i}. {item['name']} - {item['price']}$\n"
        total += item['price']
    text += f"\nالإجمالي: {total}$"
    return text

@bot.message_handler(commands=['start'])
def handle_start(message):
    ensure_user_state(message.chat.id)
    text = f"أهلاً بك {message.from_user.first_name} في متجرنا الذكي.\nتصفح منتجاتنا بسهولة:"
    bot.reply_to(message, text, reply_markup=get_main_menu())

@bot.message_handler(commands=['admin'])
def handle_admin(message):
    if str(message.chat.id) == str(ADMIN_ID):
        bot.reply_to(message, "مرحباً بك في لوحة تحكم الإدارة:", reply_markup=get_admin_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    data = call.data
    ensure_user_state(chat_id)

    if data == "main_menu":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="القائمة الرئيسية:", reply_markup=get_main_menu())

    elif data == "catalog":
        bot.answer_callback_query(call.id)
        cart = user_data[chat_id]['cart']
        cart_count = len(cart)
        total_price = sum(item['price'] for item in cart)
        text = f"اختر المنتجات لإضافتها إلى سلتك:\n(لديك {cart_count} عناصر في السلة بإجمالي {total_price}$)"
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, reply_markup=get_products_menu())

    elif data.startswith("add_"):
        product_id = data.split("_")[1]
        if product_id in PRODUCTS:
            user_data[chat_id]['cart'].append(PRODUCTS[product_id])
            bot.answer_callback_query(call.id, f"تم إضافة {PRODUCTS[product_id]['name']} للسلة بنجاح!", show_alert=False)
            cart = user_data[chat_id]['cart']
            cart_count = len(cart)
            total_price = sum(item['price'] for item in cart)
            text = f"اختر المنتجات لإضافتها إلى سلتك:\n(لديك {cart_count} عناصر في السلة بإجمالي {total_price}$)"
            bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, reply_markup=get_products_menu())

    elif data == "cart":
        bot.answer_callback_query(call.id)
        cart = user_data[chat_id]['cart']
        text = generate_cart_text(cart)
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, reply_markup=get_cart_menu(cart))

    elif data.startswith("del_"):
        idx = int(data.split("_")[1])
        cart = user_data[chat_id]['cart']
        if 0 <= idx < len(cart):
            removed_item = cart.pop(idx)
            bot.answer_callback_query(call.id, f"تم حذف {removed_item['name']}")
            text = generate_cart_text(cart)
            bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, reply_markup=get_cart_menu(cart))

    elif data == "clear_cart":
        user_data[chat_id]['cart'] = []
        bot.answer_callback_query(call.id, "تم إفراغ السلة")
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="سلتك فارغة حالياً 🛒", reply_markup=get_cart_menu([]))

    elif data == "checkout":
        bot.answer_callback_query(call.id)
        if not user_data[chat_id]['cart']:
            return
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="جاري إتمام الطلب... يرجى المتابعة أدناه.")
        msg = bot.send_message(chat_id, "لإتمام الطلب، يرجى كتابة اسمك الكامل:")
        bot.register_next_step_handler(msg, process_name_step)

    elif data == "faq":
        bot.answer_callback_query(call.id)
        text = "الأسئلة الشائعة:\n- التوصيل: خلال 24 ساعة.\n- الدفع: عند الاستلام."
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, reply_markup=get_main_menu())

    elif data == "support":
        bot.answer_callback_query(call.id)
        text = "للتواصل مع الدعم الفني المباشر:\n@Anas_Sadeq"
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, reply_markup=get_main_menu())

    elif data == "admin_stats":
        if str(chat_id) != str(ADMIN_ID): return
        bot.answer_callback_query(call.id)
        if db_sheet:
            try:
                records = db_sheet.get_all_values()
                total = len(records) - 1 if len(records) > 1 else 0
                bot.send_message(chat_id, f"الطلبات المسجلة: {total}", reply_markup=get_admin_menu())
            except Exception:
                pass

    elif data == "admin_broadcast":
        if str(chat_id) != str(ADMIN_ID): return
        bot.answer_callback_query(call.id)
        msg = bot.send_message(chat_id, "اكتب رسالة البث (أو 'إلغاء'):")
        bot.register_next_step_handler(msg, process_broadcast_step)

def process_broadcast_step(message):
    chat_id = message.chat.id
    text = message.text
    if text.strip() == 'إلغاء':
        bot.send_message(chat_id, "تم الإلغاء.", reply_markup=get_admin_menu())
        return

    bot.send_message(chat_id, "جاري معالجة البث...")
    success, fail = 0, 0
    if db_sheet:
        try:
            records = db_sheet.get_all_values()
            if len(records) > 1:
                uids = {row[2].strip() for row in records[1:] if len(row) >= 3 and row[2].strip()}
                for uid in uids:
                    try:
                        bot.send_message(uid, text)
                        success += 1
                    except Exception:
                        fail += 1
                bot.send_message(chat_id, f"اكتمل.\nنجح: {success}\nفشل: {fail}", reply_markup=get_admin_menu())
            else:
                bot.send_message(chat_id, "لا يوجد عملاء.")
        except Exception:
            pass

def process_name_step(message):
    chat_id = message.chat.id
    name = message.text
    if not is_valid_name(name):
        msg = bot.send_message(chat_id, "الاسم غير صالح، حروف فقط:")
        bot.register_next_step_handler(msg, process_name_step)
        return
    user_data[chat_id]['name'] = name
    msg = bot.send_message(chat_id, "يرجى إدخال رقم هاتفك:")
    bot.register_next_step_handler(msg, process_phone_step)

def process_phone_step(message):
    chat_id = message.chat.id
    phone = message.text
    if not is_valid_phone(phone):
        msg = bot.send_message(chat_id, "رقم غير صالح، أرقام فقط:")
        bot.register_next_step_handler(msg, process_phone_step)
        return

    name = user_data[chat_id]['name']
    cart = user_data[chat_id]['cart']
    order_id = str(uuid.uuid4().hex[:8]).upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    items_str = " + ".join([item['name'] for item in cart])
    total_price = sum([item['price'] for item in cart])
    
    if db_sheet:
        try:
            db_sheet.append_row([order_id, timestamp, str(chat_id), name, phone, items_str, f"{total_price}$"])
        except Exception:
            pass

    summary = (
        "تم تسجيل طلبك بنجاح ✅\n\n"
        f"رقم الطلب: {order_id}\n"
        f"المنتجات: {items_str}\n"
        f"الإجمالي: {total_price}$\n"
        f"الاسم: {name}\n"
        f"الهاتف: {phone}\n\n"
        "سيتواصل معك فريقنا قريباً للتأكيد."
    )
    bot.send_message(chat_id, summary)
    bot.send_message(chat_id, "القائمة الرئيسية:", reply_markup=get_main_menu())
    
    user_data[chat_id]['cart'] = []

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    bot.reply_to(message, "يرجى استخدام القائمة للتنقل:", reply_markup=get_main_menu())

if __name__ == '__main__':
    print("System running with Smart Cart & Catalog...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"System Error: {e}")

