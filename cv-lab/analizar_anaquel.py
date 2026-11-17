#!/usr/bin/env python3
"""OpenCV baseline for the 4x8 Tienda inteligente shelf.

Stage 1: perspective rectification + occupied/empty position detection.
This script does not identify product categories and does not train ML.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np

ROWS = 4
COLUMNS = 8
CELL_WIDTH = 200
CELL_HEIGHT = 285
WARP_WIDTH = COLUMNS * CELL_WIDTH
WARP_HEIGHT = ROWS * CELL_HEIGHT

# Central product-icon area; avoids slot number, name and price.
ICON_X_RANGE = (0.15, 0.85)
ICON_Y_RANGE = (0.14, 0.70)
SATURATION_THRESHOLD = 65
VALUE_THRESHOLD = 45
OCCUPANCY_THRESHOLD = 0.08


@dataclass
class CornerPicker:
    scale: float
    points: list[tuple[int, int]]

    def callback(self, event: int, x: int, y: int, flags: int, userdata: object) -> None:
        if event == cv2.EVENT_LBUTTONDOWN and len(self.points) < 4:
            self.points.append((int(round(x / self.scale)), int(round(y / self.scale))))


def read_image(path: Path) -> np.ndarray:
    """Read image paths robustly, including Windows paths with non-ASCII chars."""
    if not path.exists():
        raise FileNotFoundError(f"No se encontró la imagen: {path}")
    encoded = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"No se pudo abrir la imagen: {path}")
    return image


def order_corners(points: Sequence[Sequence[float]]) -> np.ndarray:
    """Return points in TL, TR, BR, BL order."""
    pts = np.asarray(points, dtype=np.float32)
    if pts.shape != (4, 2):
        raise ValueError("Se necesitan exactamente cuatro puntos (esquinas).")
    sums = pts.sum(axis=1)
    diffs = np.diff(pts, axis=1).reshape(-1)
    ordered = np.zeros((4, 2), dtype=np.float32)
    ordered[0] = pts[np.argmin(sums)]
    ordered[2] = pts[np.argmax(sums)]
    ordered[1] = pts[np.argmin(diffs)]
    ordered[3] = pts[np.argmax(diffs)]
    return ordered


def select_corners(image: np.ndarray) -> np.ndarray:
    """Let the user click the four outside corners of the 4x8 cell grid."""
    height, width = image.shape[:2]
    scale = min(1.0, 1250 / width, 820 / height)
    preview = cv2.resize(image, (int(width * scale), int(height * scale)))
    picker = CornerPicker(scale=scale, points=[])
    window = "Seleccionar anaquel - 4 esquinas"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window, picker.callback)

    instructions = [
        "Haz clic en las 4 esquinas EXTERIORES de la cuadrícula 4x8:",
        "1. superior izquierda  2. superior derecha  3. inferior derecha  4. inferior izquierda",
        "ENTER: confirmar con 4 puntos | R: reiniciar | ESC: cancelar",
    ]

    while True:
        canvas = preview.copy()
        for index, (x, y) in enumerate(picker.points):
            px, py = int(round(x * scale)), int(round(y * scale))
            cv2.circle(canvas, (px, py), 8, (0, 255, 255), -1)
            cv2.putText(canvas, str(index + 1), (px + 9, py - 9),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(canvas, str(index + 1), (px + 9, py - 9),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1, cv2.LINE_AA)
        y0 = 25
        for line in instructions:
            cv2.putText(canvas, line, (12, y0), cv2.FONT_HERSHEY_SIMPLEX,
                        0.52, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(canvas, line, (12, y0), cv2.FONT_HERSHEY_SIMPLEX,
                        0.52, (255, 255, 255), 1, cv2.LINE_AA)
            y0 += 24
        cv2.imshow(window, canvas)
        key = cv2.waitKey(30) & 0xFF
        if key in (10, 13) and len(picker.points) == 4:
            break
        if key in (ord("r"), ord("R")):
            picker.points.clear()
        if key == 27:
            cv2.destroyWindow(window)
            raise RuntimeError("Selección cancelada por el usuario.")

    cv2.destroyWindow(window)
    return order_corners(picker.points)


def parse_points(raw: str) -> np.ndarray:
    """Parse four points: 'x,y;x,y;x,y;x,y' (automation/testing only)."""
    try:
        points = [[float(axis) for axis in point.split(",")] for point in raw.split(";")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Formato esperado: x,y;x,y;x,y;x,y") from exc
    if len(points) != 4 or any(len(point) != 2 for point in points):
        raise argparse.ArgumentTypeError("Se deben indicar cuatro pares x,y.")
    return order_corners(points)


def rectify_shelf(image: np.ndarray, corners: np.ndarray) -> np.ndarray:
    destination = np.float32([
        [0, 0],
        [WARP_WIDTH - 1, 0],
        [WARP_WIDTH - 1, WARP_HEIGHT - 1],
        [0, WARP_HEIGHT - 1],
    ])
    matrix = cv2.getPerspectiveTransform(corners, destination)
    return cv2.warpPerspective(image, matrix, (WARP_WIDTH, WARP_HEIGHT),
                               flags=cv2.INTER_CUBIC)


def analyze_occupancy(
    rectified: np.ndarray,
    saturation_threshold: int = SATURATION_THRESHOLD,
    value_threshold: int = VALUE_THRESHOLD,
    occupancy_threshold: float = OCCUPANCY_THRESHOLD,
) -> tuple[list[dict[str, object]], np.ndarray]:
    """Detect colored product illustrations and label cells occupied/empty."""
    if rectified.shape[1] != WARP_WIDTH or rectified.shape[0] != WARP_HEIGHT:
        raise ValueError("La imagen rectificada tiene dimensiones inesperadas.")

    hsv = cv2.cvtColor(rectified, cv2.COLOR_BGR2HSV)
    annotated = rectified.copy()
    results: list[dict[str, object]] = []

    for index in range(ROWS * COLUMNS):
        row = index // COLUMNS
        col = index % COLUMNS
        x0 = col * CELL_WIDTH
        y0 = row * CELL_HEIGHT
        x1 = x0 + CELL_WIDTH
        y1 = y0 + CELL_HEIGHT

        roi_x0 = x0 + int(CELL_WIDTH * ICON_X_RANGE[0])
        roi_x1 = x0 + int(CELL_WIDTH * ICON_X_RANGE[1])
        roi_y0 = y0 + int(CELL_HEIGHT * ICON_Y_RANGE[0])
        roi_y1 = y0 + int(CELL_HEIGHT * ICON_Y_RANGE[1])
        icon_roi = hsv[roi_y0:roi_y1, roi_x0:roi_x1]

        saturation = icon_roi[:, :, 1]
        value = icon_roi[:, :, 2]
        color_mask = (saturation > saturation_threshold) & (value > value_threshold)
        color_ratio = float(np.count_nonzero(color_mask) / color_mask.size)
        occupied = color_ratio >= occupancy_threshold

        slot_number = index + 1
        label = "OCUPADO" if occupied else "VACÍO"
        overlay_label = "OK" if occupied else "VACIO"
        color = (45, 160, 75) if occupied else (0, 145, 230)

        cv2.rectangle(annotated, (x0 + 3, y0 + 3), (x1 - 4, y1 - 4), color, 4)
        text = f"{overlay_label} {color_ratio:.2f}"
        text_x = x1 - 96
        cv2.rectangle(annotated, (text_x - 4, y0 + 6), (x1 - 7, y0 + 31), (248, 248, 240), -1)
        cv2.putText(annotated, text, (text_x, y0 + 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.43, (15, 25, 20), 2, cv2.LINE_AA)
        cv2.putText(annotated, text, (text_x, y0 + 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.43, color, 1, cv2.LINE_AA)

        results.append({
            "slot": slot_number,
            "row": row + 1,
            "column": col + 1,
            "occupied": occupied,
            "status": label,
            "color_ratio": round(color_ratio, 4),
        })

    return results, annotated


def save_image(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    extension = path.suffix.lower() or ".png"
    success, encoded = cv2.imencode(extension, image)
    if not success:
        raise OSError(f"No se pudo codificar la imagen: {path}")
    encoded.tofile(str(path))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["slot", "row", "column", "occupied", "status", "color_ratio"],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rectifica una foto Android del anaquel 4x8 y detecta posiciones ocupadas/vacías."
    )
    parser.add_argument("imagen", type=Path, help="Ruta de la fotografía Android (JPG/PNG).")
    parser.add_argument("--salida", type=Path, default=Path("salida_cv"),
                        help="Carpeta de resultados (por defecto: salida_cv).")
    parser.add_argument("--esquinas", type=parse_points,
                        help="Cuatro esquinas x,y separadas por punto y coma (para pruebas).")
    parser.add_argument("--sin-ventanas", action="store_true",
                        help="No mostrar ventanas de resultado (ejecución automatizada).")
    parser.add_argument("--saturacion-min", type=int, default=SATURATION_THRESHOLD,
                        help=f"Saturación HSV mínima (0-255, valor inicial: {SATURATION_THRESHOLD}).")
    parser.add_argument("--brillo-min", type=int, default=VALUE_THRESHOLD,
                        help=f"Brillo HSV mínimo (0-255, valor inicial: {VALUE_THRESHOLD}).")
    parser.add_argument("--ratio-min", type=float, default=OCCUPANCY_THRESHOLD,
                        help=f"Proporción mínima de píxeles de color (0-1, valor inicial: {OCCUPANCY_THRESHOLD}).")
    args = parser.parse_args()

    if not 0 <= args.saturacion_min <= 255:
        parser.error("--saturacion-min debe estar entre 0 y 255.")
    if not 0 <= args.brillo_min <= 255:
        parser.error("--brillo-min debe estar entre 0 y 255.")
    if not 0 < args.ratio_min <= 1:
        parser.error("--ratio-min debe ser mayor que 0 y menor o igual que 1.")

    try:
        image = read_image(args.imagen)
        print(f"Imagen cargada: {image.shape[1]} x {image.shape[0]} px")

        corners = args.esquinas if args.esquinas is not None else select_corners(image)
        rectified = rectify_shelf(image, corners)
        detections, annotated = analyze_occupancy(
            rectified,
            saturation_threshold=args.saturacion_min,
            value_threshold=args.brillo_min,
            occupancy_threshold=args.ratio_min,
        )

        occupied = sum(1 for item in detections if item["occupied"])
        empty = len(detections) - occupied
        args.salida.mkdir(parents=True, exist_ok=True)

        save_image(args.salida / "anaquel_rectificado.png", rectified)
        save_image(args.salida / "resultado_ocupacion.png", annotated)
        write_csv(args.salida / "detecciones.csv", detections)

        report = {
            "input_image": str(args.imagen),
            "method": "HSV color saturation ratio in a central icon region",
            "scope": "occupancy detection only; no product classification or ML training",
            "grid": {"rows": ROWS, "columns": COLUMNS, "total_slots": ROWS * COLUMNS},
            "thresholds": {
                "saturation_min": args.saturacion_min,
                "value_min": args.brillo_min,
                "occupancy_ratio_min": args.ratio_min,
            },
            "summary": {"occupied_slots": occupied, "empty_slots": empty},
            "detections": detections,
        }
        (args.salida / "resultado.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        print("\nResultado:")
        print(f"  Posiciones ocupadas: {occupied}")
        print(f"  Posiciones vacías:   {empty}")
        print(f"  Total de posiciones: {len(detections)}")
        print("  Parámetros:", f"saturación={args.saturacion_min}, brillo={args.brillo_min}, ratio={args.ratio_min}")
        print(f"\nArchivos guardados en: {args.salida.resolve()}")
        print("  - anaquel_rectificado.png")
        print("  - resultado_ocupacion.png")
        print("  - detecciones.csv")
        print("  - resultado.json")
        print("\nNota: esta etapa detecta ocupación, no identifica cuál producto hay en cada espacio.")

        if not args.sin_ventanas:
            preview_height = int(1200 * annotated.shape[0] / annotated.shape[1])
            preview = cv2.resize(annotated, (1200, preview_height))
            cv2.imshow("OpenCV - ocupacion del anaquel (ESC para cerrar)", preview)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return 0

    except (FileNotFoundError, ValueError, OSError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
