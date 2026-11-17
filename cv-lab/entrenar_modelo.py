#!/usr/bin/env python3
"""Primer clasificador de productos: HOG + SVM, con separación por fotografía."""
from __future__ import annotations

import argparse
import csv
import html
import json
import os
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
        "confusion_matrix": matrix.tolist(),
        "files": {"confusion_matrix": matrix_file.name,
                  "per_class_metrics": metrics_file.name, "errors": errors_file.name},
    }


CLASS_NAMES_ES = {
    "canned": "Conservas",
    "cereal": "Cereal",
    "cookies": "Galletas",
    "detergent": "Detergente",
    "empty": "Vacío",
    "juice": "Jugo",
    "milk": "Leche",
    "soda": "Gaseosa",
    "water": "Agua",
}


def display_class(class_id: str) -> str:
    return CLASS_NAMES_ES.get(class_id, class_id)


def generate_html_report(output: Path, labels: list[str], evaluations: dict,
                         rows: list[dict]) -> Path:
    """Create a self-contained, readable HTML report with class metrics and test errors."""
    test = evaluations["test"]
    validation = evaluations["validation"]
    test_rows = [row for row in rows if row["split"] == "test"]
    matrix = test["confusion_matrix"]
    maximum = max((max(row) for row in matrix), default=1) or 1

    def pct(value: float) -> str:
        return f"{value * 100:.1f}%"

    def metric_table() -> str:
        parts = []
        for metric in test["per_class"]:
            f1 = metric["f1"]
            severity = "good" if f1 >= 0.85 else ("mid" if f1 >= 0.70 else "low")
            parts.append(
                "<tr>"
                f"<td><strong>{html.escape(display_class(metric['class_id']))}</strong>"
                f"<small>{html.escape(metric['class_id'])}</small></td>"
                f"<td>{metric['support']}</td>"
                f"<td>{pct(metric['precision'])}</td>"
                f"<td>{pct(metric['recall'])}</td>"
                f"<td><div class='score {severity}'><span>{pct(f1)}</span>"
                f"<div class='bar'><i style='width:{f1 * 100:.1f}%'></i></div></div></td>"
                "</tr>"
            )
        return "\n".join(parts)

    def confusion_table() -> str:
        header = "".join(f"<th>{html.escape(display_class(label))}</th>" for label in labels)
        body = []
        for i, label in enumerate(labels):
            cells = []
            for j, value in enumerate(matrix[i]):
                strength = value / maximum
                alpha = 0.10 + (0.72 * strength)
                color = "#ffffff" if strength > 0.55 else "#18342a"
                diagonal = " diagonal" if i == j and value else ""
                cells.append(
                    f"<td class='heat{diagonal}' style='--heat:{alpha:.3f};--ink:{color}' "
                    f"title='Real: {html.escape(display_class(label))}; predicha: "
                    f"{html.escape(display_class(labels[j]))}'>{value}</td>"
                )
            row_total = sum(matrix[i])
            body.append(
                f"<tr><th class='row-label'>{html.escape(display_class(label))}</th>"
                + "".join(cells) + f"<td class='total'>{row_total}</td></tr>"
            )
        return (
            "<table class='matrix'><thead><tr><th>Real ↓ / Predicha →</th>"
            + header + "<th>Total</th></tr></thead><tbody>"
            + "".join(body) + "</tbody></table>"
        )

    errors = []
    error_file = output / "errores_test.csv"
    if error_file.is_file():
        with error_file.open(newline="", encoding="utf-8-sig") as file:
            for item in csv.DictReader(file):
                crop_path = Path(item["crop_path"])
                try:
                    relative_image = os.path.relpath(crop_path, output).replace("\\", "/")
                except ValueError:
                    relative_image = ""
                image_tag = (
                    f"<img src='{html.escape(relative_image, quote=True)}' "
                    f"alt='Recorte mal clasificado' loading='lazy'>"
                    if relative_image and crop_path.is_file()
                    else "<span class='no-image'>Imagen no disponible</span>"
                )
                errors.append(
                    "<article class='error-card'>"
                    f"{image_tag}"
                    f"<div><strong>{html.escape(display_class(item['real']))}</strong>"
                    f"<span class='arrow'>→</span>"
                    f"<strong>{html.escape(display_class(item['predicha']))}</strong></div>"
                    f"<small>{html.escape(item['capture_id'])} · posición {html.escape(item['slot'])}</small>"
                    "</article>"
                )

    errors_section = (
        "<div class='error-grid'>" + "".join(errors) + "</div>"
        if errors else "<p class='muted'>No se registraron errores en este conjunto.</p>"
    )

    html_document = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Evaluación del modelo HOG + SVM</title>
<style>
:root {{ color-scheme: light; --ink:#17231d; --muted:#637168; --line:#dce5df; --paper:#f5f8f6; --green:#246b4b; --soft:#e8f2ec; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font:15px/1.5 Inter,Segoe UI,Arial,sans-serif; }}
main {{ width:min(1180px,94vw); margin:34px auto 64px; }}
header {{ margin-bottom:24px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }}
h1 {{ margin:6px 0; font-size:clamp(27px,4vw,38px); line-height:1.15; }}
h2 {{ font-size:21px; margin:0 0 14px; }}
h3 {{ font-size:16px; margin:0 0 8px; }}
p {{ margin:7px 0; }}
.muted, small {{ color:var(--muted); }}
.cards {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin:22px 0; }}
.card, section {{ background:white; border:1px solid var(--line); border-radius:16px; }}
.card {{ padding:17px; }}
.card .label {{ color:var(--muted); font-size:12px; font-weight:700; }}
.card .value {{ font-size:30px; font-weight:800; margin:5px 0 0; letter-spacing:-.03em; }}
.card .sub {{ font-size:12px; color:var(--muted); }}
section {{ padding:22px; margin-top:16px; overflow:hidden; }}
.table-wrap {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; font-size:14px; }}
th,td {{ border-bottom:1px solid var(--line); padding:10px 12px; text-align:right; white-space:nowrap; }}
th {{ background:#f7faf8; color:#526258; font-size:12px; }}
th:first-child,td:first-child {{ text-align:left; }}
td small {{ display:block; font-size:11px; }}
.score {{ display:flex; align-items:center; gap:10px; min-width:130px; justify-content:flex-end; }}
.score span {{ min-width:48px; font-weight:750; }}
.bar {{ width:70px; height:7px; background:#edf1ee; border-radius:9px; overflow:hidden; }}
.bar i {{ display:block; height:100%; background:var(--green); border-radius:9px; }}
.score.mid .bar i {{ background:#bd8b31; }}
.score.low .bar i {{ background:#bb5b4d; }}
.matrix {{ min-width:760px; font-size:13px; }}
.matrix th,.matrix td {{ text-align:center; padding:9px 11px; }}
.matrix .row-label {{ text-align:left; }}
.heat {{ background:rgba(36,107,75,var(--heat)); color:var(--ink); font-weight:700; }}
.heat.diagonal {{ color:var(--ink); outline:2px solid #a5cdb5; outline-offset:-2px; }}
.total {{ color:var(--muted); font-weight:700; }}
.legend {{ display:flex; gap:14px; flex-wrap:wrap; font-size:12px; color:var(--muted); margin-top:10px; }}
.dot {{ display:inline-block; width:10px; height:10px; border-radius:3px; margin-right:5px; background:#a8cdb6; }}
.dot.off {{ background:#e8efea; }}
.error-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:12px; }}
.error-card {{ border:1px solid var(--line); border-radius:12px; overflow:hidden; background:#fff; }}
.error-card img {{ display:block; width:100%; height:130px; object-fit:contain; background:#f2f5f3; padding:8px; }}
.error-card div {{ display:flex; flex-wrap:wrap; align-items:center; gap:6px; padding:9px 10px 2px; font-size:13px; }}
.error-card small {{ display:block; padding:0 10px 10px; }}
.arrow {{ color:#9a5b23; }}
.no-image {{ display:block; padding:40px 5px; color:var(--muted); text-align:center; }}
.two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
.note {{ padding:13px 15px; background:#f1f6f2; border-left:4px solid #7ba98a; border-radius:8px; }}
footer {{ color:var(--muted); font-size:12px; margin-top:18px; }}
@media(max-width:760px) {{ .cards {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .two-col {{ grid-template-columns:1fr; }} section {{ padding:16px; }} }}
</style>
</head>
<body><main>
<header>
<div class="eyebrow">Tienda inteligente · Visión por computadora</div>
<h1>Evaluación del modelo HOG + SVM</h1>
<p class="muted">Informe generado automáticamente a partir del conjunto local de prueba.</p>
</header>
<div class="cards">
<div class="card"><div class="label">Exactitud (accuracy)</div><div class="value">{pct(test['accuracy'])}</div><div class="sub">{test['correct']} de {test['total']} predicciones correctas</div></div>
<div class="card"><div class="label">F1 macro</div><div class="value">{pct(test['macro_f1_present_classes'])}</div><div class="sub">Promedio entre categorías presentes</div></div>
<div class="card"><div class="label">F1 ponderado</div><div class="value">{pct(test['weighted_f1'])}</div><div class="sub">Considera el soporte de cada clase</div></div>
<div class="card"><div class="label">Errores</div><div class="value">{test['total'] - test['correct']}</div><div class="sub">Recortes mal clasificados</div></div>
</div>
<section>
<h2>1. Rendimiento por categoría</h2>
<p class="muted">Resultados del conjunto de prueba. El soporte indica cuántos ejemplos reales había en cada clase.</p>
<div class="table-wrap"><table>
<thead><tr><th>Categoría</th><th>Ejemplos reales</th><th>Precisión</th><th>Recall</th><th>F1</th></tr></thead>
<tbody>{metric_table()}</tbody>
</table></div>
<div class="note"><strong>Cómo leerlo:</strong> precisión responde «cuando el modelo predice esta categoría, ¿cuántas veces acierta?»; recall responde «de los ejemplos reales de esta categoría, ¿cuántos encuentra?»; F1 resume ambas medidas.</div>
</section>
<section>
<h2>2. Matriz de confusión</h2>
<p class="muted">Filas = categoría real. Columnas = categoría predicha. Los valores de la diagonal son aciertos; los valores fuera de ella son confusiones.</p>
<div class="table-wrap">{confusion_table()}</div>
<div class="legend"><span><i class="dot"></i>Diagonal: aciertos</span><span><i class="dot off"></i>Fuera de la diagonal: errores o confusiones</span></div>
</section>
<section>
<h2>3. Recortes mal clasificados</h2>
<p class="muted">Cada tarjeta muestra la etiqueta real → la predicción del modelo. Revisen si el error se relaciona con la forma, el color, la perspectiva, el recorte o la etiqueta de referencia.</p>
{errors_section}
</section>
<section>
<h2>4. Contexto de evaluación</h2>
<div class="two-col">
<div><h3>Separación de los datos</h3><p>Entrenamiento: 9 capturas y 288 recortes.</p><p>Validación: 3 capturas y 96 recortes.</p><p>Prueba: 3 capturas y 96 recortes.</p><p class="muted">Los recortes de una misma fotografía permanecen juntos en un solo conjunto.</p></div>
<div><h3>Referencia de validación</h3><p>Accuracy: <strong>{pct(validation['accuracy'])}</strong></p><p>F1 macro: <strong>{pct(validation['macro_f1_present_classes'])}</strong></p><p class="muted">La validación sirve para orientar ajustes. El conjunto de prueba debe reservarse para la evaluación final.</p></div>
</div>
<div class="note"><strong>Alcance:</strong> el modelo fue entrenado y evaluado con las ilustraciones controladas del generador. Estos resultados no demuestran que reconozca empaques comerciales reales ni diseños nuevos.</div>
</section>
<footer>Generado por entrenar_modelo.py · HOG + SVM lineal · Los CSV se conservan como datos exportables.</footer>
</main></body></html>"""

    report_path = output / "informe_evaluacion.html"
    report_path.write_text(html_document, encoding="utf-8")
    return report_path


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
        report_path = generate_html_report(args.salida, labels, evaluations, rows)
        print("\nResultados guardados en:", args.salida.resolve())
        print("Informe visual:", report_path.resolve())
        print("Modelo: modelo_hog_svm.yml | Resumen: resultados.json")
        print("También se generaron matrices de confusión, métricas por clase y CSV de errores.")
        print("La evaluación solo mide estas ilustraciones; no demuestra reconocimiento de empaques reales.")
        return 0
    except (FileNotFoundError, ValueError, OSError, RuntimeError, cv2.error) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
