"""
Pipeline ETL para extracción de datos de Excel con estructuras heterogéneas.
Implementa detección difusa de nombres de hojas y columnas.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd
from fuzzywuzzy import fuzz
from .db import get_collection, clear_collection

# Mapeo de categorías canónicas
CATEGORY_PATTERNS = {
    "arete": ["areté", "arete", "arété", "etiqueta areté", "etiqueta arete"],
    "politica_poder": [
        "política y poder", "politica y poder", "poder y política", 
        "poder y politica", "etiqueta poder", "politica", "política", "poder"
    ],
    "dioses_hombres": [
        "relación entre dioses y hombres", "relacion entre dioses y hombres",
        "dioses y hombres", "dioses", "etiqueta dioses", 
        "relación entre humanos y dioses", "relacion entre humanos y dioses"
    ]
}

# Palabras clave para detectar columnas
COLUMN_KEYWORDS = {
    "canto": ["canto", "número de canto", "numero de canto", "n° canto", "nº canto"],
    "versos": ["verso", "versos", "números de versos", "numeros de versos", "n° verso"],
    "texto": ["cita", "texto", "fragmento", "pasaje"]
}


def normalize_text(text: str) -> str:
    """Normaliza texto para comparación (minúsculas, sin acentos extra)."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    # Normalizar algunos caracteres especiales
    text = text.replace("á", "a").replace("é", "e").replace("í", "i")
    text = text.replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    return text


def fuzzy_match_category(sheet_name: str, threshold: int = 70) -> Optional[str]:
    """
    Encuentra la categoría canónica que mejor coincide con el nombre de la hoja.
    
    Args:
        sheet_name: Nombre de la hoja de Excel
        threshold: Umbral mínimo de similitud (0-100)
    
    Returns:
        Categoría canónica o None si no hay coincidencia
    """
    normalized_name = normalize_text(sheet_name)
    best_match = None
    best_score = 0
    
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            score = fuzz.ratio(normalized_name, normalize_text(pattern))
            if score > best_score and score >= threshold:
                best_score = score
                best_match = category
    
    return best_match


def fuzzy_match_column(column_name: str, threshold: int = 60) -> Optional[str]:
    """
    Encuentra el nombre de columna canónico que mejor coincide.
    
    Args:
        column_name: Nombre de la columna en el Excel
        threshold: Umbral mínimo de similitud
    
    Returns:
        Nombre canónico de columna o None
    """
    normalized_name = normalize_text(str(column_name))
    best_match = None
    best_score = 0
    
    for canonical, keywords in COLUMN_KEYWORDS.items():
        for keyword in keywords:
            score = fuzz.ratio(normalized_name, normalize_text(keyword))
            if score > best_score and score >= threshold:
                best_score = score
                best_match = canonical
    
    return best_match


def find_header_row(df: pd.DataFrame, max_rows: int = 20) -> Tuple[int, Dict[str, str]]:
    """
    Busca la fila que contiene los encabezados de la tabla.
    
    Args:
        df: DataFrame cargado sin encabezados
        max_rows: Máximo de filas a inspeccionar
    
    Returns:
        Tuple (índice_fila, mapeo_columnas)
    """
    for row_idx in range(min(max_rows, len(df))):
        row = df.iloc[row_idx]
        column_mapping = {}
        
        for col_idx, cell_value in enumerate(row):
            if pd.isna(cell_value):
                continue
            
            canonical = fuzzy_match_column(str(cell_value))
            if canonical:
                column_mapping[canonical] = col_idx
        
        # Necesitamos al menos "texto" para considerarlo válido
        if "texto" in column_mapping:
            return row_idx, column_mapping
    
    return -1, {}


def extract_sheet_data(
    df: pd.DataFrame, 
    category: str, 
    source_file: str,
    sheet_name: str
) -> List[Dict]:
    """
    Extrae los datos de una hoja de Excel.
    
    Args:
        df: DataFrame de la hoja
        category: Categoría canónica
        source_file: Nombre del archivo fuente
        sheet_name: Nombre de la hoja original
    
    Returns:
        Lista de documentos para insertar en MongoDB
    """
    # Buscar fila de encabezados
    header_row, column_mapping = find_header_row(df)
    
    if header_row == -1:
        print(f"  ⚠ No se encontraron encabezados válidos en '{sheet_name}'")
        return []
    
    # Crear DataFrame con datos reales (después de encabezados)
    data_df = df.iloc[header_row + 1:].reset_index(drop=True)
    
    documents = []
    for _, row in data_df.iterrows():
        # Extraer texto (obligatorio)
        texto_col = column_mapping.get("texto")
        if texto_col is None:
            continue
            
        texto = row.iloc[texto_col] if texto_col < len(row) else None
        
        # Saltar filas sin texto
        if pd.isna(texto) or str(texto).strip() == "":
            continue
        
        # Extraer campos opcionales
        canto = None
        versos = None
        
        if "canto" in column_mapping:
            canto_col = column_mapping["canto"]
            if canto_col < len(row):
                canto_val = row.iloc[canto_col]
                canto = str(canto_val) if not pd.isna(canto_val) else None
        
        if "versos" in column_mapping:
            versos_col = column_mapping["versos"]
            if versos_col < len(row):
                versos_val = row.iloc[versos_col]
                versos = str(versos_val) if not pd.isna(versos_val) else None
        
        doc = {
            "texto": str(texto).strip(),
            "categoria": category,
            "fuente": source_file,
            "hoja_original": sheet_name,
            "canto": canto,
            "versos": versos
        }
        documents.append(doc)
    
    return documents


def process_excel_file(file_path: Path) -> List[Dict]:
    """
    Procesa un archivo Excel completo con múltiples hojas.
    
    Args:
        file_path: Ruta al archivo Excel
    
    Returns:
        Lista de todos los documentos extraídos
    """
    print(f"\n📄 Procesando: {file_path.name}")
    
    all_documents = []
    
    try:
        # Cargar todas las hojas sin encabezados
        xlsx = pd.ExcelFile(file_path)
        
        for sheet_name in xlsx.sheet_names:
            # Detectar categoría por nombre de hoja
            category = fuzzy_match_category(sheet_name)
            
            if category is None:
                print(f"  ⚠ Hoja '{sheet_name}' no coincide con ninguna categoría - saltando")
                continue
            
            print(f"  📋 Hoja '{sheet_name}' → Categoría: {category}")
            
            # Cargar hoja sin encabezados para detectar offset
            df = pd.read_excel(xlsx, sheet_name=sheet_name, header=None)
            
            # Extraer datos
            documents = extract_sheet_data(df, category, file_path.name, sheet_name)
            all_documents.extend(documents)
            
            print(f"     ✓ {len(documents)} registros extraídos")
    
    except Exception as e:
        print(f"  ✗ Error procesando {file_path.name}: {e}")
    
    return all_documents


def run_etl_pipeline(
    dataset_path: str = "Dataset",
    clear_existing: bool = True
) -> Dict:
    """
    Ejecuta el pipeline ETL completo.
    
    Args:
        dataset_path: Ruta a la carpeta con archivos Excel
        clear_existing: Si True, limpia la colección antes de insertar
    
    Returns:
        Estadísticas de la migración
    """
    print("=" * 60)
    print("🚀 Iniciando Pipeline ETL")
    print("=" * 60)
    
    dataset_dir = Path(dataset_path)
    if not dataset_dir.exists():
        raise FileNotFoundError(f"No se encontró el directorio: {dataset_path}")
    
    # Obtener archivos Excel
    excel_files = list(dataset_dir.glob("*.xlsx"))
    print(f"\n📁 Archivos encontrados: {len(excel_files)}")
    
    # Limpiar colección si se solicita
    if clear_existing:
        deleted = clear_collection("raw_texts")
        print(f"🗑 Colección limpiada: {deleted} documentos eliminados")
    
    # Procesar archivos
    all_documents = []
    stats_by_category = {"arete": 0, "politica_poder": 0, "dioses_hombres": 0}
    stats_by_file = {}
    
    for file_path in excel_files:
        documents = process_excel_file(file_path)
        all_documents.extend(documents)
        stats_by_file[file_path.name] = len(documents)
        
        for doc in documents:
            stats_by_category[doc["categoria"]] += 1
    
    # Insertar en MongoDB
    if all_documents:
        collection = get_collection("raw_texts")
        result = collection.insert_many(all_documents)
        inserted_count = len(result.inserted_ids)
    else:
        inserted_count = 0
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE MIGRACIÓN")
    print("=" * 60)
    print(f"Total de documentos insertados: {inserted_count}")
    print(f"\nPor categoría:")
    for cat, count in stats_by_category.items():
        print(f"  • {cat}: {count}")
    print(f"\nPor archivo:")
    for file, count in stats_by_file.items():
        print(f"  • {file}: {count}")
    
    return {
        "total_inserted": inserted_count,
        "by_category": stats_by_category,
        "by_file": stats_by_file
    }


if __name__ == "__main__":
    # Ejecutar ETL
    stats = run_etl_pipeline()
