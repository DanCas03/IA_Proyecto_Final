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
        "poder y politica", "etiqueta poder", "politica", "política", "poder",
        "etiqueta politica y poder", "etiqueta política y poder"
    ],
    "dioses_hombres": [
        # Variaciones completas
        "relación entre dioses y hombres", "relacion entre dioses y hombres",
        "relación entre humanos y dioses", "relacion entre humanos y dioses",
        "relación entre hombres y dioses", "relacion entre hombres y dioses",
        
        # Variaciones con "entre"
        "relación entre dioses", "relacion entre dioses",
        "relación entre hombres", "relacion entre hombres",
        "relacion entre dioses y hombres", "relacion entre hombres",
        
        # Con "etiqueta"
        "etiqueta dioses", "etiqueta relacion entre dioses",
        "etiqueta relación entre dioses", "etiqueta relacion entre hombres",
        "etiqueta relación entre hombres",
        
        # Abreviaciones comunes
        "relacion entre h y d", "relación entre h y d",
        "relacion h y d", "relación h y d",
        "h y d", "hyd",
        
        # Cortos
        "dioses y hombres", "dioses", "hombres y dioses"
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
    
    # Normalizar acentos
    text = text.replace("á", "a").replace("é", "e").replace("í", "i")
    text = text.replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    
    # Remover puntos de abreviaciones (H. -> H, D. -> D)
    text = re.sub(r'([a-z])\.', r'\1', text)
    
    # Normalizar espacios múltiples a uno solo
    text = re.sub(r'\s+', ' ', text)
    
    # Remover espacios al final
    text = text.strip()
    
    return text


def fuzzy_match_category(sheet_name: str, threshold: int = 65) -> Optional[str]:
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
    
    # Probar con diferentes métodos de fuzzy matching para mejor precisión
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            normalized_pattern = normalize_text(pattern)
            
            # Usar ratio (similitud general)
            score_ratio = fuzz.ratio(normalized_name, normalized_pattern)
            
            # Usar partial_ratio (substring matching)
            score_partial = fuzz.partial_ratio(normalized_name, normalized_pattern)
            
            # Tomar el mejor de los dos
            score = max(score_ratio, score_partial)
            
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


def detect_multi_table_layout(df: pd.DataFrame, max_scan_rows: int = 10) -> Optional[Dict]:
    """
    Detecta si una hoja tiene múltiples tablas en paralelo (como el archivo 4).
    
    Args:
        df: DataFrame de la hoja
        max_scan_rows: Máximo de filas a escanear para detectar categorías
    
    Returns:
        Diccionario con info de las tablas detectadas, o None si no se detecta este formato
    """
    # Buscar fila con títulos de categorías
    for row_idx in range(min(max_scan_rows, len(df))):
        row = df.iloc[row_idx]
        
        # Buscar celdas que coincidan con nombres de categorías
        category_columns = {}
        
        for col_idx, cell_value in enumerate(row):
            if pd.isna(cell_value):
                continue
            
            # Usar threshold más alto para evitar falsos positivos
            category = fuzzy_match_category(str(cell_value), threshold=75)
            if category:
                category_columns[category] = col_idx
        
        # Criterios estrictos para formato multi-tabla:
        # 1. Al menos 3 categorías (las 3 deben estar presentes)
        # 2. Las categorías deben estar espaciadas (al menos 5 columnas entre ellas)
        if len(category_columns) >= 3:
            # Verificar que están suficientemente espaciadas
            cols_sorted = sorted(category_columns.values())
            min_spacing = 5
            
            well_spaced = all(
                cols_sorted[i+1] - cols_sorted[i] >= min_spacing
                for i in range(len(cols_sorted) - 1)
            )
            
            if well_spaced:
                return {
                    "category_row": row_idx,
                    "categories": category_columns
                }
    
    return None


def extract_multi_table_data(
    df: pd.DataFrame,
    source_file: str,
    sheet_name: str
) -> List[Dict]:
    """
    Extrae datos de una hoja con múltiples tablas en paralelo.
    
    Args:
        df: DataFrame de la hoja
        source_file: Nombre del archivo fuente
        sheet_name: Nombre de la hoja original
    
    Returns:
        Lista de documentos de todas las tablas
    """
    # Detectar el layout
    layout_info = detect_multi_table_layout(df)
    if not layout_info:
        return []
    
    category_row = layout_info["category_row"]
    categories = layout_info["categories"]
    
    print(f"     🔍 Detectadas {len(categories)} tablas en paralelo:")
    for cat, col in categories.items():
        print(f"        • {cat} en columna {col}")
    
    all_documents = []
    
    # Procesar cada tabla por separado
    for category, start_col in categories.items():
        # Buscar encabezados (fila después del título de categoría)
        header_found = False
        header_row_idx = -1
        column_mapping = {}
        
        # Buscar en las siguientes 5 filas después del título
        for offset in range(1, 6):
            check_row = category_row + offset
            if check_row >= len(df):
                break
            
            row = df.iloc[check_row]
            temp_mapping = {}
            
            # Buscar en un rango de 7 columnas a partir de start_col
            for col_offset in range(7):
                col_idx = start_col + col_offset
                if col_idx >= len(row):
                    break
                
                cell_value = row.iloc[col_idx]
                if pd.isna(cell_value):
                    continue
                
                canonical = fuzzy_match_column(str(cell_value))
                if canonical:
                    temp_mapping[canonical] = col_idx
            
            # Si encontramos al menos "texto", es una fila de encabezados válida
            if "texto" in temp_mapping:
                header_row_idx = check_row
                column_mapping = temp_mapping
                header_found = True
                break
        
        if not header_found:
            print(f"        ⚠ No se encontraron encabezados para {category}")
            continue
        
        # Extraer datos (después de la fila de encabezados)
        data_start_row = header_row_idx + 1
        count = 0
        
        for row_idx in range(data_start_row, len(df)):
            row = df.iloc[row_idx]
            
            # Extraer texto
            texto_col = column_mapping.get("texto")
            if texto_col is None:
                continue
            
            texto = row.iloc[texto_col] if texto_col < len(row) else None
            
            # Saltar si no hay texto
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
            all_documents.append(doc)
            count += 1
        
        print(f"        ✓ {count} registros de {category}")
    
    return all_documents


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


def process_excel_file(file_path: Path, debug: bool = False) -> List[Dict]:
    """
    Procesa un archivo Excel completo con múltiples hojas.
    
    Args:
        file_path: Ruta al archivo Excel
        debug: Si True, muestra información de debugging
    
    Returns:
        Lista de todos los documentos extraídos
    """
    print(f"\n📄 Procesando: {file_path.name}")
    
    all_documents = []
    
    try:
        # Cargar todas las hojas sin encabezados
        xlsx = pd.ExcelFile(file_path)
        
        for sheet_name in xlsx.sheet_names:
            # Cargar hoja sin encabezados
            df = pd.read_excel(xlsx, sheet_name=sheet_name, header=None)
            
            # Primero, intentar detectar formato multi-tabla
            multi_table_layout = detect_multi_table_layout(df)
            
            if multi_table_layout:
                # Formato multi-tabla detectado (como archivo 4)
                print(f"  📊 Hoja '{sheet_name}' contiene múltiples tablas")
                documents = extract_multi_table_data(df, file_path.name, sheet_name)
                all_documents.extend(documents)
                print(f"     ✓ Total: {len(documents)} registros extraídos")
            else:
                # Formato normal: una categoría por hoja
                category = fuzzy_match_category(sheet_name)
                
                if category is None:
                    if debug:
                        # Mostrar scores para debugging
                        normalized = normalize_text(sheet_name)
                        print(f"  ⚠ Hoja '{sheet_name}' (normalizada: '{normalized}') no coincide")
                        print(f"     Mejores scores:")
                        for cat, patterns in CATEGORY_PATTERNS.items():
                            best = max(fuzz.partial_ratio(normalized, normalize_text(p)) for p in patterns)
                            print(f"       - {cat}: {best}")
                    else:
                        print(f"  ⚠ Hoja '{sheet_name}' no coincide con ninguna categoría - saltando")
                    continue
                
                print(f"  📋 Hoja '{sheet_name}' → Categoría: {category}")
                
                # Extraer datos
                documents = extract_sheet_data(df, category, file_path.name, sheet_name)
                all_documents.extend(documents)
                
                print(f"     ✓ {len(documents)} registros extraídos")
    
    except Exception as e:
        print(f"  ✗ Error procesando {file_path.name}: {e}")
        if debug:
            import traceback
            traceback.print_exc()
    
    return all_documents


def run_etl_pipeline(
    dataset_path: str = "Dataset",
    clear_existing: bool = True,
    debug: bool = False
) -> Dict:
    """
    Ejecuta el pipeline ETL completo.
    
    Args:
        dataset_path: Ruta a la carpeta con archivos Excel
        clear_existing: Si True, limpia la colección antes de insertar
        debug: Si True, muestra información de debugging
    
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
    excel_files = sorted(list(dataset_dir.glob("*.xlsx")))
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
        documents = process_excel_file(file_path, debug=debug)
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
    # Ejecutar ETL con debug activado
    import sys
    debug = "--debug" in sys.argv
    stats = run_etl_pipeline(debug=debug)
