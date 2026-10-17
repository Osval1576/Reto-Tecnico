# Seguimiento de incidencias

App web para registrar incidencias reportadas por usuarios, consultarlas, filtrarlas y cambiar su estado.

- **Backend:** Django 6.1 + Django REST Framework (API REST en `/api/`)
- **Frontend:** Vue 3 + Vite (una sola vista, `frontend/src/App.vue`)
- **Persistencia:** SQLite en local; PostgreSQL en producción vía `DATABASE_URL`

## Funcionalidad

| Requisito | Dónde |
|---|---|
| Registrar incidencia con prioridad **alta / media / baja** | Formulario → `POST /api/incidencias/` |
| Estado **nuevo / en proceso / resuelto** (toda incidencia nace como `nuevo`) | `Incidencia.Estado` en `backend/incidencias/models.py` |
| Mostrar incidencias registradas (más recientes primero) | Lista → `GET /api/incidencias/` |
| Cambiar el estado | Selector de cada tarjeta → `PATCH /api/incidencias/<id>/` |
| Filtrar por estado y/o prioridad | Filtros → `GET /api/incidencias/?estado=&prioridad=` |
| Validar datos indispensables | En el cliente (`validar()` en `App.vue`) **y** en el servidor (`IncidenciaSerializer`) |
| Persistencia durable | Base de datos relacional con migraciones de Django |

## Requisitos

- Python 3.12 o superior (probado con 3.14)
- Node.js 22.18+ o 24.12+

## Ejecutar en local

Se necesitan dos terminales: una para el backend y otra para el frontend.

### 1. Backend (http://127.0.0.1:8000)

```bash
cd backend
python -m venv venv
# Windows:      venv\Scripts\activate
# Linux/macOS:  source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # opcional en local: sin .env usa valores de desarrollo
python manage.py migrate
python manage.py runserver
```

Opcional: `python manage.py createsuperuser` para entrar al admin en http://127.0.0.1:8000/admin/.

### 2. Frontend (http://localhost:5173)

```bash
cd frontend
npm install
npm run dev
```

Vite redirige las peticiones a `/api` hacia `http://127.0.0.1:8000` (ver `frontend/vite.config.js`), así que no hace falta configurar CORS.

## Pruebas

```bash
# Backend: API, validaciones y filtros
cd backend
python manage.py test incidencias

# Frontend: componente App con la API simulada
cd frontend
npx vitest run
```

## API

Base: `/api/incidencias/`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/incidencias/` | Lista. Filtros opcionales `estado` y `prioridad` |
| POST | `/api/incidencias/` | Crea. Requiere `titulo` (máx. 150), `descripcion` y `prioridad` |
| GET | `/api/incidencias/<id>/` | Detalle |
| PATCH | `/api/incidencias/<id>/` | Actualización parcial, p. ej. `{"estado": "resuelto"}` |

Valores válidos:

- `prioridad`: `baja`, `media`, `alta`
- `estado`: `nuevo`, `en_proceso`, `resuelto`

Ejemplo:

```bash
curl -X POST http://127.0.0.1:8000/api/incidencias/ \
  -H "Content-Type: application/json" \
  -d '{"titulo": "No carga el login", "descripcion": "Pantalla en blanco", "prioridad": "alta"}'
```

Una petición inválida responde `400` con los errores de cada campo, que el frontend muestra debajo del input correspondiente:

```json
{"titulo": ["El título es obligatorio."], "prioridad": ["Prioridad no válida."]}
```

Un filtro con un valor desconocido (`?estado=cerrado`) también responde `400`, en lugar de devolver una lista vacía.

## Decisiones

- **Un solo servicio en producción.** Django sirve la API y el build de Vue (`frontend/dist`) con WhiteNoise. Así el front y la API comparten origen y no hacen falta CORS ni dos despliegues.
- **El estado inicial lo fija el servidor.** Aunque el cliente mande `estado` al crear, se guarda como `nuevo`.
- **Sin borrado.** La API solo acepta GET, POST y PATCH; el reto no pide eliminar incidencias.
- **Filtros sin dependencias extra.** Son dos campos con valores cerrados, así que se validan a mano en `get_queryset` en lugar de agregar `django-filter`.
- **Cambio de estado optimista.** La vista se actualiza al momento y vuelve al valor anterior si la API falla.

## Despliegue

Despliegue actual:

- **Frontend:** Vercel, con Root Directory `frontend`. → https://reto-tecnico-one.vercel.app
- **Backend:** Render. → https://reto-tecnico-1j5t.onrender.com/api/incidencias/

El front llama a la ruta relativa `/api`. En Vercel, `frontend/vercel.json` reenvía `/api/*` al backend de Render, así que no hace falta CORS ni cambiar la URL de la API por entorno. Si cambia el dominio de Render, hay que actualizarlo en ese archivo.

El dominio `*.onrender.com` se agrega solo a `ALLOWED_HOSTS` mediante la variable `RENDER_EXTERNAL_HOSTNAME`, que define Render.

Como alternativa, todo puede ir en un solo servicio de Render. El repositorio incluye `build.sh`, que compila el frontend, instala dependencias, ejecuta `collectstatic` y aplica migraciones; Django sirve entonces también el build de Vue. Configuración (Web Service con runtime Python):

| Campo | Valor |
|---|---|
| Build command | `bash build.sh` |
| Start command | `gunicorn --chdir backend config.wsgi:application` |

Variables de entorno:

| Variable | Ejemplo |
|---|---|
| `SECRET_KEY` | una clave nueva y aleatoria (obligatoria con `DEBUG=False`) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `incidencias.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://incidencias.onrender.com` |
| `DATABASE_URL` | URL de PostgreSQL que da la plataforma |
| `NODE_VERSION` | `24.12.0` (si la plataforma no trae una versión compatible) |

Con `DEBUG=False` se activan la redirección a HTTPS, las cookies seguras, HSTS y los archivos estáticos comprimidos. Antes de desplegar se puede revisar con:

```bash
cd backend
DEBUG=False SECRET_KEY=x python manage.py check --deploy
```

## Estructura

```
backend/
  config/            settings, urls raíz, wsgi
  incidencias/       modelo, serializer, viewset, urls, tests
frontend/
  src/App.vue        vista única: formulario, filtros y lista
  src/services/api.js  llamadas a la API con axios
build.sh             build para producción
```
