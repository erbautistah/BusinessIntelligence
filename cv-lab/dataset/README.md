# Dataset de fotografías del anaquel

Esta carpeta organiza las fotografías Android y las etiquetas de referencia para desarrollar y evaluar la solución de visión por computadora y Machine Learning.

## Estructura

- images/raw/: fotografías originales tomadas con Android. No modificar ni sobrescribir.
- images/rectified/: resultados rectificados por OpenCV.
- images/crops/: recortes generados automáticamente para cada posición.
- labels/: JSON de referencia exportado por el generador.
- manifests/: CSV que registra cada recorte, su captura de origen y su etiqueta.

Las subcarpetas de imágenes se mantienen localmente y están excluidas del control de versiones por tamaño. Los archivos .gitkeep conservan la estructura al clonar el repositorio.

## Mínimo acordado para la actividad: 15 fotografías distintas

Cada grupo preparará **al menos 15 fotografías completas**, una por cada configuración diferente del anaquel. Cada imagen tendrá su JSON correspondiente.

No tomaremos tres fotografías de una misma distribución para contarlas como tres configuraciones. Eso solo cambia la cámara, pero repite la disposición y reduce la diversidad de ejemplos.

Plan de captura:

| Fotos | Configuración | Qué variar |
|---|---|---|
| 001–004 | Cuatro escenarios predefinidos | Equilibrado, faltantes, completo y predominio de bebidas. La 001 ya está capturada. |
| 005–009 | Cinco distribuciones personalizadas | Cambiar posiciones y cantidades; procurar que aparezcan todas las categorías. |
| 010–012 | Tres distribuciones de baja ocupación o productos concentrados | Varios espacios vacíos y productos agrupados en distintas zonas. |
| 013–015 | Tres distribuciones diferentes con interferencias visuales moderadas | Cursor, reflejo, brillo desigual u oclusión parcial simulada. Cada una debe seguir mostrando claramente el anaquel. |

Las 15 deben tener distribuciones diferentes. También se variarán moderadamente distancia, ángulo y condiciones de luz, sin perder las cuatro esquinas de la cuadrícula.

### Cobertura de categorías

El catálogo tiene ocho clases de producto. Durante la creación de las distribuciones, procura que:
- cada producto aparezca repetidamente;
- cada producto aparezca en distintas filas y columnas;
- ninguna categoría quede casi ausente del conjunto;
- las distribuciones de baja ocupación no eliminen siempre las mismas clases.

Después de generar el manifiesto, revisaremos los conteos por categoría y por captura. Si alguna categoría tiene pocos ejemplos, se añadirán fotografías dirigidas a cubrir esa falta. Quince es el mínimo de partida, no una garantía de que el dataset ya sea suficiente para entrenar y evaluar bien.

## Cómo registrar cada captura

Para cada una de las 15 configuraciones:

1. En el generador, configura una distribución diferente.
2. Exporta el JSON de esa distribución.
3. Fotografía el anaquel con Android.
4. Copia la foto original a images/raw/.
5. Copia el JSON a labels/.
6. Usa el mismo nombre base para ambos archivos.

Ejemplo:

~~~text
images/raw/captura_001.jpg
labels/captura_001.json
~~~

Cada fotografía tendrá su propio JSON porque cada distribución es distinta. No reutilices un JSON de otra distribución.

## Fotografías con interferencias

Las imperfecciones son parte de la prueba, no errores que deban eliminarse siempre. Se pueden incluir:
- cursor visible sobre el anaquel;
- reflejo o brillo desigual de la pantalla;
- objeto que tape parcialmente una ilustración;
- perspectiva algo más oblicua.

La etiqueta debe describir el contenido real de la posición, no el artefacto:
- Si la posición está vacía y aparece el cursor, sigue siendo empty.
- Si se ve parcialmente un producto identificable, se etiqueta con el producto real y se registra la interferencia para revisión.
- Si no se puede determinar qué producto hay, no se inventa la etiqueta; esa muestra se marca para revisión o se excluye del entrenamiento.

Las fotografías del anaquel virtual permiten estudiar cursor, perspectiva, reflejos y oclusiones simuladas. No equivalen a imágenes de anaqueles físicos con polvo, insectos, empaques deteriorados o estructuras rotas.

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

Quince fotografías producen hasta 480 recortes (32 posiciones por captura). Los recortes vacíos forman parte de esos 480; el número de recortes de productos será menor. Los 480 recortes tampoco son 480 fotografías independientes: 32 recortes comparten una misma captura y sus condiciones.

## Separación para entrenamiento, validación y prueba

La separación se hará por fotografía/configuración, no mezclando recortes al azar. Como punto de partida se puede usar:
- 9 capturas para entrenamiento;
- 3 para validación;
- 3 para prueba final.

Antes de fijar esa división se comprobará que las ocho clases estén representadas en los tres conjuntos. Si no lo están, se ajustarán las distribuciones o se recogerán más fotografías.

Las imágenes de prueba no se utilizarán para entrenar, ajustar umbrales ni escoger el modelo. Con solo 15 capturas, las métricas serán una evaluación didáctica inicial, no una demostración de generalización a cualquier anaquel o cámara.

## Qué no hacer

- No editar las fotografías originales.
- No aplicar filtros ni compresión adicional.
- No asociar un JSON si no corresponde exactamente a la distribución fotografiada.
- No repartir recortes de una misma captura entre entrenamiento y prueba.
- No asumir que una foto desenfocada o incompleta debe usarse para entrenar sin revisar su utilidad y etiqueta.

## Privacidad y Git

Las fotos originales, rectificadas y los recortes no se suben automáticamente a GitHub. Permanecen en la laptop del grupo. No fotografíes personas ni información personal.

Las etiquetas JSON y el manifiesto CSV contienen metadatos de las posiciones, no datos personales. La carpeta no debe contener datos personales.
