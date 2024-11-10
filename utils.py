description = """
## Installation
To install locally the API, clone the repository and install the dependencies using pip:
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
The API will be available at `http://localhost:8000/api/<api-version>`.

## Documentation
The API documentation is available at `http://localhost:8000/api/<api-version>/docs` as a Swagger UI interface. The documentation provides information about the available endpoints, request and response formats, and examples. For an alternative view, the API documentation is also available at `http://localhost:8000/api/<api-version>/redoc`.

## Plugins
The API is organized in plugins, each containing a set of endpoints related to a specific functionality. The available plugins are:
- `kpi`: Get all KPIs available, filter KPIs by name, and set thresholds
- `machine`: Get all machines, filter machines by category, and get machine details
- `user`: Users management
- `report`: Generate and manage reports

## Contact
For any questions or issues, please contact the project maintainers:
- [Leonardo Stoppani](https://github.com/lilf4p)
- [Oleksiy Nedobiychuk](https://github.com/lesi-nedo)
"""