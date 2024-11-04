# Data Models
## Industry 5.0 Platform Data Structures

### 1. KPI Model
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "category": "string",
  "formula": "string",
  "unit": "string",
  "thresholds": {
    "warning": "number",
    "critical": "number"
  },
  "metadata": {
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "created_by": "string"
  },
  "dependencies": ["string"],
  "tags": ["string"]
}
```

### 2. Time Series Data Model
```json
{
  "id": "string",
  "timestamp": "timestamp",
  "kpi_id": "string",
  "value": "number",
  "quality": "number",
  "source": "string",
  "metadata": {
    "unit": "string",
    "confidence": "number"
  }
}
```

### 3. AI Agent Query Model
```json
{
  "id": "string",
  "query_text": "string",
  "context": {
    "kpi_ids": ["string"],
    "time_range": {
      "start": "timestamp",
      "end": "timestamp"
    }
  },
  "response": {
    "text": "string",
    "suggestions": ["string"],
    "confidence": "number"
  }
}
```

### 4. Dashboard Model
```json
{
  "id": "string",
  "name": "string",
  "layout": {
    "widgets": [
      {
        "id": "string",
        "type": "string",
        "kpi_id": "string",
        "position": {
          "x": "number",
          "y": "number",
          "width": "number",
          "height": "number"
        }
      }
    ]
  },
  "filters": {
    "time_range": {
      "start": "timestamp",
      "end": "timestamp"
    },
    "categories": ["string"]
  }
}
```

### 5. Alert Model
```json
{
  "id": "string",
  "kpi_id": "string",
  "severity": "string",
  "message": "string",
  "timestamp": "timestamp",
  "status": "string",
  "metadata": {
    "acknowledged_by": "string",
    "acknowledged_at": "timestamp"
  }
}
```

### 6. User Model
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "role": "string",
  "permissions": ["string"],
  "settings": {
    "notifications": {
      "email": "boolean",
      "web": "boolean"
    },
    "preferences": {
      "theme": "string",
      "language": "string"
    }
  }
}
```

### 7. Audit Log Model
```json
{
  "id": "string",
  "action": "string",
  "resource_type": "string",
  "resource_id": "string",
  "user_id": "string",
  "timestamp": "timestamp",
  "changes": {
    "before": {},
    "after": {}
  }
}
```

### 8. System Health Model
```json
{
  "id": "string",
  "component": "string",
  "status": "string",
  "metrics": {
    "cpu_usage": "number",
    "memory_usage": "number",
    "api_latency": "number"
  },
  "timestamp": "timestamp"
}
```