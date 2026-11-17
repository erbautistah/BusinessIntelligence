# Dataset de fotografías del anaquel

Esta carpeta organiza las fotografías Android y las etiquetas de referencia para desarrollar y evaluar la solución de visión por computadora y Machine Learning.

## Estructura

- images/raw/: fotografías originales tomadas con Android. No modificar ni sobrescribir.
- images/rectified/: resultados rectificados por OpenCV.
- images/crops/: recortes generados automáticamente para cada posición.
- labels/: JSON de referencia exportado por el generador.
- manifests/: CSV que registra cada recorte, su captura de origen y su etiqueta.

Las subcarpetas de imágenes se mantienen localmente y están excluidas del control de versiones por tamaño. Los archivos .gitkeep conservan la estructura al clonar el repositorio.

## Mínimo acordado para la actividad

Cada grupo preparará **al menos 15 fotografías completas**, cada una con su JSON correspondiente.

Organización recomendada:
- 5 distribuciones distintas del anaquel.
- 3 fotografías por distribución, cambiando moderadamente ángulo, distancia o condiciones de iluminación.

Se parte de los cuatro escenarios del generador y se prepara una quinta distribución personalizada. Si las tres fotos corresponden a la misma distribución, se duplica el JSON de referencia con el nombre base de cada fotografía.

Quince fotografías producen hasta 480 recortes (32 posiciones por captura). El número de recortes de producto depende de cuántos espacios estén ocupados. Los recortes procedentes de una misma captura no se deben repartir entre entrenamiento y prueba.

## Cómo registrar una captura

1. En el generador, configura una distribución.
2. Exporta el JSON correspondiente.
3. Fotografía el anaquel con Android.
4. Copia la fotografía original a images/raw/.
5. Copia el JSON a labels/.
6. Usa el mismo nombre base para ambos archivos.

Ejemplo:

~~~text
images/raw/captura_001.jpg
labels/captura_001.json
~~~

## Preparación automática de recortes

Desde cv-lab/, con el entorno virtual activo:

~~~bash
python preparar_dataset.py
~~~

El programa recorre las fotos de images/raw/. Para cada foto:
1. solicita seleccionar cuatro esquinas de la cuadrícula;
2. rectifica la perspectiva;
3. recorta automáticamente las 32 posiciones;
4. lee el JSON de igual nombre;
5. guarda cada recorte en la carpeta de su clase o en empty/;
6. registra el resultado en manifests/recortes.csv.

Se marcan las esquinas una vez por foto. No es necesario ejecutar el programa por separado para cada imagen.

## Estructura de los recortes

~~~text
images/crops/
├── water/
├── milk/
├── soda/
├── juice/
├── cookies/
├── cereal/
├── canned/
├── detergent/
└── empty/
~~~

Cada recorte conserva el nombre de captura y posición, por ejemplo captura_001_slot_03.png. La carpeta empty/ contiene posiciones sin producto; no es una categoría de producto.

## Variaciones de captura

Varía de manera controlada:
- distribución y posiciones de productos;
- distancia al monitor;
- ángulo horizontal o vertical moderado;
- brillo de pantalla y luz ambiental;
- dispositivo Android, si hay más de uno disponible.

Asegúrate de que la cuadrícula completa siga visible y que sus cuatro esquinas puedan identificarse.

## Qué no hacer

- No editar las fotografías originales.
- No aplicar filtros ni compresión adicional.
- No asociar un JSON si no corresponde exactamente a la distribución fotografiada.
- No mezclar capturas casi idénticas entre entrenamiento y prueba.
- No asumir que una foto desenfocada o incompleta debe usarse para entrenar sin revisar su utilidad y etiqueta.

## Privacidad y Git

Las fotos originales, rectificadas y los recortes no se suben automáticamente a GitHub. Permanecen en la laptop del grupo. No fotografíes personas ni información personal.

Las etiquetas JSON y el manifiesto CSV contienen metadatos de las posiciones, no datos personales. La carpeta no debe contener datos personales.
