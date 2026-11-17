# Arquitectura inicial del proyecto

## Contexto

El proyecto se desarrollará para la Unidad 4 de Inteligencia de Negocios. Los equipos trabajarán en grupos de 4 a 7 estudiantes y mantendrán los mismos integrantes durante los dos laboratorios y el examen práctico.

Cada clase dispone de 3 horas: 90 minutos de teoría y 90 minutos de laboratorio.

## Restricciones conocidas

- Las PC del laboratorio tienen Windows y Deep Freeze; los cambios locales no persisten al reiniciar.
- Al menos una persona por grupo dispone de una laptop con Windows, Python y Git instalados. Ese equipo será el espacio persistente del grupo.
- Los celulares utilizados para la captura serán Android.
- La red Wi-Fi académica de los celulares se considera aislada de la red cableada de las PC del laboratorio.
- No se diseñará transferencia directa celular–PC entre esas redes.
- Se considera un almacenamiento compartido accesible por Internet como posible puente para transferir imágenes. La disponibilidad del servicio aún debe comprobarse.
- El procesamiento se priorizará localmente.
- No se dependerá de APIs ni servicios externos de pago.

## Primer componente: generador de anaqueles

Se propone una aplicación web 2D sencilla, ejecutable localmente, que muestre un único anaquel.

Dimensión inicial propuesta: 4 filas por 8 columnas (32 espacios). Es una propuesta de diseño, no una decisión técnica validada todavía.

Funciones candidatas:
- Mostrar productos en celdas del anaquel.
- Cambiar, agregar o retirar productos.
- Mostrar información comercial asociada a cada producto.
- Configurar precios y promociones cuando se defina el modelo de datos.
- Generar una imagen PNG del anaquel para usarla como entrada en el laboratorio.

Se evitará ampliar el alcance a una tienda completa, navegación 3D, inventario transaccional o backend innecesario.

## Separación entre práctica y evaluación

La intención es reutilizar el generador, pero diferenciar:
- Catálogo y escenario didáctico de los laboratorios.
- Catálogo y reglas comerciales del examen práctico.

No se debe asumir que un modelo de visión reconocerá automáticamente productos nuevos. El método de reconocimiento, las clases y los datos de entrenamiento/prueba deberán definirse y probarse antes del laboratorio.

## Pendientes antes de implementar

1. Definir cómo serán representados visualmente los productos: imágenes reales, ilustraciones o etiquetas/códigos visuales.
2. Elegir un método de reconocimiento viable y comprobarlo con fotografías reales de pantallas de celular.
3. Definir catálogo y metadatos: SKU, nombre, categoría, precio, stock visible y promociones.
4. Probar el proceso de captura Android → almacenamiento compartido → descarga en laptop.
5. Verificar resolución, perspectiva, reflejos y legibilidad al fotografiar la pantalla del anaquel.
6. Definir criterios de aceptación del generador antes de añadir componentes de ML, PLN o chatbot.

## Principio de desarrollo

Construir en incrementos pequeños y verificables. Primero debe funcionar el generador de anaqueles; después se integrarán los componentes de visión, ML, PLN y sistemas conversacionales.
