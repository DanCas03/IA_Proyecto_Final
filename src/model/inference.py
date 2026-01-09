"""
Módulo de inferencia para predicciones en tiempo real.
Usado por la aplicación Streamlit y para predicciones batch.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from src.config import CATEGORIES, LABEL_NAMES, ID_TO_DISPLAY, MODELS_DIR

# Ruta por defecto del modelo
DEFAULT_MODEL_PATH = MODELS_DIR / "clasificador_textos" / "final"


class TextClassifier:
    """
    Clasificador de textos clásicos.
    Wrapper para facilitar la inferencia.
    """
    
    def __init__(self, model_path: Optional[Path] = None):
        """
        Inicializa el clasificador.
        
        Args:
            model_path: Ruta al modelo entrenado. Si es None, usa la ruta por defecto.
        """
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.model = None
        self.tokenizer = None
        self.device = None
        self._loaded = False
    
    def load(self) -> bool:
        """
        Carga el modelo y tokenizer.
        
        Returns:
            True si la carga fue exitosa, False en caso contrario.
        """
        if self._loaded:
            return True
        
        if not self.model_path.exists():
            return False
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.eval()
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            
            self._loaded = True
            return True
        except Exception as e:
            print(f"Error cargando modelo: {e}")
            return False
    
    def predict(
        self, 
        text: str, 
        return_all_scores: bool = False
    ) -> Dict:
        """
        Clasifica un texto.
        
        Args:
            text: Texto a clasificar.
            return_all_scores: Si True, devuelve probabilidades de todas las clases.
        
        Returns:
            Diccionario con la predicción y confianza.
        """
        if not self._loaded:
            if not self.load():
                raise RuntimeError("No se pudo cargar el modelo")
        
        # Tokenizar
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt"
        )
        encoding = {k: v.to(self.device) for k, v in encoding.items()}
        
        # Inferencia
        with torch.no_grad():
            outputs = self.model(**encoding)
            probs = F.softmax(outputs.logits, dim=-1)
        
        probs = probs.cpu().numpy()[0]
        predicted_id = int(probs.argmax())
        confidence = float(probs[predicted_id])
        
        # Obtener información de la categoría
        category_key = LABEL_NAMES[predicted_id]
        category_info = CATEGORIES[category_key]
        
        result = {
            "categoria": category_key,
            "categoria_display": category_info["display_name"],
            "descripcion": category_info["description"],
            "confianza": confidence,
            "confianza_porcentaje": f"{confidence * 100:.1f}%"
        }
        
        if return_all_scores:
            result["todas_probabilidades"] = {
                CATEGORIES[LABEL_NAMES[i]]["display_name"]: float(p)
                for i, p in enumerate(probs)
            }
        
        return result
    
    def predict_batch(
        self,
        texts: List[str],
        batch_size: int = 16
    ) -> List[Dict]:
        """
        Clasifica múltiples textos en lotes.
        
        Args:
            texts: Lista de textos a clasificar.
            batch_size: Tamaño del lote.
        
        Returns:
            Lista de predicciones.
        """
        if not self._loaded:
            if not self.load():
                raise RuntimeError("No se pudo cargar el modelo")
        
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Tokenizar batch
            encoding = self.tokenizer(
                batch_texts,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            )
            encoding = {k: v.to(self.device) for k, v in encoding.items()}
            
            # Inferencia
            with torch.no_grad():
                outputs = self.model(**encoding)
                probs = F.softmax(outputs.logits, dim=-1)
            
            probs = probs.cpu().numpy()
            
            for prob in probs:
                predicted_id = int(prob.argmax())
                confidence = float(prob[predicted_id])
                category_key = LABEL_NAMES[predicted_id]
                
                results.append({
                    "categoria": category_key,
                    "categoria_display": CATEGORIES[category_key]["display_name"],
                    "confianza": confidence
                })
        
        return results


# Instancia global para reutilización
_classifier_instance: Optional[TextClassifier] = None


def get_classifier() -> TextClassifier:
    """
    Obtiene o crea la instancia global del clasificador.
    
    Returns:
        Instancia del clasificador.
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = TextClassifier()
    return _classifier_instance


def classify_text(text: str, return_all_scores: bool = False) -> Dict:
    """
    Función de conveniencia para clasificar un texto.
    
    Args:
        text: Texto a clasificar.
        return_all_scores: Si True, incluye todas las probabilidades.
    
    Returns:
        Diccionario con la predicción.
    """
    classifier = get_classifier()
    return classifier.predict(text, return_all_scores=return_all_scores)


if __name__ == "__main__":
    # Test rápido
    test_text = "La virtud es el camino hacia la excelencia del alma."
    
    print("Probando clasificador...")
    try:
        result = classify_text(test_text, return_all_scores=True)
        print(f"\nTexto: {test_text}")
        print(f"Categoría: {result['categoria_display']}")
        print(f"Confianza: {result['confianza_porcentaje']}")
        print(f"\nTodas las probabilidades:")
        for cat, prob in result['todas_probabilidades'].items():
            print(f"  {cat}: {prob*100:.1f}%")
    except Exception as e:
        print(f"Error: {e}")
        print("Asegúrate de haber entrenado el modelo primero.")
