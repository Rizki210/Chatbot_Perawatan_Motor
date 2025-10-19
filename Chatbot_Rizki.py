import os
import sqlite3
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

st.title("🛠️ ChatBot Perawatan Motor 🏍️")


def get_api_key_input():
    """Minta user untuk masukkan google api key."""
    # Inisiasi api key di session state
    if "GOOGLE_API_KEY" not in st.session_state:
        st.session_state["GOOGLE_API_KEY"] = ""

    # Jangan tampilkan input jika sudah ada key yang dimasukkan
    if st.session_state["GOOGLE_API_KEY"]:
        return

    st.write("Masukkan Google API Key")

    # Form untuk masukkan API key
    col1, col2 = st.columns((80, 20))
    with col1:
        api_key = st.text_input("Masukkan API Key", label_visibility="collapsed", type="password")

    with col2:
        is_submit_pressed = st.button("Submit")
        if is_submit_pressed:
            st.session_state["GOOGLE_API_KEY"] = api_key
            os.environ["GOOGLE_API_KEY"] = st.session_state["GOOGLE_API_KEY"]
            st.rerun()

    # Jangan tampilkan apapun (kolom chat) sebelum ada API key yang dimasukkan
    if not st.session_state["GOOGLE_API_KEY"]:
        st.warning("Silakan masukkan API key untuk memulai chat.")
        st.stop()

st.write("Chatbot Perawatan Motor hadir untuk membantu kamu merawat motor dengan lebih mudah. Kamu bisa tanya apa saja seputar oli, ban, rantai, rem, aki, lampu, dll agar motor kamu lebih awet dan selalu dalam kondisi terbaik.")

def init_db():
    """Inisialisasi database SQLite dengan data dummy tentang perawatan motor."""
    if "db_initialized" not in st.session_state:
        conn = sqlite3.connect('motor_maintenance.db')
        cursor = conn.cursor()
        
        # Buat tabel
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_tips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        ''')
        
        # Data dummy
        dummy_data = [
            ('Oli', 'Oli motor: kapan ganti, cara merawat, rekomendasi merek, harga', 'Oli sebaiknya diganti setiap 2000-2500 km atau 2 bulan sekali untuk menjaga performa mesin. Cara merawat: Rutin ganti oli sesuai jadwal, pilih viskositas yang sesuai (misal 10W-40 atau 20W-50), panaskan mesin sebelum jalan, dan hindari overheat. Rekomendasi merek: Shell Advance (cocok untuk harian, harga sekitar Rp44.000 untuk 0.8L), Yamalube (original Yamaha, Rp50.000-Rp70.000), Pertamina Enduro (lokal berkualitas, Rp40.000-Rp60.000), Castrol, Motul. Harga oli umumnya Rp40.000 - Rp100.000 per liter tergantung merek dan jenis (sintetik lebih mahal).'),
            ('Ban', 'Ban motor: cara merawat, rekomendasi merek, harga', 'Cara merawat ban: Periksa tekanan ban rutin (30-35 PSI untuk ban depan/belakang), ganti setiap 10.000-15.000 km atau jika alur <1mm, bersihkan dari kotoran, hindari beban berlebih dan jalan rusak. Rekomendasi merek: IRC (tahan lama, harga Rp200.000-Rp300.000 per pasang), Bridgestone (grip bagus, Rp250.000-Rp400.000), Michelin (premium, Rp300.000-Rp500.000), Corsa, Pirelli. Harga ban tubeless sekitar Rp200.000 - Rp500.000 tergantung ukuran dan merek.'),
            ('Rantai', 'Rantai motor: cara merawat, rekomendasi merek, harga', 'Cara merawat rantai: Bersihkan dan lumasi setiap 500 km menggunakan chain lube, pastikan ketegangan 20-30 mm, periksa keausan gigi gir. Rekomendasi merek: DID (kuat dan awet, harga Rp150.000-Rp300.000), RK (racing quality, Rp200.000-Rp400.000), SSS (lokal bagus, Rp100.000-Rp200.000), Regina, TK Racing. Harga rantai sekitar Rp100.000 - Rp400.000 tergantung panjang dan tipe (O-ring lebih mahal).'),
            ('Rem', 'Rem motor: kapan ganti, cara merawat, rekomendasi merek, harga', 'Ganti kampas rem setiap 10.000-20.000 km atau jika tebal <1 mm. Cara merawat: Bersihkan kampas dari debu, periksa minyak rem (ganti setiap 2 tahun), pastikan jarak cakram dan kampas tepat. Rekomendasi merek: Brembo (high-end, master rem Rp4.000.000), Nissin (reliable, kampas Rp100.000-Rp200.000), KTC (aftermarket bagus, Rp200.000-Rp500.000), OEM seperti Honda atau Yamaha. Harga kampas rem Rp50.000 - Rp200.000, master rem lebih mahal.'),
            ('Aki', 'Aki motor: cara merawat, rekomendasi merek, harga', 'Cara merawat aki: Periksa level elektrolit setiap bulan (untuk aki basah), charge jika motor jarang dipakai, ganti setiap 1-2 tahun, hindari aksesoris berlebih. Rekomendasi merek: GS Astra (tahan lama, harga Rp120.000-Rp250.000), Yuasa (jepang quality, Rp150.000-Rp300.000), Motobatt (gel battery, Rp200.000-Rp400.000), Aspira. Harga aki 12V 3-5Ah sekitar Rp100.000 - Rp300.000.'),
            ('Lampu', 'Lampu motor: cara merawat, rekomendasi merek, harga', 'Cara merawat lampu: Bersihkan lensa secara rutin, periksa kerusakan atau redup, hindari air masuk ke rumah lampu, ganti jika bohlam mati. Rekomendasi merek: Philips Tyto M5 (LED terang, harga Rp30.000-Rp100.000), Osram (fokus bagus, Rp40.000-Rp150.000), RTD (lokal murah, Rp20.000-Rp80.000), Autovision. Harga lampu LED Rp20.000 - Rp200.000 tergantung watt dan tipe.')
        ]
        
        # Insert data
        cursor.execute('SELECT COUNT(*) FROM maintenance_tips')
        if cursor.fetchone()[0] == 0:
            cursor.executemany('INSERT INTO maintenance_tips (topic, question, answer) VALUES (?, ?, ?)', dummy_data)
        
        conn.commit()
        conn.close()
        st.session_state["db_initialized"] = True


def query_db(question):
    """Query database untuk jawaban yang cocok dengan pertanyaan user."""
    conn = sqlite3.connect('motor_maintenance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT answer FROM maintenance_tips WHERE question LIKE ? OR topic LIKE ?', (f'%{question}%', f'%{question}%'))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def load_llm():
    """Dapatkan LLM dari LangChain."""
    if "llm" not in st.session_state:
        st.session_state["llm"] = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    return st.session_state["llm"]


def get_chat_history():
    """Dapatkan chat history."""
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    return st.session_state["chat_history"]


def display_chat_message(message):
    """Display satu chat di kolom chat."""
    if isinstance(message, HumanMessage):
        role = "User"
    elif isinstance(message, AIMessage):
        role = "AI"
    else:
        return
    with st.chat_message(role):
        st.markdown(message.content)


def display_chat_history(chat_history):
    """Display seluruh chat history saat ini di kolom chat."""
    for chat in chat_history:
        display_chat_message(chat)


def user_query_to_llm(llm, chat_history):
    """Minta input query dari user, dan request ke LLM."""
    prompt = st.chat_input("Chat with AI")
    if not prompt:
        st.stop()

    system_content = "You are a friendly and helpful assistant specialized in motorcycle maintenance. Answer in a conversational, relaxed tone, like chatting with a friend. Keep responses short, concise, and to the point. Be flexible and use your knowledge to provide helpful advice even if it's not exactly matching the data—elaborate briefly, add quick tips where it fits. Provide accurate, practical advice on various topics like oil changes, tire care, chain maintenance, brakes, battery, lights, and general servicing. Use standard industry practices and always prioritize safety. If the question is off-topic (not about motorcycle maintenance), politely refuse and redirect back to motorcycle maintenance topics."
    # Tampilkan pesan user
    chat_history.extend([
        SystemMessage(content=system_content),
        HumanMessage(content=prompt),
    ])
    display_chat_message(chat_history[-1])

    # Cek database untuk jawaban langsung jika cocok
    db_answer = query_db(prompt)
    if db_answer:
        # Tambahkan db_answer ke history sebagai base info untuk LLM
        chat_history.insert(-1, SystemMessage(content=f"Use this information as a starting point but feel free to expand or adjust briefly: {db_answer}"))

    # Placeholder spinner saat AI sedang berpikir
    with st.chat_message("AI"):
        with st.spinner("Sedang Berpikir..."):
            response = llm.invoke(chat_history)
            st.markdown(response.content)

    # Simpan dan tampilkan respon AI
    chat_history.append(response)

def main():
    """Bagian utama program."""
    get_api_key_input()
    init_db()
    llm = load_llm()
    chat_history = get_chat_history()
    display_chat_history(chat_history)
    user_query_to_llm(llm, chat_history)


# Jalankan bagian utama.
main()