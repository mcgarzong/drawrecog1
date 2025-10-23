import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

st.set_page_config(page_title="Canvas Vivo", page_icon="🌿", layout="wide")

st.markdown("""
# 🌿 **Canvas Vivo**
### Donde cada trazo cobra vida
En este lienzo digital, tus líneas son más que formas:  
son señales que despiertan la curiosidad de una mente artificial.  
Dibuja, interpreta y deja que la tecnología lea la emoción detrás del color y la forma.
""")

with st.sidebar:
    st.header("🎨 Propiedades del Canvas")
    st.subheader("Dimensiones del lienzo")
    width = st.slider("Ancho", 200, 1000, 500)
    height = st.slider("Alto", 200, 800, 400)
    st.subheader("Herramienta de dibujo")
    drawing_mode = st.selectbox(
        "Selecciona la herramienta:",
        ("freedraw", "line", "rect", "circle", "transform")
    )
    stroke_width = st.slider("Grosor del trazo", 1, 30, 5)
    stroke_color = st.color_picker("Color del trazo", "#00FF88")
    bg_color = st.color_picker("Color de fondo", "#000000")

st.markdown("🖌️ Dibuja libremente y deja que **Canvas Vivo** interprete lo que nace de tu trazo.")

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=height,
    width=width,
    drawing_mode=drawing_mode,
    key="canvas_vivo",
)

ke = st.text_input("🔑 Ingresa tu clave de OpenAI", type="password")
os.environ["OPENAI_API_KEY"] = ke
api_key = os.environ.get("OPENAI_API_KEY", "")

client = OpenAI(api_key=api_key)

analyze_button = st.button("🌸 Interpretar el dibujo")

if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("🌱 La mente digital observa tu creación..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype("uint8"), "RGBA")
        input_image.save("canvas_vivo_img.png")
        base64_image = encode_image_to_base64("canvas_vivo_img.png")
        prompt_text = (
            "Observa este dibujo como si fuera parte de una obra interactiva. "
            "Interpreta con brevedad qué podría representar o transmitir emocionalmente, en español."
        )
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
            st.success("🌿 Interpretación del Canvas Vivo:")
            st.markdown(result)
        except Exception as e:
            st.error(f"Ocurrió un error durante la interpretación: {e}")
elif not api_key:
    st.warning("🔒 Ingresa tu clave de OpenAI antes de continuar con la interpretación.")
