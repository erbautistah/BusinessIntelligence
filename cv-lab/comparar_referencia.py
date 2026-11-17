#!/usr/bin/env python3
"""Compare OpenCV occupancy detections with the generator JSON ground truth."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def as_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "si", "sí"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"Valor booleano no reconocido en CSV: {value!r}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compara ocupado/vacío detectado con el JSON de referencia del generador."
    )
    parser.add_argument("--detecciones", required=True, type=Path,
                        help="CSV producido por analizar_anaquel.py")
    parser.add_argument("--referencia", required=True, type=Path,
                        help="JSON exportado por el generador de anaqueles")
    parser.add_argument("--salida", type=Path, default=Path("salida_cv/validacion.json"),
                        help="Ruta del informe JSON")
    args = parser.parse_args()

    if not args.detecciones.is_file():
        parser.error(f"No existe el CSV: {args.detecciones}")
    if not args.referencia.is_file():
        parser.error(f"No existe el JSON de referencia: {args.referencia}")

    with args.detecciones.open("r", newline="", encoding="utf-8-sig") as handle:
        detections = list(csv.DictReader(handle))
    reference_data = json.loads(args.referencia.read_text(encoding="utf-8"))
    expected_slots = reference_data.get("slots", [])

    if len(detections) != 32 or len(expected_slots) != 32:
        parser.error("Se esperaban exactamente 32 posiciones tanto en el CSV como en el JSON.")

    tp = tn = fp = fn = 0
    mismatches = []
    for expected, actual in zip(expected_slots, detections):
        if int(expected["slot"]) != int(actual["slot"]):
            parser.error("El orden o los números de posición no coinciden entre CSV y JSON.")
        truth = bool(expected["occupied"])
        predicted = as_bool(actual["occupied"])
        if truth and predicted:
            tp += 1
        elif not truth and not predicted:
            tn += 1
        elif not truth and predicted:
            fp += 1
            mismatches.append({"slot": int(expected["slot"]), "expected": "VACIO", "detected": "OCUPADO"})
        else:
            fn += 1
            mismatches.append({"slot": int(expected["slot"]), "expected": "OCUPADO", "detected": "VACIO"})

    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0

    report = {
        "reference_file": str(args.referencia),
        "detection_file": str(args.detecciones),
        "scope": "occupancy/empty detection only; not product classification",
        "confusion_matrix": {
            "true_occupied_detected_occupied": tp,
            "true_empty_detected_empty": tn,
            "false_occupied": fp,
            "missed_occupied": fn,
        },
        "metrics": {
            "accuracy": round(accuracy, 4),
            "precision_occupied": round(precision, 4),
            "recall_occupied": round(recall, 4),
            "f1_occupied": round(f1, 4),
        },
        "total_slots": total,
        "mismatches": mismatches,
        "warning": (
            "Una sola fotografía valida únicamente esta muestra; no demuestra generalización "
            "a otros celulares, ángulos o condiciones de luz."
        ),
    }
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Comparación de ocupación")
    print(f"  Aciertos ocupados (TP): {tp}")
    print(f"  Aciertos vacíos   (TN): {tn}")
    print(f"  Falsos ocupados   (FP): {fp}")
    print(f"  Ocupados omitidos (FN): {fn}")
    print(f"  Exactitud: {accuracy:.1%}")
    print(f"  Precisión: {precision:.1%}")
    print(f"  Recall:    {recall:.1%}")
    print(f"  F1:        {f1:.1%}")
    print(f"Informe: {args.salida.resolve()}")
    print("Nota: estas métricas son solo para ocupado/vacío, no para identificar los ocho productos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
