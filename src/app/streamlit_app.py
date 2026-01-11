"""
Aplicación Streamlit para clasificación de textos clásicos.
Interfaz de usuario para investigadores de humanidades.
"""

import streamlit as st
from pathlib import Path
import sys
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

# Configuración de página
st.set_page_config(
    page_title="Clasificador de Textos Clásicos",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Crimson+Pro:wght@400;500;600&display=swap');
    
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    h1 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #e8d5b7 !important;
        text-align: center;
        font-size: 3rem !important;
        font-weight: 700 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem !important;
    }
    
    .subtitle {
        font-family: 'Crimson Pro', serif;
        color: #b8a88a;
        text-align: center;
        font-size: 1.2rem;
        font-style: italic;
        margin-bottom: 2rem;
    }
    
    .stTextArea textarea {
        font-family: 'Crimson Pro', serif !important;
        font-size: 1.1rem !important;
        background-color: #0d1b2a !important;
        border: 2px solid #1b263b !important;
        border-radius: 12px !important;
        color: #e0e1dd !important;
        padding: 1rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #c9a959 !important;
        box-shadow: 0 0 15px rgba(201, 169, 89, 0.3) !important;
    }
    
    .stButton > button {
        font-family: 'Cormorant Garamond', serif !important;
        background: linear-gradient(135deg, #c9a959 0%, #a17d32 100%) !important;
        color: #1a1a2e !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        padding: 0.8rem 3rem !important;
        border: none !important;
        border-radius: 30px !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(201, 169, 89, 0.4) !important;
    }
    
    .result-card {
        background: linear-gradient(145deg, #1b263b 0%, #0d1b2a 100%);
        border: 1px solid #415a77;
        border-radius: 16px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    }
    
    .category-label {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .arete { color: #50fa7b; }
    .politica { color: #ff79c6; }
    .dioses { color: #8be9fd; }
    
    .confidence-text {
        font-family: 'Crimson Pro', serif;
        color: #b8a88a;
        text-align: center;
        font-size: 1.1rem;
    }
    
    .progress-container {
        background-color: #1b263b;
        border-radius: 10px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .category-desc {
        font-family: 'Crimson Pro', serif;
        color: #778da9;
        text-align: center;
        font-style: italic;
        margin-top: 1.5rem;
        padding: 1rem;
        border-top: 1px solid #415a77;
    }
    
    .info-section {
        background: rgba(65, 90, 119, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 3rem;
    }
    
    .info-section h3 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #e8d5b7 !important;
    }
    
    .info-section p, .info-section li {
        font-family: 'Crimson Pro', serif;
        color: #b8a88a;
    }
</style>
""", unsafe_allow_html=True)

# Mapeo de categorías
CATEGORY_INFO = {
    "arete": {
        "display": "Areté",
        "class": "arete",
        "description": "Excelencia y virtud moral. Representa la búsqueda de la perfección del carácter y el cumplimiento del propósito humano según la filosofía griega."
    },
    "politica_poder": {
        "display": "Política y Poder",
        "class": "politica",
        "description": "Reflexiones sobre el gobierno, la autoridad y las dinámicas de poder en las sociedades antiguas."
    },
    "dioses_hombres": {
        "display": "Relación Dioses-Humanos",
        "class": "dioses",
        "description": "Interacciones entre lo divino y lo mortal, destino, piedad y la influencia de los dioses en los asuntos humanos."
    }
}

def _get_base_dir() -> Path:
    """Base dir del proyecto (normal) o del bundle (PyInstaller)."""
    meipass = getattr(sys, "_MEIPASS", None)
    if getattr(sys, "frozen", False) and meipass:
        return Path(meipass)
    return Path(__file__).resolve().parents[3]


BASE_DIR = _get_base_dir()
MODEL_PATH = BASE_DIR / "models" / "clasificador_textos" / "final"


@st.cache_resource
def load_model():
    """Carga el modelo entrenado (cacheado para velocidad)."""
    if not MODEL_PATH.exists():
        return None, None, None
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
    return model, tokenizer, device


def predict(text: str, model, tokenizer, device):
    """Realiza predicción sobre un texto."""
    encoding = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=512,
        return_tensors="pt"
    )
    
    encoding = {k: v.to(device) for k, v in encoding.items()}
    
    with torch.no_grad():
        outputs = model(**encoding)
        probs = F.softmax(outputs.logits, dim=-1)
    
    probs = probs.cpu().numpy()[0]
    predicted_class = probs.argmax()
    
    # Mapear a nombres de categoría
    label_map = {0: "arete", 1: "politica_poder", 2: "dioses_hombres"}
    category = label_map[predicted_class]
    confidence = float(probs[predicted_class])
    
    return category, confidence, probs


def main():
    # Título
    st.markdown("<h1>📚 Clasificador de Textos Clásicos</h1>", unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Análisis semántico de literatura antigua mediante Inteligencia Artificial</p>', unsafe_allow_html=True)
    
    # Cargar modelo
    model, tokenizer, device = load_model()
    
    if model is None:
        st.error("⚠️ Modelo no encontrado. Asegúrate de haber entrenado el modelo primero.")
        st.info("Ejecuta el script de entrenamiento: `python -m src.model.train`")
        return
    
    # Área de texto
    st.markdown("### Ingresa el fragmento a analizar")
    text_input = st.text_area(
        label="Texto",
        placeholder="Escribe o pega aquí un fragmento de texto clásico...",
        height=200,
        label_visibility="collapsed"
    )
    
    # Botón de análisis centrado
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("✨ Analizar Texto", use_container_width=True)
    
    # Realizar predicción
    if analyze_button and text_input.strip():
        with st.spinner("Analizando texto..."):
            category, confidence, all_probs = predict(text_input, model, tokenizer, device)
        
        cat_info = CATEGORY_INFO[category]
        
        # Mostrar resultado
        st.markdown(f"""
        <div class="result-card">
            <p class="category-label {cat_info['class']}">{cat_info['display']}</p>
            <p class="confidence-text">Confianza: {confidence*100:.1f}%</p>
            <div class="progress-container">
                <div style="background: linear-gradient(90deg, {'#50fa7b' if category == 'arete' else '#ff79c6' if category == 'politica_poder' else '#8be9fd'}, transparent); 
                            width: {confidence*100}%; height: 8px;"></div>
            </div>
            <p class="category-desc">"{cat_info['description']}"</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar todas las probabilidades
        st.markdown("#### Distribución de probabilidades")
        
        for idx, (cat_key, prob) in enumerate(zip(["arete", "politica_poder", "dioses_hombres"], all_probs)):
            cat = CATEGORY_INFO[cat_key]
            color = "#50fa7b" if cat_key == "arete" else "#ff79c6" if cat_key == "politica_poder" else "#8be9fd"
            st.markdown(f"""
            <div style="margin: 0.5rem 0;">
                <span style="color: {color}; font-family: 'Crimson Pro', serif;">{cat['display']}</span>
                <span style="color: #778da9; float: right;">{prob*100:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
            st.progress(float(prob))
    
    elif analyze_button:
        st.warning("Por favor, ingresa un texto para analizar.")
    
    # Información adicional
    st.markdown("""
    <div class="info-section">
        <h3>📖 Sobre las Categorías</h3>
        <ul>
            <li><strong style="color: #50fa7b;">Areté:</strong> Virtud, excelencia moral y el ideal de perfección humana.</li>
            <li><strong style="color: #ff79c6;">Política y Poder:</strong> Gobierno, autoridad y estructuras de poder.</li>
            <li><strong style="color: #8be9fd;">Dioses y Humanos:</strong> La relación entre lo divino y lo mortal.</li>
        </ul>
        <p style="margin-top: 1rem; font-size: 0.9rem;">
            Este sistema utiliza un modelo de lenguaje BERT entrenado específicamente 
            para clasificar fragmentos de textos clásicos griegos y latinos.
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
