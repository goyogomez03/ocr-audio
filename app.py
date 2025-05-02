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

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Quicksand', sans-serif;
        background-color: #fdf6f0;
    }
    .main {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.05);
    }
    h1, h2, h3, h4 {
        color: #4a4a4a;
    }
    .stButton>button {
        background-color: #ffc0cb;
        color: #4a4a4a;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
        font-weight: 600;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #ffb6c1;
    }
    .stSelectbox>div {
        background-color: #fceef2;
        border-radius: 8px;
    }
    .stCheckbox>div, .stRadio>div {
        background-color: #f9f0ff;
        border-radius: 8px;
        padding: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES ---
def text_to_speech(input_language, output_language, text, tld):
    translator = Translator()
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20].strip().replace(" ", "_")
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

# --- INTERFAZ ---
st.title("🎨 OCR + Traducción con Audio")
st.subheader("Carga una imagen o usa tu cámara para reconocer texto")

remove_files(7)

cam_ = st.checkbox("Usar cámara")
if cam_:
    img_file_buffer = st.camera_input("Toma una Foto")
else:
    img_file_buffer = None

with st.sidebar:
    st.subheader("🌈 Opciones de Procesamiento")
    filtro = st.radio("Aplicar filtro invertido a la imagen?", ('No', 'Sí'))
    st.subheader(":globe_with_meridians: Traducción y Voz")
    try:
        os.mkdir("temp")
    except:
        pass

    in_lang = st.selectbox("Lenguaje de entrada", ("Español", "Inglés", "Bengali", "Koreano", "Mandarin", "Japones"))
    lang_map = {"Español": "es", "Inglés": "en", "Bengali": "bn", "Koreano": "ko", "Mandarin": "zh-cn", "Japones": "ja"}
    input_language = lang_map[in_lang]

    out_lang = st.selectbox("Lenguaje de salida", ("Español", "Inglés", "Bengali", "Koreano", "Mandarin", "Japones"))
    output_language = lang_map[out_lang]

    english_accent = st.selectbox("Acento del inglés (si aplica)", ("Default", "India", "United Kingdom", "United States", "Canada", "Australia", "Ireland", "South Africa"))
    tld_map = {"Default": "com", "India": "co.in", "United Kingdom": "co.uk", "United States": "com", "Canada": "ca", "Australia": "com.au", "Ireland": "ie", "South Africa": "co.za"}
    tld = tld_map[english_accent]

    display_output_text = st.checkbox("Mostrar texto traducido")

# --- PROCESAMIENTO DE IMAGEN ---
text = ""
bg_image = st.file_uploader("Cargar Imagen:", type=["png", "jpg"])
if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='Imagen cargada.', use_column_width=True)
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())
    st.success(f"Imagen guardada como {uploaded_file.name}")
    img_cv = cv2.imread(uploaded_file.name)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.write(text)

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.write(text)

# --- AUDIO ---
if st.button("🎧 Convertir a Audio"):
    result, output_text = text_to_speech(input_language, output_language, text, tld)
    audio_file = open(f"temp/{result}.mp3", "rb")
    audio_bytes = audio_file.read()
    st.markdown(f"## Tu audio:")
    st.audio(audio_bytes, format="audio/mp3", start_time=0)
    if display_output_text:
        st.markdown(f"## Texto traducido:")
        st.write(output_text)




 
    
    
