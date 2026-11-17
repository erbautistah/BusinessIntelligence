# Tienda inteligente

Proyecto académico de la asignatura **Inteligencia de Negocios**.

El repositorio reúne los componentes que se desarrollarán para trabajar la Unidad 4: Machine Learning e Inteligencia Artificial.

## Objetivo

Construir y evaluar una solución empresarial didáctica que integre:

1. Machine Learning.
2. Visión por computadora.
3. Procesamiento de lenguaje natural.
4. Sistemas conversacionales.

## Componentes disponibles

### Generador de anaqueles

Aplicación web 2D con un anaquel de 4 filas × 8 columnas (32 posiciones), ocho productos ilustrados localmente, edición de espacios, escenarios controlados, resumen y exportaciones.

Instrucciones: [shelf-generator/README.md](shelf-generator/README.md).

### OpenCV y preparación del dataset

La primera etapa recibe una fotografía Android, rectifica la perspectiva y detecta posiciones ocupadas/vacías. También se incluye un procesador por lotes que rectifica 15 o más fotografías por grupo, recorta automáticamente las 32 posiciones y las etiqueta mediante el JSON emparejado. Incluye un comparador de detecciones con la referencia.

Instrucciones: [cv-lab/README.md](cv-lab/README.md).

**Límite actual:** la preparación de recortes ya está automatizada, pero todavía no clasifica las ocho categorías ni entrena un modelo ML. La selección de cuatro esquinas sigue siendo manual por fotografía.

## Estructura

- shelf-generator/: aplicación web del generador.
- cv-lab/: scripts y dependencias locales para visión por computadora.
- docs/: documentación técnica y decisiones del proyecto.
- labs/: materiales de los laboratorios (se incorporarán progresivamente).
- exam/: recursos y escenarios de evaluación (se incorporarán cuando corresponda).

## Requisitos y restricciones

- Herramientas gratuitas y, preferentemente, open source.
- Ejecución local siempre que sea posible.
- No depender de servicios externos de pago.
- Instrucciones reproducibles para Windows.
- El generador no necesita backend ni instalar bibliotecas.

## Estado

- **Generador de anaqueles:** prototipo funcional disponible.
- **OpenCV etapa 1:** rectificación y detección de ocupación disponibles; pendiente probar en distintos teléfonos y condiciones.
- **Clasificación de productos con ML:** siguiente etapa, después de reunir fotografías etiquetadas.
- **PLN y sistema conversacional:** pendientes de desarrollo.
