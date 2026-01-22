import streamlit as st
import json
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Paramen42 İmparatorluğu", page_icon="🏰", layout="centered")

# --- VERİ TABANI SİSTEMİ ---
DB_FILE = "empire_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Verileri yükle
users = load_data()

# --- OTURUM YÖNETİMİ (Arkadaşının senin hesabına girmemesi için kritik kısım) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.logged_in:
    st.title("🏰 Hükümdarlık YNT: v19")
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        login_user = st.text_input("Kullanıcı Adı", key="l_user")
        login_pass = st.text_input("Şifre", type="password", key="l_pass")
        if st.button("Giriş Yap"):
            if login_user in users and users[login_user]["password"] == login_pass:
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")

    with tab2:
        new_user = st.text_input("Yeni Kullanıcı Adı", key="n_user")
        new_pass = st.text_input("Yeni Şifre", type="password", key="n_pass")
        if st.button("Kayıt Ol"):
            if new_user in users:
                st.warning("Bu kullanıcı adı zaten alınmış!")
            elif new_user == "":
                st.error("Kullanıcı adı boş olamaz!")
            else:
                users[new_user] = {
                    "password": new_pass,
                    "altin": 100,
                    "asker": 10,
                    "seviye": 1
                }
                save_data(users)
                st.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")

# --- OYUN ANA EKRANI ---
else:
    user_name = st.session_state.username
    user_data = users[user_name]

    st.title(f"👑 {user_name} İmparatorluğu")
    st.sidebar.header(f"Hükümdar: {user_name}")
    
    # İstatistikler
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Altın", user_data["altin"])
    col2.metric("⚔️ Asker", user_data["asker"])
    col3.metric("📈 Seviye", user_data["seviye"])

    st.divider()
    
    if st.button("💰 Vergi Topla (+50 Altın)"):
        users[user_name]["altin"] += 50
        save_data(users)
        st.success("Halktan vergiler toplandı!")
        st.rerun()

    if st.button("⚔️ Orduyu Eğit (50 Altın / +5 Asker)"):
        if user_data["altin"] >= 50:
            users[user_name]["altin"] -= 50
            users[user_name]["asker"] += 5
            save_data(users)
            st.success("Yeni yiğitler orduya katıldı!")
            st.rerun()
        else:
            st.error("Yeterli altının yok!")

    if st.sidebar.button("🚪 Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()