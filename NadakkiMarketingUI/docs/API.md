# API Documentation v3.0

## Endpoints

### Health Check
```http
GET /health
```

### Campaigns CRUD
```http
POST   /api/v1/campaigns
GET    /api/v1/campaigns
GET    /api/v1/campaigns/{id}
PATCH  /api/v1/campaigns/{id}
DELETE /api/v1/campaigns/{id}
POST   /api/v1/campaigns/{id}/publish
```

### Connections
```http
GET    /api/v1/connections
GET    /api/v1/connections/{platform}/auth-url
DELETE /api/v1/connections/{id}
```
