# Industry 5.0 API Documentation

## Overview

The Industry 5.0 API is a RESTful API designed to manage and monitor machines, users, and KPIs (Key Performance Indicators) within an industrial setup. It enables operations such as listing, filtering, adding, updating, and deleting entities in the dataset.

This API leverages the following technologies:
- **FastAPI**: A Python-based framework for building APIs, selected for its high performance and ease of use.
- **Firebase**: Firebase manages authentication and security mechanisms, ensuring secure access and data protection.

## API Endpoints

### General

#### Redirect to Swagger Docs
- **Endpoint**: `/api/v1/`
- **Method**: `GET`
- **Description**: Redirects to the API documentation on Swagger UI.
- **Response Codes**:
  - `200`: Successful redirection.

---

### Machine Endpoints

#### Get All Machines
- **Endpoint**: `/api/v1/machine/`
- **Method**: `GET`
- **Description**: Retrieves a list of all machines in the dataset.
- **Response Codes**:
  - `201`: Successfully retrieved the machine list.

#### Filter Machines by Type
- **Endpoint**: `/api/v1/machine/filter`
- **Method**: `POST`
- **Description**: Filters machines based on the specified `machine_type`.
- **Parameters**:
  - `machine_type` (string, query): The type of machine to filter by.
- **Response Codes**:
  - `201`: Successfully retrieved the filtered list.
  - `422`: Validation error.

#### Get Machine by ID
- **Endpoint**: `/api/v1/machine/{machine_id}`
- **Method**: `GET`
- **Description**: Retrieves details for a specific machine by its `machine_id`.
- **Parameters**:
  - `machine_id` (string, path): The ID of the machine.
- **Response Codes**:
  - `201`: Successfully retrieved machine data.
  - `422`: Validation error.

---

### User Endpoints

#### Login
- **Endpoint**: `/api/v1/user/login`
- **Method**: `POST`
- **Description**: Authenticates the user and returns an ID token.
- **Parameters**:
  - `email` (string, query): User's email address.
  - `password` (string, query): User's password.
- **Response Codes**:
  - `200`: Login successful.
  - `422`: Validation error.

#### List Users
- **Endpoint**: `/api/v1/user/list`
- **Method**: `GET`
- **Description**: Retrieves a list of all users.
- **Response Codes**:
  - `200`: Successfully retrieved the user list.

#### Get Current User
- **Endpoint**: `/api/v1/user/`
- **Method**: `GET`
- **Description**: Retrieves information about the currently authenticated user.
- **Response Codes**:
  - `200`: Successfully retrieved user information.

#### Add User
- **Endpoint**: `/api/v1/user/`
- **Method**: `POST`
- **Description**: Adds a new user if the current user is authenticated.
- **Parameters**:
  - `first_name` (string, query): User's first name.
  - `last_name` (string, query): User's last name.
  - `email` (string, query): User's email address.
  - `phone_number` (string, query): User's phone number.
- **Response Codes**:
  - `200`: User added successfully.
  - `422`: Validation error.

#### Update User
- **Endpoint**: `/api/v1/user/`
- **Method**: `PUT`
- **Description**: Updates the information of the current user.
- **Parameters**:
  - `first_name` (string, query): User's first name.
  - `last_name` (string, query): User's last name.
  - `phone_number` (string, query): User's phone number.
- **Response Codes**:
  - `200`: User updated successfully.
  - `422`: Validation error.

#### Filter Users
- **Endpoint**: `/api/v1/user/filter`
- **Method**: `GET`
- **Description**: Filters users by name or email.
- **Parameters**:
  - `first_name` (string, query): First name to filter by.
  - `last_name` (string, query): Last name to filter by.
  - `email` (string, query): Email to filter by.
- **Response Codes**:
  - `200`: Successfully retrieved filtered user list.
  - `422`: Validation error.

---

### KPI Endpoints

#### Get All KPIs
- **Endpoint**: `/api/v1/kpi/`
- **Method**: `GET`
- **Description**: Retrieves all KPIs in the dataset.
- **Response Codes**:
  - `201`: Successfully retrieved KPI list.

#### Create a New KPI
- **Endpoint**: `/api/v1/kpi/`
- **Method**: `POST`
- **Description**: Creates a new KPI entry.
- **Response Codes**:
  - `201`: KPI created successfully.

#### Update a KPI
- **Endpoint**: `/api/v1/kpi/{kpi_id}`
- **Method**: `PUT`
- **Description**: Updates an existing KPI based on its `kpi_id`.
- **Parameters**:
  - `kpi_id` (string, path): The ID of the KPI to update.
- **Response Codes**:
  - `201`: KPI updated successfully.

#### Delete a KPI
- **Endpoint**: `/api/v1/kpi/{kpi_id}`
- **Method**: `DELETE`
- **Description**: Deletes a KPI entry based on its `kpi_id`.
- **Parameters**:
  - `kpi_id` (string, path): The ID of the KPI to delete.
- **Response Codes**:
  - `201`: KPI deleted successfully.

---

## Schemas

TODO

## Authentication & Security

The Industry 5.0 API relies on Firebase for handling authentication, ensuring secure access to endpoints based on user credentials and permissions.

---

## Version

- **API Version**: 0.1.0 (OpenAPI 3.1)

