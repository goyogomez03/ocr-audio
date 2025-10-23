import streamlit as st
import os
import time
import glob
import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator

# Función para convertir texto a voz
def text_to_speech(input_language, output_language, text, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

# Función para eliminar archivos antiguos
def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted ", f)

remove_files(7)

# Estilo visual personalizado
st.markdown("""
    <style>
    body {
        background-color: #f9f6f8;
        font-family: 'Arial', sans-serif;
    }
    .title {
        color: #6a4c9c;
        font-size: 40px;
        font-weight: bold;
    }
    .subheader {
        color: #6a4c9c;
        font-size: 22px;
    }
    .stTextInput input {
        background-color: #ffe6f3;
        color: #6a4c9c;
    }
    .stButton>button {
        background-color: #6a4c9c;
        color: white;
    }
    .stRadio>label, .stSelectbox>label, .stCheckbox>label {
        color: black !important;
    }
    .stRadio div {
        color: black !important;
    }
    .stCheckbox div {
        color: black !important;
    }
    .stSelectbox>div>div>input {
        background-color: #ffe6f3;
        color: #6a4c9c;
    }
    .stFileUploader {
        color: #6a4c9c;
    }
    .stSidebar {
        background-color: #ffe6f3;
        color: #6a4c9c;
    }
    </style>
""", unsafe_allow_html=True)

# Título y subtítulo
st.title("Reconocimiento Óptico de Caracteres🦅", anchor="title")
st.subheader("Elige la fuente de la imágen, esta puede venir de la cámara o cargando un archivo", anchor="subheader")

# Checkbox para usar la cámara
cam_ = st.checkbox("Usar Cámara")

# Cargar imagen desde la cámara o archivo
if cam_ :
    img_file_buffer = st.camera_input("Toma una Foto")
else :
    img_file_buffer = None

# Opciones para filtro de imagen
with st.sidebar:
    st.subheader("Procesamiento para Cámara")
    filtro = st.radio("Filtro para imagen con cámara",('Sí', 'No'), key="filtro", index=1)

# Subir imagen
bg_image = st.file_uploader("Cargar Imagen:", type=["png", "jpg"])
if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='Imagen cargada.', use_column_width=True)
    
    # Guardar la imagen
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())
    
    st.success(f"Imagen guardada como {uploaded_file.name}")
    img_cv = cv2.imread(f'{uploaded_file.name}')
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.write(text)  
    
# Procesar imagen desde la cámara
if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb) 
    st.write(text) 

# Parámetros de traducción
with st.sidebar:
    st.subheader("Parámetros de traducción")
    try:
        os.mkdir("temp")
    except:
        pass
    translator = Translator()

    # Selección de idioma de entrada
    in_lang = st.selectbox("Seleccione el lenguaje de entrada", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    input_language = {"Inglés": "en", "Español": "es", "Bengali": "bn", "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"}[in_lang]

    # Selección de idioma de salida
    out_lang = st.selectbox("Seleccione el idioma de salida", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    output_language = {"Inglés": "en", "Español": "es", "Bengali": "bn", "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"}[out_lang]

    # Selección de acento
    english_accent = st.selectbox("Seleccione el acento", ("Defecto", "India", "Reino Unido", "Estados Unidos", "Canadá", "Australia", "Irlanda", "Sudáfrica"))
    tld = {"Defecto": "com", "India": "co.in", "Reino Unido": "co.uk", "Estados Unidos": "com", "Canadá": "ca", "Australia": "com.au", "Irlanda": "ie", "Sudáfrica": "co.za"}[english_accent]

    display_output_text = st.checkbox("Mostrar texto")

    # Botón para convertir texto a voz
    if st.button("Convertir"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown(f"## Texto de salida:")
            st.write(f" {output_text}")



 
    
    
