import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Sayfa Yapılandırması
st.set_page_config(page_title="Paramen42 Krallığı", page_icon="🏰")

# Google Sheets Bağlantısı
conn = st.connection("gsheets", type=GSheetsConnection)

# Verileri Çekme Fonksiyonu
def load_data():
    try:
        df = conn.read(ttl="0s")
        # Boş satırları temizle
        df = df.dropna(how="all")
        return df
    except:
        return pd.DataFrame(columns=["username", "password", "altin", "odun", "tas"])

# Verileri Kaydetme Fonksiyonu
def save_data(df):
    conn.update(data=df)
    st.cache_data.clear()

# Ana Başlık
st.title("🏰 Paramen42 İmparatorluğu v20.4")

# Veriyi Yükle
df = load_data()
users = df.set_index("username").to_dict(orient="index") if not df.empty else {}

# Oturum Durumu Kontrolü
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Giriş Yap", "📝 Kayıt Ol"])
    
    with tab1:
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        if st.button("Giriş"):
            if username in users and str(users[username]["password"]) == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.success(f"Hoş geldin Hükümdar {username}!")
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")

    with tab2:
        new_user = st.text_input("Yeni Kullanıcı Adı")
        new_pass = st.text_input("Yeni Şifre", type="password")
        if st.button("Kayıt Ol"):
            if new_user and new_user not in users:
                new_data = pd.DataFrame([{
                    "username": new_user,
                    "password": new_pass,
                    "altin": 1000,
                    "odun": 0,
                    "tas": 0
                }])
                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)
                st.success("Kayıt başarılı! Şimdi giriş yapabilirsin.")
            else:
                st.warning("Bu kullanıcı adı zaten alınmış veya boş!")

# --- OYUN EKRANI ---
else:
    user = st.session_state.user
    is_admin = (user == "Paramen42")
    
    t_list = ["🎒 Envanter", "🏗️ İnşaat", "⚔️ Ordu", "🛠️ Admin"]
    tabs = st.tabs(t_list if is_admin else t_list[:3])

    # SEKME 1: ENVANTER
    with tabs[0]:
        st.subheader(f"🛡️ {user} Cephaneliği")
        # Veriyi anlık çekmek için tekrar users kullanıyoruz
        current_user_data = users.get(user, {"altin": 0, "odun": 0, "tas": 0})
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Altın", f"{current_user_data.get('altin', 0)}")
        col2.metric("🪵 Odun", f"{current_user_data.get('odun', 0)}")
        col3.metric("🪨 Taş", f"{current_user_data.get('tas', 0)}")

    # SEKME 2: İNŞAAT
    with tabs[1]:
        st.info("İnşaat menüsü yakında eklenecek...")

    # SEKME 3: ORDU
    with tabs[2]:
        st.info("Ordu kurma özelliği yakında eklenecek...")

    # SEKME 4: ADMIN PANELİ (Sadece Sana Özel)
    if is_admin:
        with tabs[3]:
            st.header("⚡ Paramen42 Yetkili Paneli")
            if users:
                target_user = st.selectbox("Oyuncu Seç", list(users.keys()))
                
                # Hata veren yerin güvenli hali:
                target_data = users.get(target_user, {})
                current_gold = target_data.get("altin", 0)
                
                new_gold = st.number_input("Altın Miktarı Ayarla", value=int(current_gold), key="admin_gold")
                
                if st.button("Hükümdar Emriyle Güncelle"):
                    # Veriyi DataFrame üzerinde güncelle
                    df.loc[df["username"] == target_user, "altin"] = new_gold
                    save_data(df)
                    st.success(f"{target_user} altın miktarı {new_gold} olarak güncellendi!")
                    st.rerun()
            else:
                st.warning("Sistemde henüz kayıtlı kullanıcı yok.")

    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.logged_in = False
        st.rerun()