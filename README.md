
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

- `GET /status` — Service health check (_to be implemented_)
- 'POST /api/v1/health-monitoring/health-records' — Ingest smart band data



Refer to the code-level documentation for full details.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

