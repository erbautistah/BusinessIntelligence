# Validación de captura del anaquel con Android

## Objetivo

Comprobar si una fotografía tomada con un celular Android a la pantalla que muestra el generador conserva suficiente información visual para procesar los 32 espacios y reconocer las ocho clases del catálogo.

Esta prueba valida la calidad de la imagen. **Todavía no valida el método de reconocimiento ni la conectividad de transferencia entre las redes de la universidad.**

## Preparación

1. Actualizar el repositorio:
   ```powershell
   git pull
   ```
2. Iniciar el generador desde `shelf-generator`:
   ```powershell
   python -m http.server 8000
   ```
3. Abrir `http://localhost:8000`.
4. Seleccionar el escenario **Exhibición equilibrada** y pulsar **Aplicar escenario**.
5. Confirmar los valores esperados:
   - 28 espacios ocupados.
   - 4 espacios vacíos.
   - Agua mineral: 4.
   - Leche entera: 4.
   - Gaseosa: 4.
   - Jugo de naranja: 4.
   - Galletas: 3.
   - Cereal: 3.
   - Conserva: 3.
   - Detergente: 3.

## Archivos que se deben obtener

### 1. PNG original

Pulsar **Descargar imagen PNG**. No editar, recortar ni volver a guardar este archivo.

### 2. JSON de referencia

Pulsar **Datos JSON**. Este archivo contiene la distribución conocida de cada posición y se utilizará como referencia (*ground truth*).

### 3. Fotografía real con Android

1. Activar **Modo captura** en la aplicación.
2. Mostrar el anaquel completo en el monitor.
3. Colocar el celular aproximadamente frente al centro de la pantalla, con la cámara principal a 1×.
4. Desactivar el flash y evitar reflejos de luces.
5. Procurar que los cuatro bordes del anaquel sean visibles en la fotografía.
6. Tocar la zona central del anaquel para enfocar y tomar una fotografía.
7. Conservar el archivo JPG original, sin enviarlo por aplicaciones que reduzcan su resolución ni aplicarle filtros.

Para esta primera prueba, tomar una fotografía frontal. No intentar corregir perspectiva ni mejorar la imagen manualmente.

## Qué se evaluará

- ¿Se distinguen los límites de las 32 posiciones?
- ¿Se puede localizar cada producto sin que se confunda con los espacios vecinos?
- ¿Las ilustraciones conservan sus colores y formas?
- ¿Los nombres y precios se leen? Esto es secundario para la primera prueba de reconocimiento visual.
- ¿Hay reflejos, bandas, patrones de pantalla, desenfoque o perspectiva pronunciada?
- ¿La fotografía contiene el anaquel completo?

## Entrega para revisión

Compartir estos tres archivos:

- `anaquel-...png`: PNG generado por la aplicación.
- `anaquel-...json`: distribución de referencia.
- `foto-android.jpg`: fotografía real de la pantalla.

No subir datos personales ni fotografías de personas.

## Importante: qué no concluir todavía

- Que el PNG original se vea bien no demuestra que la fotografía móvil sea adecuada.
- Una buena fotografía no demuestra que un modelo reconozca los productos.
- El resumen del generador cuenta posiciones de exhibición, no existencias físicas de almacén.
- La transferencia mediante un servicio compartido (por ejemplo, Drive) se probará por separado. Para esta validación basta con que los tres archivos lleguen al equipo que realizará el análisis.

La siguiente decisión técnica se tomará después de inspeccionar la fotografía real junto con su PNG y JSON de referencia.
