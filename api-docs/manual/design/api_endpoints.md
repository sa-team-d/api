# API Endpoints
## Industry 5.0 Platform Endpoints

### 1. Knowledge Base Endpoints

#### KPI Management
```
GET    /api/v1/kpis
POST   /api/v1/kpis
GET    /api/v1/kpis/{id}
PUT    /api/v1/kpis/{id}
DELETE /api/v1/kpis/{id}
GET    /api/v1/kpis/{id}/history
GET    /api/v1/kpis/categories
GET    /api/v1/kpis/search
```

#### Taxonomy
```
GET    /api/v1/taxonomy
POST   /api/v1/taxonomy/nodes
PUT    /api/v1/taxonomy/nodes/{id}
DELETE /api/v1/taxonomy/nodes/{id}
GET    /api/v1/taxonomy/relationships
```

### 2. Data Management Endpoints

#### Time Series Data
```
GET    /api/v1/data/timeseries
POST   /api/v1/data/timeseries/batch
GET    /api/v1/data/timeseries/{kpi_id}
GET    /api/v1/data/timeseries/{kpi_id}/aggregate
GET    /api/v1/data/timeseries/export
```

#### Real-time Data
```
WS     /api/v1/data/stream
GET    /api/v1/data/stream/status
POST   /api/v1/data/stream/configure
```

### 3. AI Agent Endpoints

#### Query Interface
```
POST   /api/v1/ai/query
GET    /api/v1/ai/query/{id}
GET    /api/v1/ai/context
POST   /api/v1/ai/feedback
```

#### Generation
```
POST   /api/v1/ai/generate/kpi
POST   /api/v1/ai/generate/dashboard
POST   /api/v1/ai/generate/report
GET    /api/v1/ai/generate/{id}/status
```

### 4. KPI Engine Endpoints

#### Calculation
```
POST   /api/v1/engine/calculate
GET    /api/v1/engine/calculate/{id}
GET    /api/v1/engine/status
POST   /api/v1/engine/rules
GET    /api/v1/engine/rules/{id}
```

#### Monitoring
```
GET    /api/v1/engine/health
GET    /api/v1/engine/metrics
GET    /api/v1/engine/alerts
POST   /api/v1/engine/alerts/acknowledge
```

### 5. Dashboard Endpoints
```
GET    /api/v1/dashboards
POST   /api/v1/dashboards
GET    /api/v1/dashboards/{id}
PUT    /api/v1/dashboards/{id}
DELETE /api/v1/dashboards/{id}
POST   /api/v1/dashboards/{id}/widgets
DELETE /api/v1/dashboards/{id}/widgets/{widget_id}
```

### 6. Firebase Authentication Endpoints
```
POST /api/v1/auth/firebase/login
POST /api/v1/auth/firebase/register 
POST /api/v1/auth/firebase/verify-email 
POST /api/v1/auth/firebase/reset-password 
POST /api/v1/auth/firebase/refresh-token 
GET /api/v1/users/me PUT /api/v1/users/me 
GET /api/v1/users/{id} PUT /api/v1/users/{id} 
DELETE /api/v1/users/{id} 
GET /api/v1/users/{id}/permissions


```

### 7. System Administration Endpoints
```
GET    /api/v1/system/health
GET    /api/v1/system/metrics
GET    /api/v1/system/logs
POST   /api/v1/system/backup
GET    /api/v1/system/configuration
PUT    /api/v1/system/configuration
```

### 8. Integration Endpoints
```
POST   /api/v1/webhooks
GET    /api/v1/webhooks/{id}
DELETE /api/v1/webhooks/{id}
POST   /api/v1/integrations
GET    /api/v1/integrations/{id}/status
PUT    /api/v1/integrations/{id}/configure
```

### Authentication Headers
```
Authorization: Bearer <firebase_id_token> X-Firebase-Auth: <firebase_auth_token> X-API-Key: <api_key>
X-API-Key: <api_key>
```
### Firebase Admin Endpoints
POST /api/v1/admin/users/disable 
POST /api/v1/admin/users/enable 
POST /api/v1/admin/users/roles 
GET /api/v1/admin/users/roles 
DELETE /api/v1/admin/users/roles

### Query Parameters
```
?page=1
?per_page=20
?sort=field:desc
?filter=field:value
?include=related_resource
?fields=field1,field2
?time_range=start:end
```