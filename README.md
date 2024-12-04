# 🎬 Netflix Pocho

Un clon simple y estilizado de Netflix que permite navegar por películas y series, agregar a una lista personalizada y buscar contenido con integración de la API de TMDB.

## 🚀 Funcionalidades

- **Películas y series**: Explora una selección de películas y series populares.
- **Búsqueda dinámica**: Encuentra contenido específico utilizando el buscador.
- **Lista personalizada**: Añade o elimina contenido de tu lista de favoritos.
- **Sistema de autenticación**: Registro e inicio de sesión con formularios estilizados.
- **Detalles interactivos**: Haz clic en cualquier título para ver más información.

## 🛠️ Tecnologías

- **Framework**: Django
- **Frontend**: HTML5, CSS3 (con animaciones y diseño personalizado)
- **API**: TMDB (The Movie Database)

## ⚙️ Instrucciones para ejecutar el proyecto

1. **Clona el repositorio**  
   `git clone <URL-del-repositorio>`

2. **Accede al directorio del proyecto**  
   `cd netflix-clone`

3. **Crea un entorno virtual (opcional, pero recomendado)**  
   `python -m venv venv`  
   `source venv/bin/activate` (en Mac/Linux)  
   `venv\Scripts\activate` (en Windows)

4. **Instala las dependencias**  
   `pip install -r requirements.txt`

5. **Configura las variables de entorno**  
   - Crea un archivo `.env` en la raíz del proyecto.  
   - Añade tu clave de API de TMDB:  
     `TMDB_API_KEY=<tu_api_key>`

6. **Realiza las migraciones de la base de datos**  
   `python manage.py makemigrations`  
   `python manage.py migrate`

7. **Rellena la base de datos con contenido inicial**  
   Entra en el shell de Django:  
   `python manage.py shell`  
   Ejecuta:  
   - `from streaming.views import populate_movies, populate_series`  
   - `populate_movies()`  
   - `populate_series()`

8. **Inicia el servidor de desarrollo**  
   `python manage.py runserver`

9. **Accede al proyecto**  
   Abre tu navegador y ve a `http://127.0.0.1:8000`.

## 🌟 Notas
