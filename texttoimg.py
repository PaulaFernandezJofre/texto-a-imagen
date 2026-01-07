import streamlit as st
import sqlite3
import os
import io
import base64
from PIL import Image

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config(
    page_title="Texto a Lengua de Señas",
    layout="wide"
)

# =====================================================
# CSS (FRONTEND ANIMADO – AQUÍ VA EL CSS)
# =====================================================
def load_css():
    st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    }

    .title {
        font-size: 3rem;
        text-align: center;
        color: #00ffff;
        text-shadow: 0 0 25px #00ffff;
        animation: pulse 2s infinite alternate;
        margin-bottom: 30px;
    }

    @keyframes pulse {
        from { text-shadow: 0 0 10px #00ffff; }
        to { text-shadow: 0 0 30px #00ffff; }
    }

    .sign {
        animation: fadeInUp 0.6s ease forwards;
        border-radius: 16px;
        box-shadow: 0 0 20px rgba(0,255,255,0.6);
        transition: transform 0.3s ease;
        margin: 5px;
    }

    .sign:hover {
        transform: scale(1.15);
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# =====================================================
# BASE DE DATOS
# =====================================================
def get_connection():
    return sqlite3.connect("database.db", check_same_thread=False)

def create_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT UNIQUE,
            image_data BLOB
        )
    """)
    conn.commit()
    conn.close()

def insert_images_from_folder(folder="signs"):
    conn = get_connection()
    cur = conn.cursor()

    for file in os.listdir(folder):
        if file.lower().endswith(".png"):
            path = os.path.join(folder, file)
            with open(path, "rb") as f:
                data = f.read()

            cur.execute("""
                INSERT OR IGNORE INTO Images (image_name, image_data)
                VALUES (?, ?)
            """, (file.lower(), sqlite3.Binary(data)))

    conn.commit()
    conn.close()

def get_images(names):
    conn = get_connection()
    cur = conn.cursor()

    placeholders = ",".join("?" * len(names))
    cur.execute(
        f"SELECT image_name, image_data FROM Images WHERE image_name IN ({placeholders})",
        names
    )

    result = {name: data for name, data in cur.fetchall()}
    conn.close()
    return result

# =====================================================
# INICIALIZACIÓN
# =====================================================
create_db()

if os.path.exists("signs"):
    insert_images_from_folder("signs")

# =====================================================
# INTERFAZ
# =====================================================
st.markdown(
    '<div class="title">Texto → Lengua de Señas Animada</div>',
    unsafe_allow_html=True
)

st.markdown(
    "💡 **Proyecto inclusivo:** convierte texto en representaciones visuales de lenguaje de señas.",
)

texto = st.text_input(
    "✍️ Ingresa un texto",
    value="hola amigo"
).lower()

# =====================================================
# RENDER DE SEÑAS
# =====================================================
if texto:
    caracteres = [f"{c}.png" for c in texto if c.isalpha()]
    
    if caracteres:
        images = get_images(caracteres)

        cols = st.columns(len(caracteres))

        for i, char in enumerate(caracteres):
            if char in images:
                img = Image.open(io.BytesIO(images[char]))
                img = img.resize((120, 120))

                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode()

                cols[i].markdown(
                    f"""
                    <img class="sign"
                    src="data:image/png;base64,{img_base64}">
                    """,
                    unsafe_allow_html=True
                )
