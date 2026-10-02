# Atlas animal · Mapa autoorganizado 3D

**[Abrir la aplicación](https://zoecrz.github.io/atlas-animal-som-3d/)**

Explora 45 animales con emojis animales propios, 20 características y 10 ecosistemas en un mapa 3D. Busca, filtra, gira el mapa, consulta parecidos, ajusta seis parámetros y agrega animales con sus 20 rasgos.

La aplicación funciona desde este enlace o desde un único archivo [index.html](index.html). No requiere instalar Python ni iniciar un servidor. Necesita internet para cargar Python y NumPy desde Pyodide; espera el mensaje **Listo para explorar y entrenar**.

El algoritmo de Kohonen y el cálculo de posiciones se ejecutan en Python dentro del navegador. Los módulos principales están disponibles aquí: [som.py](som.py), [browser_backend.py](browser_backend.py), [features.py](features.py) y [animal_validation.py](animal_validation.py). JavaScript presenta la interfaz y dibuja el cubo.

**[Descargar el proyecto completo](proyecto_som_3d.zip)**: incluye todas las fuentes, datos, la alternativa Streamlit, 47 pruebas automatizadas, instrucciones, documentación del algoritmo y una guía de demostración. Descomprime el ZIP y lee su README.md.

Los animales agregados se guardan en tu navegador. Usa **Guardar mis animales** e **Importar** para trasladarlos a otro equipo. Compartir el enlace conserva los 45 animales base; no comparte automáticamente tus animales guardados. Los cambios del entrenamiento no se conservan al recargar.

Se verificaron las 47 pruebas, el alta de un animal con 20 rasgos y el entrenamiento en Chrome. La URL pública cargó Python y completó un entrenamiento de 10 épocas en un cubo de 3 × 3 × 3. Los datos son categorías educativas aproximadas.
