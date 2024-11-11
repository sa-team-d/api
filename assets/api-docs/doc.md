# Industry 5.0 RESTful API Documentation

**API Version**: 1.0 (OpenAPI 3.1)

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

## API Endpoints

### General Endpoints

#### Redirect to Swagger Docs
- **Endpoint**: `/docs`
- **Method**: `GET`
- **Description**: Redirects to the Swagger UI documentation page.
- **Response Codes**:
  - `200`: Successful redirection.

#### Redirect to ReDoc Docs
- **Endpoint**: `/redoc`
- **Method**: `GET`
- **Description**: Redirects to the ReDoc documentation page.
- **Response Codes**:
  - `200`: Successful redirection.

---

### Machine Endpoints

#### Get All Machines
- **Endpoint**: `/api/v1.0/machine/`
- **Method**: `GET`
- **Description**: Retrieves all machines in the dataset.
- **Response Codes**:
  - `200`: Successfully retrieved machine list.

#### Filter Machines by Type or Name
- **Endpoint**: `/api/v1.0/machine/filter`
- **Method**: `POST`
- **Description**: Filters machines based on `machine_name` or `machine_type`.
- **Parameters**:
  - `machine_name` (string, query): Name of the machine.
  - `machine_type` (string, query): Type of the machine.
- **Response Codes**:
  - `201`: Filter successful.
  - `422`: Validation error.

#### Get Machine by ID
- **Endpoint**: `/api/v1.0/machine/{machine_id}`
- **Method**: `GET`
- **Description**: Retrieves details of a machine by its ID.
- **Response Codes**:
  - `200`: Machine details retrieved.

---

### User Endpoints

#### Authenticate User
- **Endpoint**: `/api/v1.0/user/login`
- **Method**: `POST`
- **Description**: Authenticates a user and returns an ID token.
- **Parameters**:
  - `email` (string, query): User's email.
  - `password` (string, query): User's password.
- **Response Codes**:
  - `200`: Authentication successful.
  - `422`: Validation error.

#### List Users
- **Endpoint**: `/api/v1.0/user/list`
- **Method**: `GET`
- **Description**: Lists all users.
- **Response Codes**:
  - `200`: User list retrieved.

#### Filter Users by Name or Email
- **Endpoint**: `/api/v1.0/user/filter`
- **Method**: `POST`
- **Description**: Filters users based on `first_name`, `last_name`, or `email`.
- **Parameters**:
  - `first_name` (string, query): First name filter.
  - `last_name` (string, query): Last name filter.
  - `email` (string, query): Email filter.
- **Response Codes**:
  - `200`: Filter successful.
  - `422`: Validation error.

---

### KPI Endpoints

#### Get All KPIs
- **Endpoint**: `/api/v1.0/kpi/`
- **Method**: `GET`
- **Description**: Retrieves all KPIs.
- **Response Codes**:
  - `200`: KPI list retrieved.

#### Filter KPIs
- **Endpoint**: `/api/v1.0/kpi/filter`
- **Method**: `GET`
- **Description**: Filters KPIs by `kpi_name`, `start_date`, `end_date`, and `site_name`.
- **Parameters**:
  - `kpi_name` (string, query): Name of the KPI.
  - `start_date` (string, query): Start date.
  - `end_date` (string, query): End date.
  - `site_name` (string, query): Name of the site.
- **Response Codes**:
  - `200`: Filter successful.
  - `422`: Validation error.

#### Set KPI Threshold
- **Endpoint**: `/api/v1.0/kpi/threshold/`
- **Method**: `POST`
- **Description**: Sets a threshold value for a specified KPI.
- **Parameters**:
  - `kpi_name` (string, query): KPI name.
  - `threshold` (number, query): Threshold value.
- **Response Codes**:
  - `201`: Threshold set successfully.
  - `422`: Validation error.

---

### Report Endpoints

#### Create Report
- **Endpoint**: `/api/v1.0/report/`
- **Method**: `POST`
- **Description**: Creates and saves a new report in the database.
- **Parameters**:
  - `name` (string, query): Report name.
  - `site` (string, query): Site associated with the report.
  - `kpi` (string, query): KPI associated with the report.
  - `frequency` (string, query): Frequency of the report.
- **Response Codes**:
  - `201`: Report created successfully.
  - `422`: Validation error.

#### Get Reports by Site
- **Endpoint**: `/api/v1.0/report/filter`
- **Method**: `GET`
- **Description**: Retrieves all reports for a specific site.
- **Parameters**:
  - `site` (string, query): Name of the site.
- **Response Codes**:
  - `200`: Reports retrieved.
  - `422`: Validation error.

## Authentication & Security

The Industry 5.0 API relies on Firebase for handling authentication, ensuring secure access to endpoints based on user credentials and permissions.

## Contact
For any questions or issues, please contact the project maintainers:
- [Leonardo Stoppani](https://github.com/lilf4p)
- [Oleksiy Nedobiychuk](https://github.com/lesi-nedo)

---
