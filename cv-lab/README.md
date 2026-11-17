# OpenCV: primera etapa de visión por computadora

Esta etapa recibe **solo la fotografía tomada con Android** para procesar el anaquel. El PNG original y el JSON del generador se usan después como referencias de evaluación; no son entradas del reconocimiento.

## Qué hace esta primera versión

1. Carga una fotografía JPG/PNG tomada con Android.
2. Permite seleccionar las cuatro esquinas exteriores de la cuadrícula 4×8.
3. Corrige la perspectiva con una transformación proyectiva.
4. Divide la imagen rectificada en 32 posiciones.
5. Analiza una región central de cada posición en espacio HSV.
6. Clasifica cada posición como **ocupada** o **vacía** mediante reglas de color.
7. Guarda una imagen anotada, un CSV y un JSON con los resultados.

**Importante:** este primer programa no está entrenado. Usa umbrales fijos de saturación, brillo y proporción de color. Por eso puede procesar una sola foto y dar una respuesta inmediata. Todavía no reconoce las ocho categorías de productos ni constituye un modelo de Machine Learning.

## Requisitos e instalación

- Windows 10/11.
- Git Bash (MINGW64).
- Python 3.10 o superior.
- OpenCV y NumPy.

Desde la raíz del repositorio:

~~~bash
cd cv-lab
py -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
~~~

## Dónde guardar las fotografías y etiquetas

Todo se guarda localmente en \`cv-lab/dataset/\`:

- \`images/raw/\`: fotografías originales Android.
- \`images/rectified/\`: fotografías rectificadas.
- \`images/crops/\`: recortes de posiciones.
- \`labels/\`: JSON de referencia exportados por el generador.
- \`manifests/\`: CSV de trazabilidad.

Cada foto debe tener su JSON con el mismo nombre base. Ejemplo:

~~~text
dataset/images/raw/captura_001.jpg
dataset/labels/captura_001.json
~~~

**Por cada captura solo son obligatorios dos archivos:** JPG Android y JSON correspondiente. El PNG generado por la aplicación es opcional como referencia visual; no se usa como entrada para el procesamiento.

Las carpetas de fotos y recortes están excluidas de GitHub. No hagas \`git add\` ni subas las fotografías al repositorio público.

Consulta \`dataset/README.md\` para el plan exacto de 15 capturas, con qué distribución crear en cada número y los pasos para guardar cada pareja de archivos.

## Procesar una fotografía individual

~~~bash
python analizar_anaquel.py "dataset/images/raw/captura_001.jpg"
~~~

Selecciona las cuatro esquinas exteriores de la cuadrícula 4×8, en orden: superior izquierda, superior derecha, inferior derecha, inferior izquierda. Pulsa Enter para confirmar, R para reiniciar o Esc para cancelar.

## Parámetros de las reglas HSV

| Parámetro | Valor inicial | Significado |
|---|---:|---|
| \`--saturacion-min\` | 65 | Saturación HSV mínima. |
| \`--brillo-min\` | 45 | Brillo HSV mínimo. |
| \`--ratio-min\` | 0.08 | Proporción mínima de píxeles de color para considerar ocupada una posición. |

Ejemplo:

~~~bash
python analizar_anaquel.py "dataset/images/raw/captura_001.jpg" --saturacion-min 75 --brillo-min 55 --ratio-min 0.10
~~~

Cambiar estos umbrales es ajustar reglas de procesamiento, no entrenar un modelo ML.

## Comparar detecciones con la referencia

El JSON interviene después del reconocimiento, únicamente para comparar el resultado con la distribución conocida:

~~~bash
python comparar_referencia.py --detecciones salida_cv/detecciones.csv --referencia "dataset/labels/captura_001.json"
~~~

El comparador calcula métricas para ocupado/vacío; no evalúa la clasificación de las ocho categorías.

## Preparar recortes etiquetados de todas las fotografías

Primero guarda las 15 parejas de archivos indicadas en \`dataset/README.md\`. Después, desde \`cv-lab/\`, ejecuta una sola vez:

~~~bash
python preparar_dataset.py
~~~

El programa recorre todas las fotos de \`dataset/images/raw/\`, busca el JSON correspondiente en \`dataset/labels/\`, solicita cuatro esquinas por fotografía, rectifica el anaquel y recorta automáticamente las 32 posiciones. Los recortes se organizan en carpetas por clase y se registra su origen y etiqueta en \`dataset/manifests/recortes.csv\`.

No se ejecuta 15 veces; se hace una sola ejecución por lote. La selección de esquinas sigue siendo manual una vez por foto.

## Uso de los recortes

Los recortes servirán para construir un dataset de ocho categorías y entrenar un clasificador. \`empty/\` se mantiene como posición vacía, no como uno de los ocho productos.

La división de entrenamiento, validación y prueba se hará por captura/configuración: no mezclar recortes de una misma fotografía entre conjuntos. Quince capturas producen hasta 480 recortes, pero no equivalen a 480 fotografías independientes. Después se revisará la cobertura por clase y se decidirá si hacen falta más capturas.

## Siguiente etapa

Después de validar y revisar los recortes, desarrollaremos el entrenamiento de un clasificador clásico (HOG + SVM) y evaluaremos sus resultados con capturas separadas.