# RESTful API for Industry 5.0
This repository contains the code for the RESTful API for Industry 5.0 and is part of the Smart Application Course Project at UNIPI A.Y. 2024/25. The API is built using FastAPI and implements all the necessary endpoints to interact with the Industry 5.0 system.

## Design
The API is designed following the RESTful principles and uses FastAPI to implement the endpoints. The API is organized in plugins, each containing a set of endpoints related to a specific functionality. The plugins are modular and can be easily extended or modified to add new features or change the existing ones. The API uses Pydantic models to define the request and response formats for the endpoints and provides automatic validation and serialization of the data. The API documentation is generated automatically from the code and provides information about the available endpoints, request and response formats, and examples.

<p align="center">
	<img src="assets/api-docs/API-arch.svg" alt="API Design" width="60%"/>
</p>

All the system components communicate through the API Layer, that ensure consistency and security of the data exchanged.
## Installation
To install the API, clone the repository and install the dependencies using pip:
```bash
git clone https://github.com/sa-team-d/api.git
cd api
pip install -r requirements.txt
```

## Usage
To start the API locally, run the following command:
```bash
uvicorn main:app --reload
```
or use the FastAPI command for development:
```bash
fastapi dev main.py
```
The API will be available at `http://localhost:8000`.

## Documentation

The API documentation is available at `http://localhost:8000/docs` as a Swagger UI interface. The documentation provides information about the available endpoints, request and response formats, and examples. For an alternative view, the API documentation is also available at `http://localhost:8000/redoc`.

## Plugins
The API is organized in plugins, each containing a set of endpoints related to a specific functionality. The available plugins are:
- `kpi`: Key Performance Indicators
- `machine`: Machines
- `user`: Users
- `TODO`: Add new plugins

## Contact
For any questions or issues, please contact the project maintainers:
- [Leonardo Stoppani](https://github.com/lilf4p)
- [Oleksiy](https://github.com/lesi-nedo)

