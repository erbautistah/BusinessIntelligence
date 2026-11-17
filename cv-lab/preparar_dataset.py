#!/usr/bin/env python3
"""Batch-prepares labeled crops from Android shelf photographs.

Each input photo must have a same-stem JSON label file exported by the shelf generator.
For each photo, the user selects four shelf-grid corners once. The script then
rectifies the complete 4x8 shelf, crops all 32 product regions, and associates
each crop with its product ID from the JSON. It does not train a model.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import cv2

from analizar_anaquel import (
    COLUMNS,
    ROWS,
    CELL_HEIGHT,
    CELL_WIDTH,
    read_image,
    rectify_shelf,
    save_image,
    select_corners,
)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Keep the full illustration while excluding the slot number, product name and price.
CROP_X_RANGE = (0.15, 0.85)
CROP_Y_RANGE = (0.08, 0.73)



def load_labels(json_path: Path) -> tuple[dict[int, dict[str, Any]], dict[str, str]]:
    """Load and validate the 32 slot labels and product names."""
    data = json.loads(json_path.read_text(encoding="utf-8-sig"))
    slots = data.get("slots")
    if not isinstance(slots, list) or len(slots) != ROWS * COLUMNS:
        raise ValueError(f"{json_path.name}: se esperaban exactamente 32 posiciones en 'slots'.")

    product_names: dict[str, str] = {}
    for product in data.get("products", []):
        product_id = product.get("id")
        product_name = product.get("name")
        if product_id and product_name:
            product_names[str(product_id)] = str(product_name)

    by_number: dict[int, dict[str, Any]] = {}
    for slot in slots:
        try:
            number = int(slot["slot"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{json_path.name}: una posición no tiene un número válido.") from exc
        if number < 1 or number > ROWS * COLUMNS or number in by_number:
            raise ValueError(f"{json_path.name}: número de posición duplicado o fuera de rango: {number}.")
        if number not in range(1, ROWS * COLUMNS + 1):
            raise ValueError(f"{json_path.name}: posición fuera de rango: {number}.")
        product_id = slot.get("product_id")
        occupied = bool(slot.get("occupied"))
        if occupied and not product_id:
            raise ValueError(f"{json_path.name}: la posición {number} figura ocupada pero no tiene product_id.")
        if product_id and str(product_id) not in product_names:
            raise ValueError(f"{json_path.name}: product_id desconocido en posición {number}: {product_id}.")
        by_number[number] = slot

    expected = set(range(1, ROWS * COLUMNS + 1))
    if set(by_number) != expected:
        raise ValueError(f"{json_path.name}: faltan posiciones en el rango 1–32.")
    return by_number, product_names


def crop_slot(rectified, slot_number: int):
    """Crop the product illustration area, excluding product name and price."""
    index = slot_number - 1
    row = index // COLUMNS
    column = index % COLUMNS

    x0 = column * CELL_WIDTH
    y0 = row * CELL_HEIGHT

    left = x0 + int(CELL_WIDTH * CROP_X_RANGE[0])
    right = x0 + int(CELL_WIDTH * CROP_X_RANGE[1])
    top = y0 + int(CELL_HEIGHT * CROP_Y_RANGE[0])
    bottom = y0 + int(CELL_HEIGHT * CROP_Y_RANGE[1])

    crop = rectified[top:bottom, left:right]
    if crop.size == 0:
        raise ValueError(f"No se pudo extraer el recorte de la posición {slot_number}.")
    return crop


def output_crop_path(crops_dir: Path, capture_stem: str, slot_number: int, class_id: str) -> Path:
    safe_class = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in class_id)
    return crops_dir / safe_class / f"{capture_stem}_slot_{slot_number:02d}.png"


def process_capture(
    image_path: Path,
    labels_path: Path,
    rectified_dir: Path,
    crops_dir: Path,
    overwrite: bool,
) -> tuple[list[dict[str, Any]], Counter]:
    """Select corners and create the rectified image and 32 labeled crops."""
    labels, product_names = load_labels(labels_path)
    source = read_image(image_path)
    print(f"\nFotografía: {image_path.name} ({source.shape[1]} × {source.shape[0]} px)")
    print("Selecciona las cuatro esquinas exteriores de la cuadrícula 4×8.")
    print("Orden: superior izquierda, superior derecha, inferior derecha, inferior izquierda.")

    corners = select_corners(source)
    rectified = rectify_shelf(source, corners)

    rectified_dir.mkdir(parents=True, exist_ok=True)
    crops_dir.mkdir(parents=True, exist_ok=True)
    rectified_path = rectified_dir / f"{image_path.stem}_rectificada.png"
    if overwrite or not rectified_path.exists():
        save_image(rectified_path, rectified)

    manifest_rows: list[dict[str, Any]] = []
    counts: Counter = Counter()

    for slot_number in range(1, ROWS * COLUMNS + 1):
        slot = labels[slot_number]
        product_id = slot.get("product_id")
        class_id = str(product_id) if product_id else "empty"
        class_name = product_names.get(class_id, "Vacío")
        crop_path = output_crop_path(crops_dir, image_path.stem, slot_number, class_id)
        crop_path.parent.mkdir(parents=True, exist_ok=True)

        if overwrite or not crop_path.exists():
            crop = crop_slot(rectified, slot_number)
            save_image(crop_path, crop)

        counts[class_id] += 1
        manifest_rows.append({
            "capture_id": image_path.stem,
            "source_image": str(image_path),
            "label_json": str(labels_path),
            "slot": slot_number,
            "row": (slot_number - 1) // COLUMNS + 1,
            "column": (slot_number - 1) % COLUMNS + 1,
            "class_id": class_id,
            "class_name": class_name,
            "occupied": bool(product_id),
            "crop_path": str(crop_path),
        })

    print(f"  Rectificada: {rectified_path}")
    print(f"  Recortes generados/registrados: {len(manifest_rows)}")
    print(f"  Ocupados: {sum(v for k, v in counts.items() if k != 'empty')} | Vacíos: {counts.get('empty', 0)}")
    return manifest_rows, counts


def write_manifest(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "capture_id", "source_image", "label_json", "slot", "row", "column",
        "class_id", "class_name", "occupied", "crop_path",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rectifica en lote fotografías Android y genera 32 recortes etiquetados por fotografía."
    )
    parser.add_argument("--entrada", type=Path, default=Path("dataset/images/raw"),
                        help="Carpeta de fotografías originales.")
    parser.add_argument("--etiquetas", type=Path, default=Path("dataset/labels"),
                        help="Carpeta de JSON exportados por el generador.")
    parser.add_argument("--rectificadas", type=Path, default=Path("dataset/images/rectified"),
                        help="Carpeta de imágenes rectificadas.")
    parser.add_argument("--recortes", type=Path, default=Path("dataset/images/crops"),
                        help="Carpeta de recortes organizados por clase.")
    parser.add_argument("--manifiesto", type=Path, default=Path("dataset/manifests/recortes.csv"),
                        help="CSV con la etiqueta y la ruta de cada recorte.")
    parser.add_argument("--sobrescribir", action="store_true",
                        help="Volver a generar archivos aunque ya existan.")
    args = parser.parse_args()

    if not args.entrada.is_dir():
        parser.error(f"No existe la carpeta de fotografías: {args.entrada}")
    if not args.etiquetas.is_dir():
        parser.error(f"No existe la carpeta de etiquetas: {args.etiquetas}")

    images = sorted(
        path for path in args.entrada.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    if not images:
        parser.error(f"No se encontraron JPG, JPEG, PNG o WEBP en {args.entrada}.")

    all_rows: list[dict[str, Any]] = []
    total_counts: Counter = Counter()
    processed = 0
    skipped = 0

    print(f"Fotografías encontradas: {len(images)}")
    print("Se solicitarán cuatro esquinas por fotografía. Los 32 recortes y sus etiquetas se generan automáticamente.")
    print("Pulsa ESC en la ventana de selección para cancelar el lote.")

    for image_path in images:
        label_path = args.etiquetas / f"{image_path.stem}.json"
        if not label_path.is_file():
            print(f"[OMITIDA] No existe JSON correspondiente: {label_path.name}")
            skipped += 1
            continue

        try:
            rows, counts = process_capture(
                image_path=image_path,
                labels_path=label_path,
                rectified_dir=args.rectificadas,
                crops_dir=args.recortes,
                overwrite=args.sobrescribir,
            )
            all_rows.extend(rows)
            total_counts.update(counts)
            processed += 1
        except RuntimeError as exc:
            print(f"\nProceso cancelado: {exc}")
            break
        except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as exc:
            print(f"[ERROR] {image_path.name}: {exc}")
            skipped += 1
        finally:
            cv2.destroyAllWindows()

    if all_rows:
        write_manifest(args.manifiesto, all_rows)

    total_crops = len(all_rows)
    total_occupied = sum(value for key, value in total_counts.items() if key != "empty")
    total_empty = total_counts.get("empty", 0)

    print("\nResumen del lote")
    print(f"  Fotografías procesadas: {processed}")
    print(f"  Fotografías omitidas/con error: {skipped}")
    print(f"  Recortes registrados: {total_crops}")
    print(f"  Recortes de productos: {total_occupied}")
    print(f"  Recortes vacíos: {total_empty}")
    print(f"  Manifiesto: {args.manifiesto.resolve() if all_rows else 'no generado'}")
    print("\nNota: los recortes están etiquetados con el JSON, pero todavía no se ha entrenado ningún modelo.")

    return 0 if processed > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
