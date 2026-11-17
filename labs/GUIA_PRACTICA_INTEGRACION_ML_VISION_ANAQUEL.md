# Guía de práctica: integración de Machine Learning y visión por computadora

**Unidad 4 – Inteligencia de Negocios**  
**Ejes de trabajo:** Machine Learning como parte de la IA y Visión por computadora.  
**Modalidad:** trabajo grupal (4 a 7 integrantes).  
**Tiempo de laboratorio:** 90 minutos.

---

## 1. Propósito de la práctica

Integrar los componentes desarrollados en las actividades anteriores para construir un flujo que reciba una fotografía de un anaquel, localice sus 32 posiciones, clasifique cada posición con el modelo HOG + SVM y genere un inventario visual estimado.

Al finalizar, el equipo deberá poder explicar qué partes corresponden a visión por computadora, cuáles a Machine Learning y cómo se comprueba el resultado.

**Resultado esperado:** un prototipo local que procese una fotografía del anaquel y genere una imagen anotada y un resumen de las categorías identificadas.

## 2. Punto de partida

El repositorio ya contiene los componentes siguientes:

| Componente | Archivo | Función |
|---|---|---|
| Generador de anaqueles | \`shelf-generator/\` | Construye el anaquel 2D y exporta PNG, JSON y CSV. |
| Procesamiento OpenCV | \`cv-lab/analizar_anaquel.py\` | Selecciona las cuatro esquinas y rectifica la cuadrícula 4×8. |
| Preparación del dataset | \`cv-lab/preparar_dataset.py\` | Extrae 32 recortes por fotografía y los etiqueta usando el JSON. |
| Entrenamiento | \`cv-lab/entrenar_modelo.py\` | Extrae HOG y entrena el clasificador SVM. |
| Modelo entrenado | \`cv-lab/salida_ml/modelo_hog_svm.yml\` | Contiene el clasificador generado localmente. |
| Configuración del modelo | \`cv-lab/salida_ml/modelo_hog_svm.json\` | Contiene las clases y los parámetros usados por HOG y SVM. |
| Informe de evaluación | \`cv-lab/salida_ml/informe_evaluacion.html\` | Presenta métricas, matriz de confusión y recortes mal clasificados. |

El dataset contiene 15 fotografías y hasta 480 recortes. La separación se realizó por fotografía:

- Capturas 001–009: entrenamiento.
- Capturas 010–012: validación.
- Capturas 013–015: prueba.

La clase \`empty\` representa una posición vacía; no es un producto. En total, el clasificador trabaja con nueve clases: ocho productos y una clase vacía.

## 3. Requisitos previos

Antes de iniciar, comprobar que el equipo dispone de:

- Repositorio actualizado.
- Python y entorno virtual \`.venv\` configurado.
- Dependencias instaladas desde \`requirements.txt\`.
- Fotografías, recortes y manifiesto del dataset preparados localmente.
- Modelo entrenado en \`cv-lab/salida_ml/\`.

Desde Git Bash, en la carpeta raíz del repositorio:

~~~bash
git pull
cd cv-lab
source .venv/Scripts/activate
~~~

Ejecutar el entrenamiento para generar el modelo y el informe visual con la versión actual del código:

~~~bash
python entrenar_modelo.py
~~~

Abrir el informe:

~~~bash
explorer.exe salida_ml/informe_evaluacion.html
~~~

**Comprobación:** no continuar hasta que existan \`modelo_hog_svm.yml\`, \`modelo_hog_svm.json\` e \`informe_evaluacion.html\` en \`salida_ml/\`.

> El modelo y sus resultados se generan en la laptop del grupo. La carpeta \`salida_ml/\` está excluida de GitHub; cada equipo debe entrenar su propio modelo con su dataset local.

## 4. Actividad 1 – Interpretar la evaluación del modelo

**Tiempo sugerido: 10 minutos.**

Abrir \`informe_evaluacion.html\` y revisar exclusivamente el conjunto de prueba.

En equipo, registrar:

1. ¿Cuál es el valor de accuracy y cuántas predicciones fueron incorrectas?
2. ¿Qué dos categorías tienen el F1 más bajo?
3. En la matriz de confusión, ¿qué categorías se confunden entre sí?
4. Al revisar la galería de errores, ¿qué característica visual podría explicar alguna confusión?

No se busca mejorar todavía el modelo. Primero se debe comprender su comportamiento y reconocer sus limitaciones.

## 5. Actividad 2 – Integrar la predicción del anaquel

**Tiempo sugerido: 45 minutos.**

Hasta ahora, el clasificador recibe un recorte individual y devuelve una clase. En esta actividad se construirá un programa que ejecute el proceso completo sobre una fotografía.

Crear el archivo:

~~~text
cv-lab/predecir_anaquel.py
~~~

El programa debe implementar las siguientes operaciones, en este orden:

### Paso 1. Recibir la fotografía

El programa debe recibir la ruta de una fotografía Android como argumento. No debe utilizar el JSON para decidir qué productos aparecen.

Ejemplo de uso que tendrá el programa:

~~~bash
python predecir_anaquel.py "dataset/images/raw/captura_016.jpg"
~~~

### Paso 2. Rectificar el anaquel

Reutilizar las funciones de \`analizar_anaquel.py\`:

- \`read_image()\`: carga la fotografía.
- \`select_corners()\`: permite seleccionar las cuatro esquinas exteriores de la cuadrícula.
- \`rectify_shelf()\`: corrige la perspectiva.

La selección manual de las esquinas se mantiene en esta versión.

### Paso 3. Cargar el modelo

Cargar:

- \`salida_ml/modelo_hog_svm.yml\` con \`cv2.ml.SVM_load()\`.
- \`salida_ml/modelo_hog_svm.json\` para recuperar las clases y los parámetros de HOG.

No se debe volver a entrenar el modelo dentro del proceso de predicción.

### Paso 4. Extraer los 32 recortes

Reutilizar \`crop_slot()\` de \`preparar_dataset.py\`. La función extrae la región de producto de cada posición, sin incluir el número, nombre o precio.

Recorrer las posiciones del 1 al 32.

### Paso 5. Aplicar HOG y SVM a cada recorte

Es fundamental utilizar la misma configuración que se utilizó durante el entrenamiento:

- Convertir el recorte a escala de grises.
- Redimensionar a 72 × 96 píxeles (ancho × alto).
- Calcular el descriptor HOG con ventana 72 × 96, bloque 16 × 16, desplazamiento 8 × 8, celda 8 × 8 y 9 orientaciones.
- Entregar el descriptor al clasificador SVM.
- Convertir el índice predicho a su identificador de clase utilizando la lista \`classes\` del archivo \`modelo_hog_svm.json\`.

Fragmento orientativo para la extracción de características:

~~~python
gray = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
fixed = cv2.resize(gray, (72, 96), interpolation=cv2.INTER_AREA)
descriptor = hog.compute(fixed)
~~~

El descriptor debe convertirse en una muestra de una fila antes de llamar a \`svm.predict()\`.

### Paso 6. Generar los resultados

El programa debe guardar, como mínimo:

| Archivo | Contenido |
|---|---|
| \`salida_ml/anaquel_predicho.png\` | Fotografía rectificada y anotada con la predicción de cada posición. |
| \`salida_ml/predicciones.csv\` | Número de posición y categoría predicha. |
| \`salida_ml/inventario_predicho.json\` | Conteo de posiciones por categoría y total de posiciones vacías. |

La imagen anotada debe mostrar el número de posición y la categoría que predijo el modelo.

El inventario generado es una **estimación visual de las posiciones del anaquel**. No representa el stock total de almacén ni las unidades disponibles fuera del anaquel.

## 6. Actividad 3 – Contrastar la predicción con la referencia

**Tiempo sugerido: 20 minutos.**

Para comprobar el flujo completo, generar una captura adicional con una distribución personalizada:

1. Abrir el generador actual.
2. Crear una distribución diferente de las 15 utilizadas para preparar el dataset. Procurar incluir las ocho categorías y algunas posiciones vacías.
3. Exportar el JSON de esa distribución.
4. Activar el modo captura y tomar una fotografía Android.
5. Guardar la pareja localmente:

~~~text
cv-lab/dataset/images/raw/captura_016.jpg
cv-lab/dataset/labels/captura_016.json
~~~

Esta captura es una prueba externa de integración: **no se incorpora al entrenamiento ni modifica el manifiesto de las 15 capturas**.

Ejecutar \`predecir_anaquel.py\` sobre \`captura_016.jpg\`. Primero guardar las predicciones y los resultados. Solo después abrir \`captura_016.json\` para comparar las predicciones con las etiquetas reales.

Para cada una de las 32 posiciones, comparar:

- Categoría real: \`product_id\` del JSON; si no existe producto, la clase real es \`empty\`.
- Categoría predicha: resultado entregado por HOG + SVM.
- Resultado: acierto o error.

Calcular:

- Número de posiciones correctamente clasificadas.
- Número de posiciones incorrectamente clasificadas.
- Accuracy sobre las 32 posiciones.

~~~text
Accuracy = posiciones correctas / 32
~~~

**Regla:** el JSON se utiliza únicamente después de la predicción para evaluar. No debe pasarse al clasificador ni utilizarse para corregir automáticamente sus resultados.

## 7. Actividad 4 – Interpretar el resultado

**Tiempo sugerido: 10 minutos.**

Responder en equipo:

1. ¿El inventario estimado coincide con la distribución real? Indicar cuántas posiciones se clasificaron correctamente.
2. ¿Qué producto o productos fueron confundidos?
3. ¿El error parece estar relacionado con el recorte, la iluminación, la perspectiva o las características visuales de las ilustraciones?
4. ¿Qué diferencia existe entre detectar que una posición está ocupada y reconocer qué producto contiene?
5. ¿Por qué este modelo no puede considerarse todavía un reconocedor de productos comerciales?

Las respuestas deben apoyarse en la imagen anotada, el archivo de predicciones y la comparación con el JSON.

## 8. Entregables

Cada equipo debe conservar en su laptop:

1. \`predecir_anaquel.py\` funcional.
2. \`salida_ml/anaquel_predicho.png\`.
3. \`salida_ml/predicciones.csv\`.
4. \`salida_ml/inventario_predicho.json\`.
5. \`captura_016.jpg\` y \`captura_016.json\`.
6. Un breve análisis de las cinco preguntas de la actividad 4.

El código fuente del script puede incorporarse al repositorio mediante Git. Las fotografías, recortes, modelos entrenados y resultados locales no deben subirse al repositorio público.

## 9. Criterios de revisión

Se revisará que el equipo:

- Integre correctamente OpenCV, HOG y SVM en un solo flujo.
- Mantenga las mismas dimensiones y parámetros HOG utilizados durante el entrenamiento.
- Genere las predicciones de las 32 posiciones sin utilizar el JSON como entrada.
- Contraste las predicciones con la referencia y calcule la exactitud.
- Interprete los errores y reconozca las limitaciones de la solución.

## 10. Alcance y límites de esta práctica

El prototipo trabaja con un anaquel fijo de 4 × 8 y con las ocho ilustraciones controladas del generador actual. La cuadrícula se localiza mediante cuatro esquinas seleccionadas manualmente.

Esta práctica integra la primera solución de Machine Learning y visión por computadora de la tienda inteligente. No implementa detección automática de anaqueles, reconocimiento de empaques reales, gestión de inventario físico ni conexión con sistemas comerciales.

**La siguiente sesión de la Unidad 4 se reservará para completar los ejes temáticos de Procesamiento de lenguaje natural y Sistemas conversacionales.** Los resultados del inventario visual podrán utilizarse como contexto de negocio para esa actividad.
