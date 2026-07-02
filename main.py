from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from datetime import datetime
import sqlite3

# تنظیم فونت پیش‌فرض سیستم برای پشتیبانی از فارسی در اندروید
from kivy.core.text import LabelBase
# در اندروید، فونت DroidSansFallback یا Roboto تمام حروف فارسی را بدون مربع شدن نشان می‌دهد
LabelBase.register(name="Roboto", fn_regular="Roboto-Regular.ttf")

def init_db():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            item_name TEXT,
            model TEXT,
            price REAL,
            date_booked TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_today_jalali():
    today = datetime.now()
    gy, gm, gd = today.year, today.month, today.day
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0):
        for i in range(1, 12): g_d_m[i] += 1
    days = 365 * (gy - 1) + (gy - 1) // 4 - (gy - 1) // 100 + (gy - 1) // 400 + g_d_m[gm - 1] + gd
    jy = int((days - 79) // 365.2425)
    days -= int(jy * 365.2425) + 79
    if days < 0:
        jy -= 1
        days += 366 if ((jy + 1) % 4 == 0) else 365
    if days < 186:
        jm = int(days // 31) + 1
        jd = int(days % 31) + 1
    else:
        jm = int((days - 186) // 30) + 7
        jd = int((days - 186) % 30) + 1
    return f"{jy + 1595}/{jm:02d}/{jd:02d}"

KV = """
BoxLayout:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.07, 0.07, 0.07, 1
        Rectangle:
            pos: self.pos
            size: self.size

    MDTopAppBar:
        title: "سیستم مدیریت سفارشات"
        anchor_title: "center"
        md_bg_color: 0.12, 0.12, 0.12, 1

    ScrollView:
        do_scroll_x: False
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: dp(16)
            spacing: dp(16)

            MDCard:
                orientation: 'vertical'
                padding: dp(12)
                size_hint_y: None
                height: dp(90)
                md_bg_color: 0.15, 0.15, 0.15, 1
                radius: [12, ]
                
                MDTextField:
                    id: search_input
                    hint_text: "🔍 جستجوی نام مشتری..."
                    on_text: app.load_orders(self.text)

            MDCard:
                orientation: 'vertical'
                padding: dp(16)
                size_hint_y: None
                height: dp(380)
                md_bg_color: 0.15, 0.15, 0.15, 1
                radius: [12, ]
                spacing: dp(10)

                MDLabel:
                    text: "ثبت سفارش جدید"
                    theme_text_color: "Custom"
                    text_color: 0.22, 0.7, 1, 1
                    font_style: "Subtitle1"
                    bold: True

                MDTextField:
                    id: c_name
                    hint_text: "نام مشتری"
                MDTextField:
                    id: i_name
                    hint_text: "نام جنس"
                MDTextField:
                    id: m_name
                    hint_text: "مدل"
                MDTextField:
                    id: p_value
                    hint_text: "قیمت"
                MDTextField:
                    id: d_value
                    hint_text: "تاریخ (خالی بماند امروز ثبت می‌شود)"

                MDRaisedButton:
                    text: "ثبت و ذخیره سفارش"
                    size_hint_x: 1
                    md_bg_color: 0.1, 0.6, 0.3, 1
                    on_release: app.add_order()

            MDLabel:
                text: "لیست سفارشات:"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                bold: True
                size_hint_y: None
                height: dp(30)

            BoxLayout:
                id: orders_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(12)

<OrderCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(180)
    padding: dp(12)
    md_bg_color: 0.2, 0.2, 0.2, 1
    radius: [8, ]
    spacing: dp(4)

    BoxLayout:
        orientation: 'horizontal'
        MDLabel:
            text: "👤 مشتری: " + root.customer
            bold: True
        MDLabel:
            text: "📅 " + root.date
            halign: "right"

    MDLabel:
        text: "📦 کالا: " + root.item + " | مدل: " + root.model

    BoxLayout:
        orientation: 'horizontal'
        MDLabel:
            text: "💰 قیمت:"
        MDLabel:
            text: root.price
            text_color: 0.3, 0.85, 0.4, 1
            bold: True

    BoxLayout:
        orientation: 'horizontal'
        spacing: dp(8)
        size_hint_y: None
        height: dp(40)
        
        MDTextField:
            id: new_p
            hint_text: "قیمت جدید"
            size_hint_x: 0.5
        MDRaisedButton:
            text: "بروزرسانی"
            md_bg_color: 0.8, 0.6, 0.1, 1
            on_release: app.update_price(root.order_id, new_p.text)
        MDRaisedButton:
            text: "حذف"
            md_bg_color: 0.8, 0.1, 0.1, 1
            on_release: app.delete_order(root.order_id)
"""

class OrderCard(BoxLayout):
    order_id = StringProperty()
    customer = StringProperty()
    item = StringProperty()
    model = StringProperty()
    price = StringProperty()
    date = StringProperty()

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        init_db()
        return Builder.load_string(KV)

    def on_start(self):
        self.load_orders()

    def load_orders(self, search_query=""):
        self.root.ids.orders_container.clear_widgets()
        conn = sqlite3.connect("orders.db")
        cursor = conn.cursor()
        if search_query:
            cursor.execute("SELECT * FROM orders WHERE customer_name LIKE ?", (f'%{search_query}%',))
        else:
            cursor.execute("SELECT * FROM orders")
        rows = cursor.fetchall()
        for row in rows:
            card = OrderCard(
                order_id=str(row[0]),
                customer=str(row[1]),
                item=str(row[2]),
                model=str(row[3]) if row[3] else "-",
                price=str(row[4]),
                date=str(row[5])
            )
            self.root.ids.orders_container.add_widget(card)
        conn.close()

    def add_order(self):
        ids = self.root.ids
        if ids.c_name.text and ids.i_name.text and ids.p_value.text:
            date_text = ids.d_value.text if ids.d_value.text else get_today_jalali()
            conn = sqlite3.connect("orders.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO orders (customer_name, item_name, model, price, date_booked) VALUES (?, ?, ?, ?, ?)",
                           (ids.c_name.text, ids.i_name.text, ids.m_name.text, float(ids.p_value.text), date_text))
            conn.commit()
            conn.close()
            ids.c_name.text = ""; ids.i_name.text = ""; ids.m_name.text = ""; ids.p_value.text = ""; ids.d_value.text = ""
            self.load_orders()

    def delete_order(self, order_id):
        conn = sqlite3.connect("orders.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE id = ?", (int(order_id),))
        conn.commit()
        conn.close()
        self.load_orders()

    def update_price(self, order_id, new_price):
        if new_price:
            conn = sqlite3.connect("orders.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET price = ? WHERE id = ?", (float(new_price), int(order_id)))
            conn.commit()
            conn.close()
            self.load_orders()

if __name__ == '__main__':
    MainApp().run()
