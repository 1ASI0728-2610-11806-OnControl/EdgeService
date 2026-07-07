
# Smart Band Edge Service (smart_band_edge_service)

## Overview

Smart Band Edge Service is a Python-based application for processing and analyzing data from smart wearable devices at the edge. It provides real-time data collection, device authentication, and RESTful APIs for health monitoring and activity tracking.

## Features

- Real-time data ingestion from smart bands
- Device authentication and management
- RESTful API for data access and control
- Edge processing and analytics
- Configurable data storage (SQLite)
- Easy integration with cloud or local systems

## Dependencies

- Python 3.13 or higher
- Flask (web framework)
- Peewee (ORM for SQLite)
- python-dateutil (date and time handling)

## Domain-Driven Design (DDD) Structure

The project follows a Domain-Driven Design (DDD) approach, distributing the features in two main bounded contexts:
- **Health Monitoring**: Manages health-related data from smart bands, including heart rate, steps, and sleep patterns.
- **Identity and Access Management**: Handles device authentication.

Inside each bounded context, code is organized into distinct layers:
- **Domain**: Contains core business logic and domain models.
- **Application**: Contains application services and use cases.
- **Infrastructure**: Contains data access, external service integrations, and configurations.
- **Interfaces**: Contains API controllers and user interfaces.

## Documentation

For detailed documentation, refer to the [docs](docs) directory. It includes:
- **Class Diagrams**: The file [docs/class-diagram.puml](docs/class-diagram.puml) contains the visual representation of the domain-driven packages, classes, and their relationships in PlantUML DSL.

## Usage

### Start the Service

```sh
python app.py
```

The service will initialize the database and create a test device on the first run.

### API Endpoints

Current demo endpoints:

- `GET /status` - Service health check.
- `POST /OnControl/parameters` - Ingest smart band data from a device.
- `GET /OnControl/parameters/latest-demo` - Latest demo reading without JWT.

Refer to the code-level documentation for full details.

## Demo academica IoT

Arquitectura de la demo:

```text
Wokwi / ESP32 -> EdgeService Flask -> Frontend Next.js
```

Deploy recomendado:

- Frontend: Vercel
- EdgeService: Render
- Backend principal: Render
- Wokwi: simulador online

### Variables de entorno

EdgeService:

```env
FLASK_ENV=development
PORT=5000
DEVICE_ID=smart-band-001
DEVICE_API_KEY=oncontrol-grupo2-demo-key
CORS_ORIGINS=http://localhost:3000,https://TU-FRONTEND.vercel.app
```

Frontend:

```env
NEXT_PUBLIC_API_URL=https://TU-BACKEND-PRINCIPAL.onrender.com
NEXT_PUBLIC_EDGE_API_URL=https://TU-EDGESERVICE.onrender.com
```

### Levantar EdgeService localmente

```powershell
python -m pip install -r requirements.txt
$env:FLASK_ENV="development"
$env:PORT="5000"
$env:DEVICE_ID="smart-band-001"
$env:DEVICE_API_KEY="oncontrol-grupo2-demo-key"
$env:CORS_ORIGINS="http://localhost:3000"
python app.py
```

### Endpoints de la demo

- `GET /status`: health check publico.
- `POST /OnControl/parameters`: recibe datos del dispositivo con header `X-API-Key`.
- `GET /OnControl/parameters/latest-demo`: devuelve el ultimo dato del dispositivo demo sin JWT.

### Criterios de riesgo

`is_critical` es `true` si ocurre cualquiera de estos casos:

- BPM menor a 50 o mayor a 120.
- Temperatura menor a 35.5 o mayor a 38.0.
- SpO2 menor a 92.

### Pruebas curl en PowerShell

```powershell
curl http://localhost:5000/status

curl -X POST http://localhost:5000/OnControl/parameters `
  -H "Content-Type: application/json" `
  -H "X-API-Key: oncontrol-grupo2-demo-key" `
  -d "{\"device_id\":\"smart-band-001\",\"bpm\":82,\"temp\":36.8,\"spo2\":97}"

curl http://localhost:5000/OnControl/parameters/latest-demo
```

### Prueba local completa

1. Levantar EdgeService.
2. Probar `/status`.
3. Enviar un POST a `/OnControl/parameters`.
4. Probar `/OnControl/parameters/latest-demo`.
5. Levantar el frontend con `NEXT_PUBLIC_EDGE_API_URL=http://localhost:5000`.
6. Abrir el dashboard del paciente y verificar la card de signos vitales demo.
7. Configurar Wokwi con la URL publica del EdgeService si se prueba online.

### Evidencias para exposicion

- Captura de Wokwi con los 3 potenciometros.
- Captura del Serial Monitor con HTTP 200 o 201.
- Captura de logs de EdgeService recibiendo POST.
- Captura de `/OnControl/parameters/latest-demo`.
- Captura del frontend mostrando BPM, temperatura y SpO2.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

