# Generador de anaqueles 2D

Aplicación web local para construir escenarios visuales de exhibición en el proyecto académico **Tienda inteligente**.

## Requisitos

- Windows, macOS o Linux.
- Navegador moderno.
- Python 3 para iniciar un servidor HTTP local. No se instalan paquetes.

## Ejecutar en Windows

Desde PowerShell:

```powershell
git clone https://github.com/mfernando25/tienda-inteligente.git
cd tienda-inteligente/shelf-generator
python -m http.server 8000
```

Abrir http://localhost:8000. Para detener el servidor, pulsa `Ctrl+C` en PowerShell.

## Funcionalidades

- Anaquel 2D de 4 filas × 8 columnas (32 posiciones).
- Catálogo local de ocho productos SVG.
- Asignar, reemplazar o retirar productos de una posición.
- Cuatro escenarios controlados: equilibrado, faltantes, completo y predominio de bebidas.
- Distribución aleatoria y opción para vaciar el anaquel.
- Indicadores: espacios ocupados, vacíos, variedad, porcentaje de ocupación y valor referencial de exhibición.
- Modo captura para fotografiar el anaquel desde Android.
- Exportación de imagen PNG, metadatos JSON y datos por posición CSV.

## Exportaciones

Los archivos comparten un nombre base con escenario y fecha:
- **PNG:** imagen de referencia del anaquel en alta resolución.
- **JSON:** escenario, catálogo, posición de cada producto, supuestos e indicadores.
- **CSV:** una fila por posición, incluyendo las posiciones vacías.

El JSON y el CSV funcionan como referencia de verdad (*ground truth*) para comparar posteriormente los resultados de visión por computadora. No contienen datos de estudiantes.

## Interpretación de los datos

Cada celda es una posición de exhibición (*facing*). El simulador considera un producto visible por posición ocupada. Por ello, el valor referencial suma los precios unitarios de los espacios ocupados.

**El conteo de posiciones no equivale al stock total de almacén ni a unidades disponibles fuera del anaquel.** Los precios son ilustrativos y no representan precios comerciales reales.

## Limitaciones actuales

- Las ilustraciones son controladas y simples; no representan fotografías reales de empaques.
- El catálogo visual contiene ocho clases conocidas. No es un detector genérico de cualquier producto.
- El simulador no incluye OpenCV, entrenamiento ML, promociones ni chatbot.
- Los escenarios no se guardan automáticamente entre sesiones; se recomienda exportar JSON/CSV cuando se necesite conservarlos.
- El modo captura solo presenta la vista limpia. La fotografía se toma desde el dispositivo Android.
- La exportación PNG se genera en el navegador mediante SVG y Canvas; requiere abrir la aplicación a través del servidor HTTP local.

## Prueba sugerida

1. Generar cada escenario controlado.
2. Comprobar que los conteos coincidan con el escenario elegido.
3. Modificar manualmente varias posiciones y verificar el estado personalizado.
4. Descargar PNG, JSON y CSV.
5. Comparar los productos visibles en PNG con las 32 filas del CSV.
6. Abrir el modo captura y comprobar que el anaquel se vea completo en pantalla.
