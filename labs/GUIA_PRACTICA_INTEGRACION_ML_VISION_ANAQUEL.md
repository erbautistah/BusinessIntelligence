# Práctica: integrar Machine Learning y visión por computadora

**Unidad 4 – Inteligencia de Negocios**  
**Trabajo grupal:** 4 a 7 integrantes · **Laboratorio:** 90 minutos

## Objetivo

Generar un dataset propio, entrenar HOG + SVM y aplicar el modelo a una fotografía nueva para estimar los productos presentes en las 32 posiciones del anaquel.

## 1. Clonar el repositorio y preparar Python

Requisitos: Windows, Git for Windows (Git Bash) y Python 3.10 o superior.

Abrir Git Bash y ejecutar:

~~~bash
git clone https://github.com/mfernando25/tienda-inteligente.git
cd tienda-inteligente/cv-lab

py -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
~~~

## 2. Generar las 15 fotografías y sus etiquetas

Cada equipo debe generar su propio dataset. Las fotografías son **imágenes tomadas con un celular Android a la pantalla del computador donde se muestra el anaquel del generador**. No se deben tomar fotografías de productos reales ni de supermercados.

### Qué distribuciones preparar

| Captura | Distribución del anaquel |
|---|---|
| 001 | Distribución equilibrada, con varias categorías y espacios vacíos. |
| 002 | Escenario «Faltantes de productos». |
| 003 | Escenario «Anaquel completo» (32 posiciones ocupadas). |
| 004 | Escenario «Predominio de bebidas». |
| 005–009 | Cinco distribuciones personalizadas diferentes. Cambiar productos, cantidades y posiciones; procurar incluir las ocho categorías. |
| 010 | Pocos productos agrupados a la izquierda. |
| 011 | Pocos productos agrupados al centro o a la derecha. |
| 012 | Otra distribución de baja ocupación, con productos en filas y columnas diferentes. |
| 013 | Una distribución nueva con el cursor visible como interferencia moderada, preferentemente sobre un espacio vacío. |
| 014 | Una distribución nueva con brillo desigual o reflejo moderado en la pantalla. |
| 015 | Una distribución nueva fotografiada desde un ángulo ligeramente oblicuo o con una oclusión parcial que no impida identificar la cuadrícula. |

Las 15 distribuciones deben ser diferentes. No basta con fotografiar varias veces el mismo anaquel.

### Cómo tomar las fotografías

- Mostrar el anaquel completo en la pantalla, con las 4 filas y 8 columnas visibles.
- Mantener visibles las cuatro esquinas exteriores de la cuadrícula; no cortar los bordes.
- Tomar la fotografía en orientación horizontal, enfocada y sin movimiento.
- Evitar usar zoom digital, flash, filtros o edición posterior.
- Variar moderadamente distancia, ángulo e iluminación en las capturas indicadas; no deformar tanto la imagen que se pierda la cuadrícula.
- Para las capturas con interferencia, conservar suficiente visibilidad para que se pueda reconocer la posición y mantener la etiqueta real del JSON. Una celda vacía con el cursor encima sigue siendo la clase empty.
- Guardar el archivo original en formato JPG.


Iniciar el generador desde Git Bash:

~~~bash
cd ../shelf-generator
python -m http.server 8000
~~~

Abrir http://localhost:8000.

Crear las 15 distribuciones indicadas en [dataset/README.md](../cv-lab/dataset/README.md). Para cada distribución:

1. Configurar el anaquel.
2. Descargar el JSON desde el generador.
3. Renombrar el JSON con el número de captura: `captura_001.json`, `captura_002.json`, etc.
4. Activar el modo captura y fotografiar la pantalla con un celular Android.
5. Transferir la fotografía JPG a la laptop y renombrarla con el mismo nombre base: `captura_001.jpg`, `captura_002.jpg`, etc.
6. Guardar cada pareja en las carpetas correspondientes:

~~~text
cv-lab/dataset/
├── images/raw/
│   ├── captura_001.jpg
│   ├── captura_002.jpg
│   └── ... captura_015.jpg
└── labels/
    ├── captura_001.json
    ├── captura_002.json
    └── ... captura_015.json
~~~

**El nombre debe coincidir exactamente:** `captura_001.jpg` corresponde a `captura_001.json`. Repetir hasta completar las 15 parejas. Seguir el plan de distribuciones de `dataset/README.md`; no tomar 15 fotografías del mismo anaquel.

Las carpetas `images/raw/` y `labels/` ya existen. No hay que crearlas. El generador se utiliza para crear el anaquel y exportar el JSON; la fotografía se toma con Android. El PNG no es necesario.

Al terminar las 15 capturas, detener el servidor con `Ctrl + C` y volver a `cv-lab/`:

~~~bash
cd ../cv-lab
~~~

## 3. Preparar los recortes y entrenar el modelo

Ejecutar el procesamiento del dataset:

~~~bash
python preparar_dataset.py
~~~

Para cada fotografía, seleccionar las cuatro esquinas exteriores de la cuadrícula 4×8 en este orden: superior izquierda, superior derecha, inferior derecha e inferior izquierda.

El programa genera automáticamente:
- Las imágenes rectificadas.
- Los 32 recortes por fotografía, organizados en nueve clases: ocho productos y `empty`.
- El manifiesto `dataset/manifests/recortes.csv`.

Después, entrenar el modelo:

~~~bash
python entrenar_modelo.py
explorer.exe salida_ml/informe_evaluacion.html
~~~

Revisar las métricas por categoría, la matriz de confusión y los recortes mal clasificados. Identificar dos categorías con menor F1 y revisar al menos dos errores.

## 4. Crear una captura nueva para probar el modelo

Esta captura se realiza **después del entrenamiento**. No se incorpora al dataset de entrenamiento.

Iniciar nuevamente el generador:

~~~bash
cd ../shelf-generator
python -m http.server 8000
~~~

Abrir http://localhost:8000 y crear una distribución personalizada diferente de las 15 anteriores.

1. Descargar su JSON y renombrarlo `captura_016.json`.
2. Activar el modo captura y fotografiar el anaquel con Android.
3. Transferir la fotografía a la laptop y renombrarla `captura_016.jpg`.
4. Guardar los archivos en:

~~~text
cv-lab/dataset/images/raw/captura_016.jpg
cv-lab/dataset/labels/captura_016.json
~~~

Detener el servidor con `Ctrl + C` y volver a `cv-lab/`:

~~~bash
cd ../cv-lab
~~~

**No volver a ejecutar `preparar_dataset.py` ni `entrenar_modelo.py` después de agregar `captura_016`.** Esta fotografía se reserva para probar el modelo ya entrenado.

## 5. Crear el programa de predicción

Crear `predecir_anaquel.py` dentro de `cv-lab/`.

El programa recibe la fotografía y clasifica las 32 posiciones con el modelo entrenado. No debe consultar el JSON durante la predicción.

Implementar este flujo:

1. Cargar la fotografía indicada como argumento.
2. Reutilizar de `analizar_anaquel.py` las funciones `read_image()`, `select_corners()` y `rectify_shelf()`.
3. Cargar `salida_ml/modelo_hog_svm.yml` con `cv2.ml.SVM_load()`.
4. Leer `salida_ml/modelo_hog_svm.json` para recuperar las clases y los parámetros HOG.
5. Recorrer las 32 posiciones y extraer cada recorte con `crop_slot()` de `preparar_dataset.py`.
6. Para cada recorte:
   - Convertir a escala de grises.
   - Redimensionar a 72 × 96 píxeles.
   - Extraer HOG con ventana 72 × 96, bloque 16 × 16, desplazamiento 8 × 8, celda 8 × 8 y 9 orientaciones.
   - Enviar el descriptor al SVM y convertir la predicción a su nombre de clase usando la lista `classes` del JSON del modelo.

Fragmento para preparar cada recorte:

~~~python
gray = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
fixed = cv2.resize(gray, (72, 96), interpolation=cv2.INTER_AREA)
descriptor = hog.compute(fixed)
~~~

Guardar dentro de `salida_ml/`:

| Archivo | Contenido |
|---|---|
| `anaquel_predicho.png` | Anaquel rectificado con la clase predicha en cada posición. |
| `predicciones.csv` | Número de posición y clase predicha. |
| `inventario_predicho.json` | Cantidad de posiciones por categoría y total de vacíos. |

## 6. Ejecutar y evaluar

Ejecutar:

~~~bash
python predecir_anaquel.py "dataset/images/raw/captura_016.jpg"
~~~

Comparar las predicciones con `captura_016.json`. Para cada posición, registrar la clase real, la clase predicha y si fue un acierto o error.

Calcular:

~~~text
Accuracy = posiciones correctas / 32
~~~

Responder:

1. ¿Cuántas posiciones clasificó correctamente?
2. ¿Qué categorías confundió?
3. ¿Qué característica de la imagen pudo causar los errores?
4. ¿Qué diferencia hay entre detectar una posición ocupada y reconocer el producto?
5. ¿Qué limitaciones tiene el modelo para reconocer empaques comerciales?

## Entregables

- Las 15 parejas JPG + JSON (`captura_001` a `captura_015`).
- `predecir_anaquel.py`.
- `anaquel_predicho.png`, `predicciones.csv` e `inventario_predicho.json`.
- La pareja de prueba `captura_016.jpg` y `captura_016.json`.
- Tabla de comparación de las 32 posiciones y respuestas a las cinco preguntas.

No subir fotografías, JSON de captura, recortes, modelos ni resultados locales al repositorio público. Se puede subir el código fuente.

