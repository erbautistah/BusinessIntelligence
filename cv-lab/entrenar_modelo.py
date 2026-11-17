#!/usr/bin/env python3
"""Primer clasificador de productos: HOG + SVM, con separación por fotografía."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import numpy as np

BASE = Path(__file__).resolve().parent
DEFAULT_MANIFEST = BASE / "dataset/manifests/recortes.csv"
DEFAULT_OUTPUT = BASE / "salida_ml"

# Los recortes de preparar_dataset.py son aprox. 140 x 185 px (relación 3:4).
HOG_WINDOW = (72, 96)  # ancho, alto
TRAIN_IDS = set(range(1, 10))
VALIDATION_IDS = set(range(10, 13))
TEST_IDS = set(range(13, 16))


def get_split(capture_id: str) -> str:
    match = re.search(r"(\d+)$", capture_id)
    if not match:
        raise ValueError(f"ID de captura no válido: {capture_id!r}; ejemplo: captura_001")
    number = int(match.group(1))
    if number in TRAIN_IDS:
        return "train"
    if number in VALIDATION_IDS:
        return "validation"
    if number in TEST_IDS:
        return "test"
    raise ValueError(
        f"Captura no incluida en la división inicial: {capture_id}. "
        "Se esperan capturas 001-015."
    )


def resolve_path(value: str) -> Path:
    path = Path(value)
    options = [path] if path.is_absolute() else [Path.cwd() / path, BASE / path]
    for option in options:
        if option.is_file():
            return option.resolve()
    raise FileNotFoundError(f"No se encontró el recorte: {value}")


def load_manifest(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"No existe {path}. Ejecuta primero preparar_dataset.py.")
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        required = {"capture_id", "class_id", "crop_path"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"El manifiesto debe contener las columnas: {', '.join(sorted(required))}")
        rows = list(reader)
    if not rows:
        raise ValueError("El manifiesto está vacío.")
    clean = []
    for line, row in enumerate(rows, start=2):
        capture = row["capture_id"].strip()
        label = row["class_id"].strip()
        if not capture or not label or not row["crop_path"].strip():
            raise ValueError(f"Fila {line}: hay campos obligatorios vacíos.")
        clean.append({
            "capture_id": capture,
            "class_id": label,
            "crop_path": resolve_path(row["crop_path"].strip()),
            "slot": row.get("slot", ""),
            "split": get_split(capture),
        })
    return clean


def extract_features(rows: list[dict], hog: cv2.HOGDescriptor) -> np.ndarray:
    result = []
    for index, row in enumerate(rows, start=1):
        data = np.fromfile(str(row["crop_path"]), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"No se pudo leer: {row['crop_path']}")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fixed = cv2.resize(gray, HOG_WINDOW, interpolation=cv2.INTER_AREA)
        descriptor = hog.compute(fixed)
        if descriptor is None:
            raise ValueError(f"No se pudo extraer HOG: {row['crop_path']}")
        result.append(descriptor.reshape(-1))
        if index % 50 == 0 or index == len(rows):
            print(f"  Recortes procesados: {index}/{len(rows)}")
    return np.asarray(result, dtype=np.float32)


def evaluate(y_true: np.ndarray, y_pred: np.ndarray, labels: list[str],
             rows: list[dict], output: Path, split: str) -> dict:
    count = len(labels)
    matrix = np.zeros((count, count), dtype=int)
    for true, predicted in zip(y_true, y_pred):
        matrix[int(true), int(predicted)] += 1

    metrics = []
    f1_present = []
    weighted_f1 = 0.0
    for index, label in enumerate(labels):
        tp = int(matrix[index, index])
        support = int(matrix[index, :].sum())
        predicted_count = int(matrix[:, index].sum())
        precision = tp / predicted_count if predicted_count else 0.0
        recall = tp / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        metrics.append({"class_id": label, "support": support,
                        "predicted_count": predicted_count,
                        "precision": round(precision, 4), "recall": round(recall, 4),
                        "f1": round(f1, 4)})
        if support:
            f1_present.append(f1)
            weighted_f1 += f1 * support

    matrix_file = output / f"matriz_confusion_{split}.csv"
    with matrix_file.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["real \ predicha", *labels])
        for label, values in zip(labels, matrix):
            writer.writerow([label, *values.tolist()])

    metrics_file = output / f"metricas_por_clase_{split}.csv"
    with metrics_file.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(metrics[0]))
        writer.writeheader()
        writer.writerows(metrics)

    errors_file = output / f"errores_{split}.csv"
    with errors_file.open("w", newline="", encoding="utf-8-sig") as file:
        fields = ["capture_id", "slot", "crop_path", "real", "predicha"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for row, true, predicted in zip(rows, y_true, y_pred):
            if true != predicted:
                writer.writerow({"capture_id": row["capture_id"], "slot": row["slot"],
                                 "crop_path": str(row["crop_path"]),
                                 "real": labels[int(true)], "predicha": labels[int(predicted)]})

    total = len(y_true)
    correct = int(np.trace(matrix))
    return {
        "accuracy": round(correct / total, 4) if total else 0.0,
        "macro_f1_present_classes": round(float(np.mean(f1_present)), 4) if f1_present else 0.0,
        "weighted_f1": round(weighted_f1 / total, 4) if total else 0.0,
        "correct": correct, "total": total, "per_class": metrics,
        "files": {"confusion_matrix": matrix_file.name,
                  "per_class_metrics": metrics_file.name, "errors": errors_file.name},
    }


def show_distribution(rows: list[dict], labels: list[str]) -> None:
    counts = defaultdict(Counter)
    captures = defaultdict(set)
    for row in rows:
        counts[row["split"]][row["class_id"]] += 1
        captures[row["split"]].add(row["capture_id"])
    print("\nDistribución por categoría:")
    print(f"{'Clase':<14}{'Train':>8}{'Valid.':>9}{'Prueba':>9}")
    for label in labels:
        print(f"{label:<14}{counts['train'][label]:>8}{counts['validation'][label]:>9}{counts['test'][label]:>9}")
    print("Capturas:", ", ".join(f"{part}={len(captures[part])}" for part in ("train", "validation", "test")))


def main() -> int:
    parser = argparse.ArgumentParser(description="Entrena y evalúa un clasificador HOG + SVM.")
    parser.add_argument("--manifiesto", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--salida", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--c", type=float, default=1.0, help="Parámetro C del SVM lineal (por defecto 1.0).")
    args = parser.parse_args()
    if args.c <= 0:
        parser.error("--c debe ser mayor que cero.")

    try:
        print("Cargando manifiesto...")
        rows = load_manifest(args.manifiesto)
        capture_sets = {part: {r["capture_id"] for r in rows if r["split"] == part}
                        for part in ("train", "validation", "test")}
        expected = {"train": 9, "validation": 3, "test": 3}
        for part, number in expected.items():
            if len(capture_sets[part]) != number:
                raise ValueError(f"Se esperaban {number} capturas en {part}; se encontraron {len(capture_sets[part])}.")

        labels = sorted({row["class_id"] for row in rows})
        show_distribution(rows, labels)
        train_classes = {row["class_id"] for row in rows if row["split"] == "train"}
        missing_train = sorted(set(labels) - train_classes)
        if missing_train:
            raise ValueError("No hay ejemplos de estas clases en entrenamiento: " + ", ".join(missing_train))
        for part in ("validation", "test"):
            present = {row["class_id"] for row in rows if row["split"] == part}
            missing = sorted(set(labels) - present)
            if missing:
                print(f"AVISO: {part} no contiene ejemplos reales de: {', '.join(missing)}")

        args.salida.mkdir(parents=True, exist_ok=True)
        hog = cv2.HOGDescriptor(HOG_WINDOW, (16, 16), (8, 8), (8, 8), 9)
        print("\nExtrayendo características HOG (imagen en escala de grises)...")
        x = extract_features(rows, hog)
        label_to_index = {label: index for index, label in enumerate(labels)}
        y = np.asarray([label_to_index[row["class_id"]] for row in rows], dtype=np.int32)
        splits = np.asarray([row["split"] for row in rows])

        train_mask = splits == "train"
        svm = cv2.ml.SVM_create()
        svm.setType(cv2.ml.SVM_C_SVC)
        svm.setKernel(cv2.ml.SVM_LINEAR)
        svm.setC(float(args.c))
        svm.setTermCriteria((cv2.TERM_CRITERIA_MAX_ITER | cv2.TERM_CRITERIA_EPS, 10000, 1e-6))
        print(f"\nEntrenando SVM con {int(train_mask.sum())} recortes...")
        if not svm.train(x[train_mask], cv2.ml.ROW_SAMPLE, y[train_mask].reshape(-1, 1)):
            raise RuntimeError("OpenCV no pudo entrenar el clasificador SVM.")

        model_file = args.salida / "modelo_hog_svm.yml"
        svm.save(str(model_file))
        model_info = {
            "model": "HOG + SVM C-SVC lineal", "classes": labels,
            "label_to_index": label_to_index,
            "hog": {"window": list(HOG_WINDOW), "block": [16, 16],
                    "stride": [8, 8], "cell": [8, 8], "orientation_bins": 9,
                    "input": "escala de grises"},
            "svm": {"kernel": "LINEAR", "C": float(args.c)},
            "captures": {key: sorted(value) for key, value in capture_sets.items()},
        }
        (args.salida / "modelo_hog_svm.json").write_text(
            json.dumps(model_info, ensure_ascii=False, indent=2), encoding="utf-8")

        evaluations = {}
        for part in ("validation", "test"):
            mask = splits == part
            _, predictions = svm.predict(x[mask])
            true_values = y[mask]
            selected_rows = [row for row, keep in zip(rows, mask) if keep]
            result = evaluate(true_values, predictions.reshape(-1).astype(int),
                              labels, selected_rows, args.salida, part)
            evaluations[part] = result
            print(f"\n{part.upper()}: {result['correct']}/{result['total']} correctos | "
                  f"accuracy={result['accuracy']:.3f} | macro-F1={result['macro_f1_present_classes']:.3f}")

        summary = {
            "description": "Primera línea base HOG + SVM; prueba independiente del entrenamiento.",
            "counts": {"total": len(rows), "train": int(train_mask.sum()),
                       "validation": int((splits == "validation").sum()),
                       "test": int((splits == "test").sum())},
            "classes": labels, "evaluations": evaluations,
            "model_file": model_file.name,
        }
        (args.salida / "resultados.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print("\nResultados guardados en:", args.salida.resolve())
        print("Modelo: modelo_hog_svm.yml | Resumen: resultados.json")
        print("También se generaron matrices de confusión, métricas por clase y CSV de errores.")
        print("La evaluación solo mide estas ilustraciones; no demuestra reconocimiento de empaques reales.")
        return 0
    except (FileNotFoundError, ValueError, OSError, RuntimeError, cv2.error) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
