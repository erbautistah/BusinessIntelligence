# Tienda inteligente

Proyecto académico de la asignatura **Inteligencia de Negocios**.

El repositorio reúne los componentes de la Unidad 4: Machine Learning, visión por computadora, procesamiento de lenguaje natural y sistemas conversacionales.

## Componentes

### Generador de anaqueles
Aplicación web local 2D con un anaquel de 4 filas × 8 columnas, ocho productos ilustrados, escenarios controlados, edición manual y exportaciones PNG, JSON y CSV.

Instrucciones: [shelf-generator/README.md](shelf-generator/README.md).

### Visión por computadora y Machine Learning
El proyecto incluye:
- Rectificación de perspectiva y detección inicial de posiciones ocupadas/vacías mediante reglas HSV.
- Preparación por lotes de fotografías Android, con 32 recortes por captura y etiquetas procedentes del JSON de referencia.
- Primer clasificador multiclase HOG + SVM, con separación por fotografía, métricas por clase, matrices de confusión y registro de errores.

Instrucciones: [cv-lab/README.md](cv-lab/README.md).

**Límite actual:** el clasificador se entrena con ocho ilustraciones de productos y una clase empty. Esta primera línea base no demuestra que pueda reconocer empaques comerciales reales.

## Estructura

- shelf-generator/: aplicación web del generador.
- cv-lab/: scripts OpenCV, preparación del dataset y entrenamiento ML.
- docs/: documentación técnica y decisiones del proyecto.
- labs/: materiales de laboratorio.
- exam/: recursos de evaluación.

## Requisitos y restricciones

- Herramientas gratuitas y preferentemente open source.
- Ejecución local siempre que sea posible.
- Sin dependencia de servicios externos de pago.
- Instrucciones reproducibles para Windows.

## Estado

- **Generador de anaqueles:** prototipo funcional.
- **Dataset CV:** 15 fotografías y 480 recortes preparados localmente.
- **Clasificación ML:** primera implementación HOG + SVM incorporada; pendiente ejecutar con el dataset local y analizar los errores reales.
- **Nuevo generador de diseños:** siguiente etapa, para evaluar generalización ante diseños visuales que el modelo no vio durante el entrenamiento.
- **PLN y sistema conversacional:** pendientes.
