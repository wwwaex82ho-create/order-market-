from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from datetime import datetime
from kivy.core.text import LabelBase
import sqlite3

# ثبت رسمی فایل فونتی که در کنار کد آپلود کردی
LabelBase.register(name="FarsiFont", fn_regular="Vazir.ttf")

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
            rgba: 0.05, 0.05, 0.05, 1
        Rectangle:
            pos: self.pos
            size: self.size

    MDTopAppBar:
        title: "مدیریت سفارشات آفلاین"
        font_name: "FarsiFont"
        anchor_title: "center"
        md_bg_color: 0.1, 0.1, 0.1, 1
        elevation: 4

    ScrollView:
        do_scroll_x: False
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: dp(12)
            spacing: dp(14)

            MDCard:
                orientation: 'vertical'
                padding: [16, 4, 16, 4]
                size_hint_y: None
                height: dp(65)
                md_bg_color: 0.12, 0.12, 0.12, 1
                radius: [10, ]
                elevation: 1
                
                MDTextField:
                    id: search_input
                    hint_text: "🔍 جستجوی نام مشتری..."
                    font_name: "FarsiFont"
                    hint_font_name: "FarsiFont"
                    mode: "line"
                    on_text: app.load_orders(self.text)

            MDCard:
                orientation: 'vertical'
                padding: dp(16)
                size_hint_y: None
                height: dp(390)
                md_bg_color: 0.12, 0.12, 0.12, 1
                radius: [10, ]
                spacing: dp(12)
                elevation: 1

                MDLabel:
                    text: "ثبت سفارش جدید"
                    font_name: "FarsiFont"
                    theme_text_color: "Custom"
                    text_color: 0.22, 0.7, 1, 1
                    font_style: "Button"
                    bold: True

                MDTextField:
                    id: c_name
                    hint_text: "نام مشتری"
                    font_name: "FarsiFont"
                    hint_font_name: "FarsiFont"
                MDTextField:
                    id: i_name
                    hint_text: "نام جنس / کالا"
                    font_name: "FarsiFont"
                    hint_font_name: "FarsiFont"
                MDTextField:
                    id: m_name
                    hint_text: "مدل یا ویژگی"
                    font_name: "FarsiFont"
                    hint_font_name: "FarsiFont"
                MDTextField:
                    id: p_value
                    hint_text: "قیمت (عدد)"
                    font_name: "FarsiFont"
                    hint_font_name: "FarsiFont"
                MDTextField:
                    id: d_value
                    hint_text: "تاریخ (خالی بماند امروز ثبت می‌شود)"
                    font_name: "FarsiFont"
                    hint_font_name: "FarsiFont"

                MDRaisedButton:
                    text: "ثبت و ذخیره در دیتابیس"
                    font_name: "FarsiFont"
                    size_hint_x: 1
                    md_bg_color: 0.11, 0.55, 0.24, 1
                    on_release: app.add_order()

            MDLabel:
                text: "لیست سفارشات ثبت شده:"
                font_name: "FarsiFont"
                theme_text_color: "Custom"
                text_color: 0.7, 0.7, 0.7, 1
                bold: True
                size_hint_y: None
                height: dp(25)

            BoxLayout:
                id: orders_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(10)

<OrderCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(145)
    padding: dp(12)
    md_bg_color: 0.16, 0.16, 0.16, 1
    radius: [8, ]
    spacing: dp(6)

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(24)
        MDLabel:
            text: "👤 " + root.customer
            font_name: "FarsiFont"
            bold: True
        MDLabel:
            text: "📅 " + root.date
            font_name: "FarsiFont"
            halign: "right"
            theme_text_color: "Custom"
            text_color: 0.6, 0.6, 0.6, 1

    MDLabel:
        text: "📦 " + root.item + "  |  مدل: " + root.model
        font_name: "FarsiFont"

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(24)
        MDLabel:
            text: "قیمت:"
            font_name: "FarsiFont"
        MDLabel:
            text: root.price + " تومان"
            font_name: "FarsiFont"
            text_color: 0.29, 0.7, 0.42, 1
            bold: True

    BoxLayout:
        orientation: 'horizontal'
        spacing: dp(6)
        size_hint_y: None
        height: dp(34)
        
        MDTextField:
            id: new_p
            hint_text: "قیمت جدید..."
            font_name: "FarsiFont"
            hint_font_name: "FarsiFont"
            size_hint_x: 0.5
            mode: "line"
        
        MDRaisedButton:
            text: "بروزرسانی"
            font_name: "FarsiFont"
            md_bg_color: 0.75, 0.52, 0.1, 1
            size_hint_x: 0.3
            on_release: app.update_price(root.order_id, new_p.text)
            
        MDRaisedButton:
            text: "حذف"
            font_name: "FarsiFont"
            md_bg_color: 0.75, 0.15, 0.15, 1
            size_hint_x: 0.2
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
