# Generador de anaqueles 2D

Primera versión funcional del simulador didáctico.

## Requisitos

- Windows, macOS o Linux.
- Navegador moderno.
- Python 3 para iniciar un servidor HTTP local (no se instalan paquetes).

## Ejecutar en Windows

1. Clona el repositorio.
2. Abre PowerShell en la carpeta `shelf-generator`.
3. Ejecuta:

```powershell
python -m http.server 8000
```

4. Abre en el navegador: http://localhost:8000
5. Para detener el servidor, vuelve a PowerShell y pulsa `Ctrl+C`.

> Se recomienda iniciar un servidor local en lugar de abrir `index.html` directamente, porque el navegador puede restringir la carga del archivo SVG externo cuando se utiliza el protocolo `file://`.

## Funciones incluidas

- Anaquel 2D de 4 filas × 8 columnas (32 espacios).
- Catálogo local de ocho productos ilustrados en SVG.
- Selección de un espacio y asignación, reemplazo o retiro de producto.
- Generación aleatoria de una distribución.
- Limpieza completa del anaquel.
- Resumen de espacios ocupados y vacíos por producto.
- Modo captura para ocultar controles y fotografiar el anaquel desde un dispositivo Android.

## Alcance y limitaciones

Esta aplicación solo genera una exhibición visual. El resumen cuenta espacios ocupados por categoría; **no representa el inventario real de una tienda**. Los precios son datos ilustrativos asociados a cada producto.

La aplicación todavía no incorpora OpenCV, reconocimiento de productos, Machine Learning, promociones ni persistencia de escenarios. Esos componentes se definirán y probarán por separado.
