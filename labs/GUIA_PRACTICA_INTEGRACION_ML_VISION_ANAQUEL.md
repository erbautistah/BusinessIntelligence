# Práctica: integrar Machine Learning y visión por computadora

**Unidad 4 – Inteligencia de Negocios**  
**Trabajo grupal:** 4 a 7 integrantes · **Laboratorio:** 90 minutos

## Objetivo

Integrar OpenCV y el clasificador HOG + SVM para procesar una fotografía del anaquel, clasificar sus 32 posiciones y generar un inventario visual estimado.

## 1. Descargar el proyecto y preparar el entorno

Requisitos: Windows, Git for Windows (Git Bash) y Python 3.10 o superior.

Abrir Git Bash y ejecutar:

~~~bash
git clone https://github.com/mfernando25/tienda-inteligente.git
cd tienda-inteligente/cv-lab

py -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
~~~

## 2. Copiar el dataset de práctica

El repositorio no incluye las fotografías ni los recortes del dataset. El docente proporcionará el paquete preparado con esta estructura:

~~~text
dataset/
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

Crear las carpetas para la nueva captura y copiar el paquete del docente dentro de `tienda-inteligente/cv-lab/`:

~~~bash
mkdir -p dataset/images/raw dataset/labels
~~~

Comprobar que exista:

~~~text
cv-lab/dataset/manifests/recortes.csv
~~~

El paquete contiene los 480 recortes etiquetados de las 15 capturas. No es necesario volver a generar los recortes durante esta práctica.

## 3. Entrenar y revisar el modelo

Desde la carpeta `cv-lab`, con el entorno virtual activo:

~~~bash
python entrenar_modelo.py
explorer.exe salida_ml/informe_evaluacion.html
~~~

En el informe, revisar el conjunto **Test**:

- Accuracy y F1 macro.
- Métricas por categoría.
- Matriz de confusión.
- Recortes que el modelo clasificó incorrectamente.

Anotar dos categorías con dificultades y revisar al menos dos errores de la galería.

## 4. Crear el programa de predicción del anaquel

Crear `predecir_anaquel.py` dentro de `cv-lab/`.

El programa recibirá una fotografía y utilizará el modelo entrenado para clasificar sus 32 posiciones. No debe utilizar el JSON durante la predicción.

### Procesamiento requerido

1. Cargar la fotografía indicada como argumento.
2. Reutilizar de `analizar_anaquel.py` las funciones `read_image()`, `select_corners()` y `rectify_shelf()`.
3. Cargar `salida_ml/modelo_hog_svm.yml` con `cv2.ml.SVM_load()`.
4. Leer `salida_ml/modelo_hog_svm.json` para recuperar las clases y la configuración HOG.
5. Recorrer las 32 posiciones y extraer cada recorte con `crop_slot()` de `preparar_dataset.py`.
6. Para cada recorte:
   - Convertir a escala de grises.
   - Redimensionar a 72 × 96 píxeles.
   - Extraer HOG con la misma configuración del entrenamiento: ventana 72 × 96, bloque 16 × 16, desplazamiento 8 × 8, celda 8 × 8 y 9 orientaciones.
   - Enviar el descriptor al SVM y convertir la salida al nombre de clase usando la lista `classes` del archivo JSON del modelo.

Fragmento para preparar cada imagen:

~~~python
gray = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
fixed = cv2.resize(gray, (72, 96), interpolation=cv2.INTER_AREA)
descriptor = hog.compute(fixed)
~~~

### Archivos que debe generar

Guardar dentro de `salida_ml/`:

| Archivo | Contenido |
|---|---|
| `anaquel_predicho.png` | Anaquel rectificado con la clase predicha en cada posición. |
| `predicciones.csv` | Número de posición y clase predicha. |
| `inventario_predicho.json` | Cantidad de posiciones predichas por categoría y total de vacíos. |

El inventario es una estimación de lo que aparece en el anaquel; no representa el stock total de almacén.

## 5. Probar con una distribución nueva

Crear una distribución personalizada en el generador incluido en `shelf-generator/`. Debe ser diferente de las 15 utilizadas para entrenar y evaluar el modelo.

1. Iniciar el generador desde Git Bash:

~~~bash
cd ../shelf-generator
python -m http.server 8000
~~~

2. Abrir http://localhost:8000.
3. Crear una distribución con varias categorías y espacios vacíos.
4. Exportar el JSON y guardarlo como `captura_016.json`.
5. Activar el modo captura y fotografiar el anaquel con un celular Android.
6. Guardar la fotografía como `captura_016.jpg`.

Copiar los archivos a:

~~~text
cv-lab/dataset/images/raw/captura_016.jpg
cv-lab/dataset/labels/captura_016.json
~~~

Transferir la fotografía a la laptop por el medio disponible. No modificar la distribución entre exportar el JSON y tomar la foto.

Detener el servidor del generador con `Ctrl + C` y regresar a la carpeta de trabajo:

~~~bash
cd ../cv-lab
~~~

Ejecutar:

~~~bash
python predecir_anaquel.py "dataset/images/raw/captura_016.jpg"
~~~

## 6. Comparar y entregar

Después de ejecutar la predicción, abrir el JSON y comparar la clase real de cada posición con la clase predicha. El JSON se utiliza solo para evaluar, nunca como entrada del modelo.

Registrar para las 32 posiciones:

- Número de posición.
- Clase real.
- Clase predicha.
- Acierto o error.

Calcular:

~~~text
Accuracy = posiciones correctas / 32
~~~

**Entregables del equipo:**

1. `predecir_anaquel.py`.
2. `anaquel_predicho.png`.
3. `predicciones.csv` e `inventario_predicho.json`.
4. `captura_016.jpg` y `captura_016.json`.
5. Una tabla de comparación de las 32 posiciones y una conclusión breve: ¿qué categorías confundió el modelo y qué pudo causar esos errores?

No subir fotografías, recortes, modelos ni resultados locales al repositorio público. Se puede subir el código fuente.

**La próxima sesión se dedicará a Procesamiento de lenguaje natural y Sistemas conversacionales.**
