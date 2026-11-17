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

## Requisitos

- Windows 10/11.
- Git Bash (MINGW64) o una terminal Bash compatible.
- Python 3.10 o superior.
- OpenCV y NumPy instalados desde requirements.txt.

## Instalación en Git Bash

Desde la raíz del repositorio:

~~~bash
cd cv-lab
py -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
~~~

Verifica la instalación:

~~~bash
python -c "import cv2; print(cv2.__version__)"
~~~

## Dónde guardar las fotografías

La carpeta del conjunto de datos está en cv-lab/dataset/:

- images/raw/: fotografías originales de Android. No editarlas.
- images/rectified/: imágenes rectificadas que generará OpenCV.
- images/crops/: recortes individuales de las posiciones/productos para la futura clasificación.
- labels/: JSON exportado por el generador que describe la distribución real del anaquel.

Cada fotografía debe tener un JSON con el mismo nombre base:

~~~text
dataset/
├── images/
│   ├── raw/
│   │   ├── captura_001.jpg
│   │   └── captura_002.jpg
│   ├── rectified/
│   └── crops/
└── labels/
    ├── captura_001.json
    └── captura_002.json
~~~

Por ejemplo, captura_001.jpg debe corresponder a captura_001.json. Si se fotografía varias veces una misma distribución, se puede duplicar su JSON de referencia con el nombre de cada fotografía.

Las carpetas locales de imágenes no se suben automáticamente a GitHub: se excluyen para evitar que el repositorio crezca con fotografías pesadas. Cada grupo conservará su conjunto de datos en su laptop.

Consulta dataset/README.md para las reglas de captura y organización.

## Ejecutar una fotografía

Copia una fotografía Android en images/raw/, por ejemplo captura_001.jpg.

Desde cv-lab/, con el entorno virtual activo:

~~~bash
python analizar_anaquel.py "dataset/images/raw/captura_001.jpg"
~~~

Se abrirá una ventana para seleccionar cuatro esquinas. Haz clic en los límites exteriores de la cuadrícula 4×8, no en el marco exterior del anaquel:

1. Superior izquierda.
2. Superior derecha.
3. Inferior derecha.
4. Inferior izquierda.

Pulsa **Enter** para confirmar. Usa **R** para reiniciar o **Esc** para cancelar.

Por defecto, los resultados se guardan en salida_cv/. Para guardar la imagen rectificada en la carpeta del dataset:

~~~bash
python analizar_anaquel.py "dataset/images/raw/captura_001.jpg" --salida "dataset/images/rectified/captura_001"
~~~

## Probar y modificar los parámetros

El algoritmo actual utiliza tres umbrales configurables desde la terminal:

| Parámetro | Valor inicial | Significado |
|---|---:|---|
| --saturacion-min | 65 | Saturación HSV mínima de un píxel. |
| --brillo-min | 45 | Brillo HSV mínimo de un píxel. |
| --ratio-min | 0.08 | Proporción mínima de píxeles que deben superar los umbrales para considerar ocupada la posición. |

Ejemplo para cambiar los parámetros:

~~~bash
python analizar_anaquel.py "dataset/images/raw/captura_001.jpg" --saturacion-min 75 --brillo-min 55 --ratio-min 0.10
~~~

Los valores son puntos de partida, no valores universales. Conviene ejecutar la misma fotografía con distintos parámetros y después repetir la comparación con otras fotografías.

**Ajustar estos umbrales no es entrenar un modelo ML.** Es experimentar con reglas de procesamiento de imágenes.

## Archivos de salida

Se crea la carpeta indicada mediante --salida:

- anaquel_rectificado.png: cuadrícula transformada a una vista frontal.
- resultado_ocupacion.png: posiciones marcadas en verde (ocupadas) y naranja (vacías).
- detecciones.csv: una fila por posición, con estado y proporción de píxeles de color.
- resultado.json: método, parámetros utilizados y resultados.

## Comparar contra la respuesta esperada

El JSON se utiliza solo después de la detección. Compara el CSV producido por OpenCV con el JSON correspondiente a esa fotografía:

~~~bash
python comparar_referencia.py --detecciones salida_cv/detecciones.csv --referencia "dataset/labels/captura_001.json"
~~~

El comparador calcula exactitud, precisión, recall y F1 para ocupado/vacío. No evalúa la clasificación de las ocho categorías.

Si guardaste los resultados en otra ubicación, ajusta la ruta de --detecciones.

## Por qué necesitamos varias fotografías

Una foto basta para ejecutar las reglas actuales, pero **no basta para demostrar robustez ni para entrenar un clasificador de productos**.

Se recopilarán fotografías con variaciones controladas:
- Distintas distribuciones de productos generadas por el simulador.
- Diferentes celulares Android, cuando sea posible.
- Distancia y ángulo ligeramente distintos.
- Diferentes condiciones de brillo de pantalla y luz ambiente.

Cada foto debe tener su JSON de referencia emparejado por nombre. No se debe usar la misma imagen o una copia casi idéntica simultáneamente para entrenamiento y prueba.

Se mantendrán separados:
- **Entrenamiento:** imágenes etiquetadas con las que se ajustará el clasificador.
- **Validación:** imágenes distintas para comparar configuraciones y modelos.
- **Prueba final:** imágenes que no se utilizarán durante el entrenamiento ni los ajustes.

No se fija todavía una cantidad final de fotografías: primero construiremos el flujo de recorte y etiquetado, y luego estimaremos el volumen necesario para las ocho clases.

## Siguiente etapa

Después de recoger varias fotografías, se desarrollará el flujo para:
1. Rectificar cada foto.
2. Recortar las 32 posiciones.
3. Asociar cada recorte con la clase indicada por su JSON.
4. Construir un dataset de las ocho clases.
5. Entrenar y evaluar un clasificador de Machine Learning con imágenes separadas por captura.
