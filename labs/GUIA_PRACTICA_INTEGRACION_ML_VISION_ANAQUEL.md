# Práctica: integrar Machine Learning y visión por computadora

**Unidad 4 – Inteligencia de Negocios**  
**Trabajo grupal:** 4 a 7 integrantes · **Laboratorio:** 90 minutos

## Objetivo

Aplicar el modelo HOG + SVM a una fotografía nueva del anaquel, clasificar sus 32 posiciones y comparar el inventario estimado con la distribución real.

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

## 2. Cargar el dataset de entrenamiento

Las imágenes del dataset no están incluidas en GitHub. El docente entregará un archivo ZIP con los 480 recortes y el manifiesto.

1. Descomprimir el ZIP.
2. Copiar su carpeta \`images/crops/\` y su carpeta \`manifests/\` dentro de \`cv-lab/dataset/\`.
3. Si el sistema pregunta, combinar las carpetas.

La estructura final debe quedar así:

~~~text
cv-lab/
└── dataset/
    ├── images/
    │   └── crops/
    │       ├── canned/
    │       ├── cereal/
    │       ├── cookies/
    │       ├── detergent/
    │       ├── empty/
    │       ├── juice/
    │       ├── milk/
    │       ├── soda/
    │       └── water/
    └── manifests/
        └── recortes.csv
~~~

Las carpetas \`raw/\` y \`labels/\` ya forman parte del repositorio. No es necesario crearlas manualmente.

## 3. Entrenar y revisar el modelo

Desde \`cv-lab/\`, con el entorno virtual activo:

~~~bash
python entrenar_modelo.py
explorer.exe salida_ml/informe_evaluacion.html
~~~

Revisar el conjunto **Test**: métricas por categoría, matriz de confusión y recortes mal clasificados. Anotar dos categorías con menor F1 e identificar al menos dos errores.

## 4. Iniciar el generador y crear una nueva distribución

El generador permite construir el anaquel virtual; no se cargan fotografías dentro de él. La fotografía se toma después con un celular Android.

Desde la terminal ubicada en \`cv-lab/\`, ejecutar:

~~~bash
cd ../shelf-generator
python -m http.server 8000
~~~

Abrir http://localhost:8000.

1. Crear una distribución personalizada distinta de las 15 capturas del dataset.
2. Procurar incluir varias categorías y espacios vacíos.
3. Descargar el archivo JSON de esa distribución.
4. Activar el modo captura y fotografiar la pantalla con un celular Android.
5. Transferir la fotografía JPG a la laptop.

Guardar los dos archivos con el mismo nombre base:

~~~text
cv-lab/dataset/images/raw/captura_016.jpg
cv-lab/dataset/labels/captura_016.json
~~~

El JPG es la entrada del modelo. El JSON se reserva para comparar las predicciones con la distribución real. El PNG del generador no es necesario.

Detener el servidor con \`Ctrl + C\` y volver a \`cv-lab/\`:

~~~bash
cd ../cv-lab
~~~

## 5. Crear el programa de predicción

Crear \`predecir_anaquel.py\` dentro de \`cv-lab/\`.

El programa recibirá una fotografía y clasificará las 32 posiciones con el modelo ya entrenado. No debe utilizar el JSON durante la predicción.

Implementar este flujo:

1. Cargar la fotografía indicada como argumento.
2. Reutilizar de \`analizar_anaquel.py\` las funciones \`read_image()\`, \`select_corners()\` y \`rectify_shelf()\`.
3. Cargar \`salida_ml/modelo_hog_svm.yml\` con \`cv2.ml.SVM_load()\`.
4. Leer \`salida_ml/modelo_hog_svm.json\` para recuperar las clases y los parámetros de HOG.
5. Recorrer las 32 posiciones y extraer cada recorte con \`crop_slot()\` de \`preparar_dataset.py\`.
6. Para cada recorte:
   - Convertir a escala de grises.
   - Redimensionar a 72 × 96 píxeles.
   - Extraer HOG con ventana 72 × 96, bloque 16 × 16, desplazamiento 8 × 8, celda 8 × 8 y 9 orientaciones.
   - Enviar el descriptor al SVM y convertir la predicción a su nombre de clase usando la lista \`classes\` del JSON del modelo.

Fragmento para preparar el recorte:

~~~python
gray = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
fixed = cv2.resize(gray, (72, 96), interpolation=cv2.INTER_AREA)
descriptor = hog.compute(fixed)
~~~

Guardar los resultados dentro de \`salida_ml/\`:

| Archivo | Contenido |
|---|---|
| \`anaquel_predicho.png\` | Anaquel rectificado con la clase predicha en cada posición. |
| \`predicciones.csv\` | Número de posición y clase predicha. |
| \`inventario_predicho.json\` | Cantidad de posiciones por categoría y total de vacíos. |

## 6. Ejecutar y evaluar

Desde \`cv-lab/\`:

~~~bash
python predecir_anaquel.py "dataset/images/raw/captura_016.jpg"
~~~

Comparar las predicciones con \`captura_016.json\`. Para cada posición, registrar la clase real, la clase predicha y si fue un acierto o error.

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

- \`predecir_anaquel.py\`.
- \`anaquel_predicho.png\`, \`predicciones.csv\` e \`inventario_predicho.json\`.
- \`captura_016.jpg\` y \`captura_016.json\`.
- Tabla de comparación de las 32 posiciones y respuestas a las cinco preguntas.

No subir fotografías, recortes, modelos ni resultados locales al repositorio público. Se puede subir el código fuente.

**La próxima sesión se dedicará a Procesamiento de lenguaje natural y Sistemas conversacionales.**
