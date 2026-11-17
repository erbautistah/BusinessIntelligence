# Dataset de fotografías del anaquel

Esta carpeta organiza las fotografías Android y las etiquetas de referencia para desarrollar y evaluar la solución de visión por computadora y Machine Learning.

## Estructura

- images/raw/: fotografías originales tomadas con Android. No modificar ni sobrescribir.
- images/rectified/: resultados rectificados por OpenCV.
- images/crops/: recortes generados de cada posición del anaquel.
- labels/: JSON de referencia exportado por el generador.

Las subcarpetas de imágenes se mantienen localmente y están excluidas del control de versiones por tamaño. Los archivos .gitkeep conservan la estructura al clonar el repositorio.

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

Si tomas tres fotografías de la misma distribución, conserva tres pares:

~~~text
images/raw/captura_001.jpg
images/raw/captura_002.jpg
images/raw/captura_003.jpg
labels/captura_001.json
labels/captura_002.json
labels/captura_003.json
~~~

Puedes copiar el JSON original y renombrar la copia para cada fotografía que represente exactamente la misma distribución.

## Variaciones de captura

Para obtener datos útiles, no tomes únicamente tres fotos idénticas desde el mismo lugar. Varía de manera controlada:
- Distribución y posiciones de productos.
- Distancia al monitor.
- Ángulo horizontal o vertical moderado.
- Brillo de pantalla y luz ambiental.
- Dispositivo Android, si hay más de uno disponible.

Asegúrate de que la cuadrícula completa siga siendo visible y que los cuatro bordes puedan identificarse.

## Qué no hacer

- No editar las fotografías originales.
- No aplicar filtros ni compresión adicional.
- No asociar un JSON si no corresponde exactamente a la distribución fotografiada.
- No mezclar fotos casi idénticas entre entrenamiento y prueba.
- No asumir que una foto con errores de desenfoque o encuadre debe usarse para entrenar sin revisar su etiqueta y utilidad.

## Privacidad y Git

Las fotos originales, rectificadas y los recortes no se suben automáticamente a GitHub. Permanecen en la laptop del grupo. No fotografíes personas ni información personal.

Las etiquetas JSON pueden compartirse si el equipo docente lo solicita. La carpeta no debe contener datos personales.
