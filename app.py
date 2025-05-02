import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator

# Configuración de página
title = "Reconocimiento Óptico de Caracteres"
st.set_page_config(page_title=title, page_icon="📝", layout="centered")

# CSS personalizado para asegurar texto negro sobre fondo blanco
st.markdown("""
    <style>
    body, .css-1cpxqw2, .css-ffhzg2, .css-1d391kg, .css-1v3fvcr {
        color: black !important;
        background-color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

translator = Translator()
text = ""

def text_to_speech(input_language, output_language, text, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    my_file_name = text[0:20] if text else "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    now = time.time()
    n_days = n * 86400
    for f in mp3_files:
        if os.stat(f).st_mtime < now - n_days:
            os.remove(f)
remove_files(7)

# Título principal
st.title(title)

# Selección de entrada
st.subheader("📷 Elige la fuente de la imagen")
cam_ = st.checkbox("Usar cámara")
img_file_buffer = st.camera_input("Toma una foto") if cam_ else st.file_uploader("Cargar imagen:", type=["png", "jpg"])

if img_file_buffer:
    if not cam_:
        with open(img_file_buffer.name, 'wb') as f:
            f.write(img_file_buffer.read())
        st.image(img_file_buffer, caption='Imagen cargada.', use_column_width=True)
        img_cv = cv2.imread(img_file_buffer.name)
    else:
        bytes_data = img_file_buffer.getvalue()
        img_cv = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    filtro = st.radio("¿Aplicar filtro de color negativo?", ('No', 'Sí'))
    if filtro == 'Sí':
        img_cv = cv2.bitwise_not(img_cv)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

    with st.expander("📄 Texto detectado"):
        st.markdown("### Resultado del OCR:")
        st.write(text if text.strip() else "No se detectó texto.")

# Sidebar: Parámetros de traducción
with st.sidebar:
    st.header("🌐 Traducción y Audio")

    try:
        os.mkdir("temp")
    except:
        pass

    input_language = st.selectbox("Idioma de entrada", ["en", "es", "bn", "ko", "zh-cn", "ja"], format_func=lambda x: {"en": "Inglés", "es": "Español", "bn": "Bengalí", "ko": "Coreano", "zh-cn": "Mandarín", "ja": "Japonés"}[x])
    output_language = st.selectbox("Idioma de salida", ["en", "es", "bn", "ko", "zh-cn", "ja"], format_func=lambda x: {"en": "Inglés", "es": "Español", "bn": "Bengalí", "ko": "Coreano", "zh-cn": "Mandarín", "ja": "Japonés"}[x])

    tld_option = st.selectbox("Acento del audio (solo aplica si el idioma de salida es inglés)", {
        "Default": "com",
        "India": "co.in",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canadá": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za",
    }.keys())
    tld = {
        "Default": "com",
        "India": "co.in",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canadá": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za",
    }[tld_option]

    display_output_text = st.checkbox("Mostrar texto traducido")
    if st.button("🔄 Traducir y reproducir audio"):
        if text.strip():
            result, output_text = text_to_speech(input_language, output_language, text, tld)
            audio_file = open(f"temp/{result}.mp3", "rb")
            audio_bytes = audio_file.read()
            st.markdown("## 🔊 Tu audio:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)
            if display_output_text:
                st.markdown("## 📃 Texto traducido:")
                st.write(output_text)
        else:
            st.warning("Por favor carga una imagen válida con texto antes de traducir.")





 
    
    
