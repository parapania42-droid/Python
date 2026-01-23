import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time
import random

# Sayfa Yapılandırması
st.set_page_config(page_title="Paramen42 Krallığı", page_icon="🏰")

# Google Sheets Bağlantısı
conn = st.connection("gsheets", type=GSheetsConnection)

# Verileri Çekme Fonksiyonu
def load_data():
    try:
        # ttl="0s" verinin her seferinde güncel gelmesini sağlar
        df = conn.read(ttl="0s")
        df = df.dropna(how="all")
        return df
    except Exception as e:
        # Eğer sayfa boşsa veya hata verirse boş bir şablon döndürür
        return pd.DataFrame(columns=["username", "password", "altin", "odun", "tas"])

# Verileri Kaydetme Fonksiyonu
def save_data(df):
    conn.update(data=df)
    st.cache_data.clear()

# Ana Başlık
st.title("🏰 Paramen42 İmparatorluğu v20.4")

# Veriyi Yükle
df = load_data()
# DataFrame'i hızlı erişim için sözlüğe çeviriyoruz
if not df.empty and "username" in df.columns:
    users = df.set_index("username").to_dict(orient="index")
else:
    users = {}

# Oturum Durumu Kontrolü
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Giriş Yap", "📝 Kayıt Ol"])
    
    with tab1:
        username_input = st.text_input("Kullanıcı Adı", key="login_user")
        password_input = st.text_input("Şifre", type="password", key="login_pass")
        if st.button("Giriş"):
            if username_input in users and str(users[username_input].get("password")) == password_input:
                st.session_state.logged_in = True
                st.session_state.user = username_input
                st.success(f"Hoş geldin Hükümdar {username_input}!")
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")

    with tab2:
        new_user = st.text_input("Yeni Kullanıcı Adı", key="reg_user")
        new_pass = st.text_input("Yeni Şifre", type="password", key="reg_pass")
        if st.button("Kayıt Ol"):
            if new_user and new_user not in users:
                new_row = pd.DataFrame([{
                    "username": new_user,
                    "password": new_pass,
                    "altin": 1000,
                    "odun": 0,
                    "tas": 0
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("Kayıt başarılı! Şimdi giriş yapabilirsin.")
            else:
                st.warning("Bu kullanıcı adı zaten alınmış veya geçersiz!")

# --- OYUN EKRANI ---
else:
    user = st.session_state.user
    # Admin kontrolü
    is_admin = (user == "Paramen42")
    
    menu_list = ["🎒 Envanter", "🏗️ İnşaat", "⚔️ Ordu"]
    if is_admin:
        menu_list.append("🛠️ Admin")
        
    tabs = st.tabs(menu_list)

    # SEKME 1: ENVANTER
    with tabs[0]:
        st.subheader(f"🛡️ {user} Cephaneliği")
        current_data = users.get(user, {"altin": 0, "odun": 0, "tas": 0})
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Altın", f"{current_data.get('altin', 0)}")
        col2.metric("🪵 Odun", f"{current_data.get('odun', 0)}")
        col3.metric("🪨 Taş", f"{current_data.get('tas', 0)}")

    # SEKME 2: İNŞAAT
    with tabs[1]:
        st.info("İnşaat menüsü yakında eklenecek...")

    # SEKME 3: ORDU
    with tabs[2]:
        st.info("Ordu kurma özelliği yakında eklenecek...")

    # SEKME 4: ADMIN PANELİ
    if is_admin:
        with tabs[3]:
            st.header("⚡ Paramen42 Yetkili Paneli")
            if users:
                target_user = st.selectbox("Oyuncu Seç", list(users.keys()))
                target_info = users.get(target_user, {})
                
                gold_val = st.number_input("Altın Miktarı", value=int(target_info.get("altin", 0)))
                
                if st.button("Hükümdar Emriyle Güncelle"):
                    df.loc[df["username"] == target_user, "altin"] = gold_val
                    save_data(df)
                    st.success(f"{target_user} hazinesi güncellendi!")
                    st.rerun()
            else:
                st.warning("Henüz kayıtlı kullanıcı bulunamadı.")

    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.rerun()