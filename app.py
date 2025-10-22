import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# --- Función para codificar la imagen ---
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# --- Configuración de la página ---
st.set_page_config(page_title="Tablero Inteligente", page_icon="🧠", layout="wide")
st.title("🧠 Tablero para dibujo")

# --- Sidebar con propiedades del tablero ---
with st.sidebar:
    st.header("🎨 Propiedades del Tablero")

    st.subheader("Dimensiones del Tablero")
    width = st.slider("Ancho del tablero", 200, 1000, 500)
    height = st.slider("Alto del tablero", 200, 800, 400)

    st.subheader("Herramienta de Dibujo")
    drawing_mode = st.selectbox(
        "Selecciona la herramienta de dibujo:",
        ("freedraw", "line", "rect", "circle", "transform")
    )

    stroke_width = st.slider("Selecciona el ancho de línea", 1, 30, 5)
    stroke_color = st.color_picker("Color del trazo", "#00FF88")
    bg_color = st.color_picker("Color de fondo", "#000000")

# --- Área principal ---
st.write("✏️ Dibuja el boceto en el panel y presiona el botón para analizarlo")

# --- Canvas de dibujo ---
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=height,
    width=width,
    drawing_mode=drawing_mode,
    key="canvas",
)

# --- Clave de API ---
ke = st.text_input("🔑 Ingresa tu clave de OpenAI", type="password")
os.environ["OPENAI_API_KEY"] = ke
api_key = os.environ.get("OPENAI_API_KEY", "")

# --- Inicializar cliente ---
client = OpenAI(api_key=api_key)

# --- Botón para analizar ---
analyze_button = st.button("✨ Analizar la imagen")

if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("Analizando..."):
        # Convertir imagen del canvas
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype("uint8"), "RGBA")
        input_image.save("img.png")

        # Codificar en base64
        base64_image = encode_image_to_base64("img.png")

        # Prompt
        prompt_text = "Describe brevemente en español lo que ves en la imagen."

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                            },
                        ],
                    }
                ],
                max_tokens=400,
            )

            result = response.choices[0].message.content
            st.success("✅ Resultado del análisis:")
            st.markdown(result)

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

elif not api_key:
    st.warning("⚠️ Por favor ingresa tu clave API antes de analizar.")

