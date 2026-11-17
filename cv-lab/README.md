# OpenCV: primera etapa de visión por computadora

Esta etapa recibe **solo la fotografía tomada con Android** para procesar el anaquel. No utiliza el PNG original ni el JSON para detectar objetos.

## Qué hace esta primera versión

1. Carga la fotografía JPG/PNG del celular.
2. Permite seleccionar las cuatro esquinas exteriores de la cuadrícula 4×8.
3. Corrige la perspectiva con una transformación proyectiva.
4. Divide la imagen rectificada en 32 posiciones.
5. Analiza una región central de cada posición en espacio HSV.
6. Clasifica cada posición como **ocupada** o **vacía** usando un umbral de color.
7. Guarda una imagen anotada, un CSV y un JSON con los resultados.

**Alcance deliberado:** todavía no identifica cuál de los ocho productos está en cada posición y no entrena un modelo de ML. Esta primera versión resuelve la geometría del anaquel y la detección de ocupación.

## Requisitos

- Windows 10/11 (también puede ejecutarse en otros sistemas).
- Python 3.10 o superior.
- Cámara Android y una fotografía del anaquel.
- OpenCV y NumPy, instalados desde el archivo requirements.txt.

## Instalación en Windows

Desde PowerShell, en la raíz del repositorio:

~~~powershell
cd cv-lab
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
~~~

Si PowerShell bloquea la activación del entorno virtual, se puede ejecutar el intérprete del entorno directamente:

~~~powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
~~~

## Ejecutar el análisis

Con el entorno virtual activado y estando dentro de cv-lab:

~~~powershell
python analizar_anaquel.py "C:\ruta\a\foto-android.jpg"
~~~

Se abrirá una ventana para seleccionar cuatro puntos. Haz clic en las esquinas exteriores de la cuadrícula de posiciones, no en los bordes del monitor:

1. Esquina superior izquierda.
2. Esquina superior derecha.
3. Esquina inferior derecha.
4. Esquina inferior izquierda.

Después pulsa **Enter** para confirmar. Usa **R** para reiniciar la selección o **Esc** para cancelar.

El programa corrige la perspectiva y presenta la imagen con los resultados. Pulsa una tecla en la ventana de resultados para cerrarla.

## Archivos de salida

Se crea la carpeta salida_cv/:

- anaquel_rectificado.png: cuadrícula transformada a una vista frontal.
- resultado_ocupacion.png: posiciones marcadas en verde (ocupadas) y naranja (vacías).
- detecciones.csv: una fila por posición, con estado y proporción de píxeles de color.
- resultado.json: configuración del método, umbrales y resultados por posición.

## Comparar contra la respuesta esperada

El PNG y el JSON exportados por el generador **no entran en el algoritmo de detección**. El JSON se usa únicamente después, para comparar las posiciones detectadas con la distribución conocida.

Ejemplo:

~~~powershell
python comparar_referencia.py --detecciones salida_cv/detecciones.csv --referencia "C:\ruta\anaquel-equilibrado.json"
~~~

El comparador produce salida_cv/validacion.json y calcula exactitud, precisión, recall y F1 para la tarea binaria ocupado/vacío. Estas métricas no evalúan la clasificación de los ocho productos.

## Parámetros iniciales

En analizar_anaquel.py:
- SATURATION_THRESHOLD: saturación mínima del píxel.
- VALUE_THRESHOLD: brillo mínimo del píxel.
- OCCUPANCY_THRESHOLD: proporción mínima de píxeles de color para marcar una posición como ocupada.
- ICON_X_RANGE e ICON_Y_RANGE: zona analizada de cada posición.

Son umbrales iniciales ajustados al catálogo ilustrado del generador. Pueden fallar con fotografías muy oscuras, reflejos fuertes, otros diseños de productos o cambios en la interfaz.

## Qué significa que una fotografía tenga fallas

Las variaciones de perspectiva, iluminación, enfoque y reflejos son útiles para probar la robustez. Para usarlas en entrenamiento se necesitan múltiples fotografías y etiquetas correctas. No se debe entrenar con una imagen mal identificada como si su detección errónea fuera la respuesta correcta.

Se debe mantener separado:
- **Entrenamiento:** fotos etiquetadas que permiten ajustar el clasificador.
- **Validación:** fotos distintas usadas para ajustar parámetros y comparar alternativas.
- **Prueba final:** fotos que no se utilizaron para entrenar ni ajustar.

Una sola fotografía, aunque se detecte correctamente, no demuestra que el método funcione con otras cámaras o condiciones.

## Siguiente etapa

Tras validar la detección ocupado/vacío con varias fotografías, se preparará un conjunto etiquetado por producto y se implementará la clasificación de las ocho categorías. Esa etapa permitirá integrar ML de forma explícita y evaluar su desempeño con datos separados.
