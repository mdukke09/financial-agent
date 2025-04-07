# Financial Agent - Microservicio de Asistente Financiero con IA

## Descripción

Financial Agent es un microservicio desarrollado en Python y Flask que implementa un chat de inteligencia artificial especializado en ayudar a los usuarios a establecer y gestionar metas financieras. El asistente mantiene conversaciones naturales para obtener información sobre las metas financieras del usuario y, una vez completada, almacena esta información en MongoDB.

## Características principales

- **Chat con IA**: Integración con modelos DeepSeek/OpenAI para mantener conversaciones naturales
- **Registro de metas financieras**: Captura y almacenamiento de información estructurada
- **Autenticación JWT**: Sistema seguro de autenticación y autorización
- **API RESTful**: Endpoints bien definidos con documentación automática
- **Persistencia en MongoDB**: Almacenamiento eficiente de metas y conversaciones
- **Dockerizado**: Fácil implementación en cualquier entorno

## Tecnologías

- **Backend**: Python 3.11, Flask 2.2.3
- **API**: Flask-Smorest, Marshmallow para validación y documentación
- **Base de datos**: MongoDB
- **Autenticación**: JWT (JSON Web Tokens)
- **IA**: DeepSeek API (compatible con OpenAI)
- **Contenedorización**: Docker

## Estructura del proyecto

```
financial-agent/
│
├── api/                            # Módulos de la API
│   ├── financial_agent/            # Módulo de agente financiero
│   │   ├── controllers.py          # Controladores para endpoints
│   │   ├── routes.py               # Definición de rutas
│   │   ├── schemas.py              # Esquemas de validación
│   │   └── services.py             # Lógica de negocio
│   └── auth/                       # Módulo de autenticación
│       ├── controllers.py          # Controladores para endpoints
│       ├── routes.py               # Definición de rutas
│       ├── schemas.py              # Esquemas de validación
│       └── services.py             # Lógica de negocio
│
├── config/                         # Configuración
│   └── settings.py                 # Variables de configuración
│
├── models/                         # Modelos de datos
│   ├── financial_goals.py          # Modelos para metas financieras
│   ├── users.py                    # Modelos de usuarios
│   └── blacklist.py                # Gestión de tokens revocados
│
├── utils/                          # Utilidades
│   ├── json_utils.py               # Utilidades para manejo de JSON
│   ├── middlewares/                # Middlewares
│   │   └── session_vars_middleware.py  # Middleware de sesión
│   └── prompt_templates.py         # Plantillas para IA
│
├── app.py                          # Punto de entrada de la aplicación
├── Dockerfile                      # Configuración de Docker
├── requirements.txt                # Dependencias
└── .env                            # Plantilla de variables de entorno
```

## Endpoints principales

### Agente Financiero

- `POST /api/financial-agent/chat`: Envía un mensaje al chat y recibe respuesta del asistente
- `GET /api/financial-agent/goals`: Obtiene todas las metas financieras del usuario
- `GET /api/financial-agent/goals/{goal_id}`: Obtiene una meta financiera específica
- `GET /api/financial-agent/conversation/{session_id}`: Obtiene el historial de una conversación

### Autenticación

- `POST /api/auth/register`: Registra un nuevo usuario
- `POST /api/auth/login`: Inicia sesión y obtiene tokens
- `POST /api/auth/refresh-token`: Refresca el token de acceso
- `POST /api/auth/logout`: Cierra la sesión (revoca el token)
- `GET /api/auth/me`: Obtiene la información del usuario actual

## Instalación y ejecución

### Prerrequisitos

- Docker y Docker Compose
- Cuenta y API key de DeepSeek o OpenAI
- MongoDB (local o Atlas)

### Configuración

1. Clona el repositorio:
   ```bash
   git clone https://github.com/mdukke09/financial-agent.git
   cd financial-agent
   ```

2. Crea un archivo `.env`.

3. Edita el archivo `.env` con tus propias credenciales:
   ```
   # Flask
   FLASK_APP=app.py
   APP_HOST=0.0.0.0
   APP_PORT=4000
   APP_DEBUG=False
   
   # DeepSeek API
   DEEPSEEK_API_KEY=tu_api_key_aqui
   DEEPSEEK_MODEL=deepseek-chat
   
   # MongoDB
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/dbname
   MONGODB_DATABASE=financial_goals_db
   
   # JWT
   JWT_SECRET_KEY=tu_clave_secreta_aleatoria
   JWT_ACCESS_TOKEN_EXPIRES=3600
   JWT_REFRESH_TOKEN_EXPIRES=2592000
   ```

### Ejecución

#### Con Docker

```bash
# Construir y ejecutar con Docker
docker build -t financial-agent .
docker run -p 4000:4000 --env-file .env --name financial-agent financial-agent
```

#### Comando combinado

```bash
docker build -t financial-agent .; docker rm -f financial-agent; docker run -p 4000:4000 --env-file .env --name financial-agent financial-agent
```

### Acceso

Una vez en ejecución, la API estará disponible en:
- API: `http://localhost:4000/api/`
- Documentación OpenAPI: `http://localhost:4000/swagger-ui`

## Uso del Servicio

### Ejemplo de conversación con el agente financiero

1. Inicia sesión para obtener un token JWT
2. Envía tu primer mensaje:

```json
POST /api/financial-agent/chat
{
  "message": "Hola, quiero ahorrar para un viaje",
  "session_id": "mi-sesion-1"
}
```

3. El asistente te guiará, preguntando detalles sobre tu meta
4. Cuando proporciones toda la información, el asistente creará la meta financiera

### Consulta de metas financieras

```json
GET /api/financial-agent/goals
```

Respuesta:
```json
{
  "success": true,
  "message": {
    "total": 1,
    "data": [
      {
        "id": "67ef9d221a19784f02b6b81b",
        "nombre": "Viaje a Cancún",
        "valor": 6000000.0,
        "tiempo": "8 meses",
        "descripcion": "Ahorro para vuelos, hotel, comidas y actividades",
        "categoria": "viajes",
        "fecha_creacion": "2025-04-04T00:00:00",
        "estado": "pendiente"
      }
    ]
  }
}
```

## Desarrollo

### Dependencias principales

```
flask==2.2.3
flask-smorest==0.42.0
flask-jwt-extended==4.5.2
flask-cors==4.0.0
marshmallow==3.19.0
pymongo==4.3.3
openai>=1.3.0
python-dotenv==1.0.0
gunicorn==20.1.0
bcrypt==4.0.1
```

### Extensión y Personalización

- **Nuevos endpoints**: Añade nuevos controladores en la carpeta `api/`
- **Personalización de prompts**: Modifica los prompts en `utils/prompt_templates.py`
- **Cambio de proveedor IA**: Ajusta la implementación en `services.py` para usar otro proveedor

## Contribución

1. Haz un fork del repositorio
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Haz commit de tus cambios: `git commit -am 'Añadir nueva funcionalidad'`
4. Empuja la rama: `git push origin feature/nueva-funcionalidad`
5. Envía un Pull Request

## Licencia

Este proyecto está licenciado bajo la licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Para preguntas o soporte, por favor contacta a [tu-email@ejemplo.com](mailto:tu-email@ejemplo.com).
