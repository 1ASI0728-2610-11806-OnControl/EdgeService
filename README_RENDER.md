# EdgeService - Render Deploy

Servicio Flask para recibir datos del ESP32/Wokwi y exponer el ultimo dato a la demo frontend.

## Build command

```sh
pip install -r requirements.txt
```

## Start command

```sh
gunicorn app:app --bind 0.0.0.0:$PORT
```

## Variables de entorno

```env
PORT=5000
DEVICE_ID=smart-band-001
DEVICE_API_KEY=oncontrol-grupo2-demo-key
CORS_ORIGINS=http://localhost:3000,https://TU-FRONTEND.vercel.app
```

Opcional para desarrollo:

```env
FLASK_ENV=development
```

## Endpoints de verificacion

```powershell
curl https://TU-EDGESERVICE.onrender.com/status

curl -X POST https://TU-EDGESERVICE.onrender.com/OnControl/parameters `
  -H "Content-Type: application/json" `
  -H "X-API-Key: oncontrol-grupo2-demo-key" `
  -d "{\"device_id\":\"smart-band-001\",\"bpm\":82,\"temp\":36.8,\"spo2\":97}"

curl https://TU-EDGESERVICE.onrender.com/OnControl/parameters/latest-demo
```

## Wokwi

En `OnControlESP32/sketch_nov26b.ino`, usar como `API_URL` la URL base de Render:

```cpp
const char* API_URL = "https://TU-EDGESERVICE.onrender.com";
```

El sketch agrega `/OnControl/parameters` automaticamente.
