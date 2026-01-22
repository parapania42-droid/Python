import streamlit as st
import json
import os
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Paramen42 İmparatorluğu", page_icon="👑", layout="wide")

# --- VERİ TABANI SİSTEMİ ---
DB_FILE = "empire_data.json"
CHAT_FILE = "chat_logs.json"

def load_data(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return [] if file == CHAT_FILE else {}
    return [] if file == CHAT_FILE else {}

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Verileri yükle
users = load_data(DB_FILE)
chat_messages = load_data(CHAT_FILE)

# --- OTURUM YÖNETİMİ ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- GİRİŞ / KAYIT EKRANI ---
if not st.session_state.logged_in:
    st.title("🏰 Hükümdarlık YNT: v20.1")
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        u = st.text_input("Kullanıcı Adı", key="login_u")
        p = st.text_input("Şifre", type="password", key="login_p")
        if st.button("Giriş Yap"):
            if u in users and users[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else: st.error("Hatalı bilgi!")

    with tab2:
        nu = st.text_input("Yeni Ad", key="reg_u")
        np = st.text_input("Yeni Şifre", type="password", key="reg_p")
        if st.button("Kayıt Ol"):
            if nu not in users and nu != "":
                users[nu] = {"password": np, "altin": 100, "asker": 10, "isçi": 1, "elmas": 0, "market": []}
                save_data(DB_FILE, users)
                st.success("Kayıt Başarılı!")
            else: st.error("Geçersiz ad veya kullanıcı var!")

# --- OYUN ANA EKRANI ---
else:
    user = st.session_state.username
    # --- KRİTİK ADMİN AYARI ---
    # Sadece senin ismin yetkili!
    is_admin = (user == "Paramen42")

    # Sidebar: Bilgiler ve ÇIKIŞ YAP
    st.sidebar.title(f"👑 {user}")
    st.sidebar.metric("💰 Altın", users[user]["altin"])
    st.sidebar.metric("💎 Elmas", users[user].get("elmas", 0))
    st.sidebar.metric("⚔️ Asker", users[user]["asker"])
    
    if st.sidebar.button("🚪 ÇIKIŞ YAP", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # --- ANA SEKMELER ---
    tabs = ["🏗️ Üretim", "🛒 Market", "💬 Sohbet"]
    if is_admin:
        tabs.append("🛠️ Admin Paneli")
    else:
        tabs.append("🏆 Sıralama")
        
    t_list = st.tabs(tabs)

    # SEKME 1: ÜRETİM
    with t_list[0]:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("⛏️ Maden Çalıştır (+20 Altın)"):
                users[user]["altin"] += 20
                save_data(DB_FILE, users); st.rerun()
        with col_b:
            if st.button("🌾 Çiftlik Kur (50 Altın -> +1 İşçi)"):
                if users[user]["altin"] >= 50:
                    users[user]["altin"] -= 50
                    users[user]["isçi"] = users[user].get("isçi", 0) + 1
                    save_data(DB_FILE, users); st.rerun()

    # SEKME 2: MARKET
    with t_list[1]:
        st.subheader("Krallık Mağazası")
        items = {"🛡️ Çelik Zırh": 200, "🐎 Savaş Atı": 500, "🏰 Kale Suru": 1000}
        for item, price in items.items():
            if st.button(f"{item} Satın Al ({price} Altın)"):
                if users[user]["altin"] >= price:
                    users[user]["altin"] -= price
                    if "market" not in users[user]: users[user]["market"] = []
                    users[user]["market"].append(item)
                    save_data(DB_FILE, users); st.success(f"{item} Alındı!")
                else: st.error("Para yetersiz!")

    # SEKME 3: CHAT
    with t_list[2]:
        st.subheader("Global Sohbet")
        msg = st.text_input("Mesajını Yaz...", key="chat_input")
        if st.button("Gönder"):
            if msg:
                chat_messages.append(f"{datetime.now().strftime('%H:%M')} **{user}**: {msg}")
                save_data(CHAT_FILE, chat_messages); st.rerun()
        
        st.divider()
        for m in reversed(chat_messages[-10:]):
            st.write(m)

    # SEKME 4: ADMIN VEYA SIRALAMA
    if is_admin:
        with t_list[3]:
            st.header("⚡ Paramen42 Yetkili Paneli")
            target_user = st.selectbox("Oyuncu Seç", list(users.keys()))
            new_gold = st.number_input("Altın Miktarı Ayarla", value=users[target_user]["altin"])
            if st.button("Hükümdar Emriyle Güncelle"):
                users[target_user]["altin"] = new_gold
                save_data(DB_FILE, users); st.success(f"{target_user} verileri güncellendi!")
            
            if st.button("🚨 TÜM KRALLIKLARI SIFIRLA"):
                save_data(DB_FILE, {}); st.warning("Tüm veriler silindi!")
                st.rerun()
    else:
        with t_list[3]:
            st.subheader("🏆 En Zenginler")
            sorted_users = sorted(users.items(), key=lambda x: x[1]['altin'], reverse=True)
            for i, (name, data) in enumerate(sorted_users[:5]):
                st.write(f"{i+1}. **{name}**: {data['altin']} Altın")