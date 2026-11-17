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

### Alcance acordado

- Aplicación web 2D sencilla que muestra un único anaquel.
- Distribución de 4 filas por 8 columnas (32 espacios).
- Catálogo inicial de ocho productos ilustrados mediante recursos SVG locales.
- Seleccionar un espacio y asignar, reemplazar o retirar el producto.
- Generar una distribución aleatoria o vaciar el anaquel.
- Mostrar un resumen de espacios ocupados y vacíos por categoría.
- Activar un modo de captura que oculta los controles para fotografiar el anaquel desde Android.
- Sin backend, base de datos, frameworks ni dependencias externas.

### Implementación disponible

Ubicación: `shelf-generator/`.

Para ejecutarlo en Windows:
1. Abrir PowerShell en la carpeta `shelf-generator`.
2. Ejecutar `python -m http.server 8000`.
3. Abrir `http://localhost:8000` en el navegador.

Se utiliza un servidor HTTP local porque algunos navegadores restringen la carga de SVG externos al abrir el HTML directamente mediante `file://`.

### Límites del prototipo

- El resumen cuenta espacios de exhibición, no inventario real ni unidades físicas en bodega.
- Los precios son ilustrativos.
- Todavía no incluye promociones ni reglas comerciales.
- Todavía no incorpora OpenCV, reconocimiento de productos ni modelos de ML.
- La aplicación no guarda escenarios entre sesiones; la persistencia se definirá si resulta necesaria.
- El modo captura prepara la visualización, pero no toma ni transfiere fotografías.

## Separación entre práctica y evaluación

La intención es reutilizar la arquitectura del generador, pero diferenciar el catálogo y los requerimientos del laboratorio y del examen práctico.

No se debe asumir que un modelo de visión reconocerá automáticamente productos nuevos. El método de reconocimiento, las clases y los datos de entrenamiento/prueba deberán definirse y probarse antes del laboratorio.

## Pendientes técnicos y didácticos

1. Probar la legibilidad del anaquel al fotografiar una pantalla con distintos celulares Android.
2. Definir el proceso de transferencia de las fotografías mediante un almacenamiento compartido accesible desde el Wi-Fi académico y la red cableada.
3. Evaluar distorsión de perspectiva, reflejos, resolución y patrones de pantalla.
4. Elegir un método de visión por computadora realista para 90 minutos y comprobarlo con las fotografías.
5. Definir los datos de entrenamiento/prueba y las clases de productos.
6. Decidir cómo ML utilizará los resultados visuales para producir una clasificación o predicción empresarial.
7. Diseñar los componentes de PLN y sistemas conversacionales para que consuman datos del mismo caso de negocio.

## Principio de desarrollo

Construir en incrementos pequeños y verificables. El generador debe probarse primero con dispositivos reales; después se integrarán visión por computadora, ML, PLN y sistemas conversacionales.
