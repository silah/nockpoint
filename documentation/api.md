# API Documentation

## Overview

The Nockpoint API provides RESTful endpoints for managing archery club operations. All endpoints require proper authentication and authorization based on user roles.

## Authentication

### Login Endpoint
```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=password
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Logout Endpoint
```
POST /auth/logout
```

## User Management API

### Register New User
```
POST /auth/register
Content-Type: application/x-www-form-urlencoded

username=newuser&email=user@example.com&password=securepass&confirm_password=securepass&first_name=John&last_name=Doe
```

### Get User Profile
```
GET /members/<int:user_id>
Authorization: Required (Admin or self)
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "admin",
  "created_at": "2025-01-15T10:30:00Z",
  "is_active": true
}
```

## Competition Management API

### List Competitions
```
GET /competitions
Authorization: Required
```

**Response:**
```json
{
  "upcoming_competitions": [
    {
      "id": 1,
      "event": {
        "id": 1,
        "name": "Monthly Championship",
        "date": "2025-02-15",
        "location": "Main Range"
      },
      "status": "registration_open",
      "number_of_rounds": 6,
      "arrows_per_round": 6,
      "target_size_cm": 122,
      "registration_count": 12
    }
  ],
  "past_competitions": []
}
```

### Create Competition
```
POST /competitions
Authorization: Admin Required
Content-Type: application/x-www-form-urlencoded

event_id=1&number_of_rounds=6&arrows_per_round=6&target_size_cm=122&max_team_size=4
```

### Get Competition Details
```
GET /competitions/<int:id>
Authorization: Required
```

**Response:**
```json
{
  "id": 1,
  "event": {
    "id": 1,
    "name": "Monthly Championship",
    "date": "2025-02-15",
    "start_time": "10:00:00",
    "location": "Main Range"
  },
  "number_of_rounds": 6,
  "arrows_per_round": 6,
  "target_size_cm": 122,
  "max_team_size": 4,
  "status": "registration_open",
  "total_arrows": 36,
  "max_possible_score": 360,
  "registration_count": 12,
  "groups": [
    {
      "id": 1,
      "name": "Adults",
      "participant_count": 8,
      "teams": []
    }
  ]
}
```

### Start Competition
```
POST /competitions/<int:id>/start
Authorization: Admin Required
```

### Complete Competition
```
POST /competitions/<int:id>/complete
Authorization: Admin Required
```

**Response:**
```json
{
  "success": true,
  "message": "Competition completed! 15 missing arrows were automatically filled with 0-point scores.",
  "filled_arrows": 15,
  "completion_stats": {
    "total_participants": 12,
    "completed_participants": 12,
    "completion_percentage": 100.0,
    "missing_arrows_total": 0
  }
}
```

### Delete Competition
```
DELETE /competitions/<int:id>
Authorization: Admin Required
```

## Competition Groups & Teams API

### Setup Groups
```
GET /competitions/<int:id>/groups
Authorization: Admin Required
```

### Create Competition Group
```
POST /competitions/<int:id>/groups
Authorization: Admin Required
Content-Type: application/x-www-form-urlencoded

name=Adults&description=Adult+category&min_age=18
```

### Generate Teams
```
POST /competitions/<int:id>/generate-teams
Authorization: Admin Required
```

**Response:**
```json
{
  "success": true,
  "teams_created": 3,
  "groups": [
    {
      "group_name": "Adults",
      "teams": [
        {
          "team_number": 1,
          "target_number": 1,
          "members": ["john_doe", "jane_smith", "bob_wilson"]
        }
      ]
    }
  ]
}
```

## Competition Registration API

### Register for Competition
```
POST /competitions/<int:id>/register
Authorization: Required
Content-Type: application/x-www-form-urlencoded

group_id=1&notes=First+time+competing
```

### Get Registration Status
```
GET /competitions/<int:id>/my-registration
Authorization: Required
```

**Response:**
```json
{
  "registered": true,
  "registration": {
    "id": 15,
    "group": "Adults",
    "team": {
      "number": 2,
      "target": 3
    },
    "registration_date": "2025-01-15T14:30:00Z",
    "total_score": 245,
    "completed_rounds": 4,
    "is_complete": false
  }
}
```

## Scoring API

### Get Scoring Overview
```
GET /competitions/<int:id>/scoring
Authorization: Admin Required
```

**Response:**
```json
{
  "competition": {
    "id": 1,
    "status": "in_progress",
    "total_arrows": 36
  },
  "completion_stats": {
    "total_participants": 12,
    "completed_participants": 8,
    "completion_percentage": 66.7,
    "missing_arrows_total": 144
  },
  "participants": [
    {
      "registration_id": 15,
      "member": {
        "id": 5,
        "username": "archer1",
        "name": "John Archer"
      },
      "group": "Adults",
      "team": 2,
      "total_score": 245,
      "completed_rounds": 4,
      "is_complete": false,
      "round_scores": [42, 38, 45, 41, 0, 0]
    }
  ]
}
```

### Get Individual Scoring Form
```
GET /competitions/<int:id>/score/<int:registration_id>
Authorization: Admin Required
```

### Submit Arrow Scores
```
POST /competitions/<int:id>/score/<int:registration_id>
Authorization: Admin Required
Content-Type: application/x-www-form-urlencoded

arrow_1=8&is_x_1=false&arrow_2=9&is_x_2=false&arrow_3=10&is_x_3=true&arrow_4=7&is_x_4=false&arrow_5=8&is_x_5=false&arrow_6=9&is_x_6=false&round=1
```

**Response:**
```json
{
  "success": true,
  "round_completed": 1,
  "round_score": 51,
  "total_score": 51,
  "next_round": 2,
  "is_complete": false
}
```

## Results API

### Get Competition Results
```
GET /competitions/<int:id>/results
Authorization: Required
```

**Response:**
```json
{
  "competition": {
    "id": 1,
    "name": "Monthly Championship",
    "status": "completed"
  },
  "results_by_group": {
    "Adults": [
      {
        "rank": 1,
        "registration": {
          "id": 15,
          "member": {
            "username": "archer1",
            "name": "John Archer"
          },
          "team": 2,
          "total_score": 312,
          "round_scores": [52, 48, 55, 49, 53, 55],
          "x_count": 8
        }
      }
    ]
  },
  "team_results": {
    "Adults": [
      {
        "rank": 1,
        "team_number": 2,
        "target_number": 3,
        "total_score": 1180,
        "average_score": 295.0,
        "members": ["john_archer", "jane_smith", "bob_wilson", "alice_johnson"]
      }
    ]
  }
}
```

## Event Management API

### List Events
```
GET /events
Authorization: Required
```

### Create Event
```
POST /events
Authorization: Admin Required
Content-Type: application/x-www-form-urlencoded

name=Weekly+Practice&description=Regular+practice+session&location=Indoor+Range&date=2025-02-20&start_time=19:00&duration_hours=2&price=15.00&max_participants=20
```

### Get Event Attendance
```
GET /events/<int:id>/attendance
Authorization: Admin Required
```

### Record Attendance
```
POST /events/<int:id>/attendance
Authorization: Admin Required
Content-Type: application/x-www-form-urlencoded

member_id=5&attended=true&notes=Excellent+participation
```

## Inventory Management API

### List Inventory Categories
```
GET /inventory/categories
Authorization: Required
```

### Create Inventory Category
```
POST /inventory/categories
Authorization: Admin Required
Content-Type: application/x-www-form-urlencoded

name=Recurve+Bows&description=Traditional+recurve+bows+for+target+archery
```

### List Inventory Items
```
GET /inventory
Authorization: Required
Query Parameters: ?category=1&search=bow&page=1&per_page=20
```

### Create Inventory Item
```
POST /inventory
Authorization: Admin Required
Content-Type: application/x-www-form-urlencoded

name=Samick+Sage&description=Traditional+recurve+bow&category_id=1&quantity=5&unit=piece&location=Rack+A&purchase_price=120.00&condition=good&attributes={"draw_weight":45,"handedness":"right"}
```

### Update Inventory Item
```
PUT /inventory/<int:id>
Authorization: Admin Required
Content-Type: application/x-www-form-urlencoded

quantity=3&condition=fair&notes=Needs+string+replacement
```

## Member Management API

### List Members
```
GET /members
Authorization: Admin Required
Query Parameters: ?search=john&role=member&active=true&page=1&per_page=20
```

### Update Member
```
PUT /members/<int:id>
Authorization: Admin Required
Content-Type: application/x-www-form-urlencoded

role=admin&is_active=true&notes=Promoted+to+admin
```

### Get Member Charges
```
GET /members/<int:id>/charges
Authorization: Admin or Self
```

### Create Member Charge
```
POST /members/<int:id>/charges
Authorization: Admin Required
Content-Type: application/x-www-form-urlencoded

description=Equipment+rental&amount=25.00&event_id=5
```

### Mark Charge as Paid
```
POST /members/<int:id>/charges/<int:charge_id>/pay
Authorization: Admin Required
Content-Type: application/x-www-form-urlencoded

payment_notes=Cash+payment+received
```

## Error Responses

### Standard Error Format
```json
{
  "error": true,
  "message": "Description of the error",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created successfully
- `400` - Bad request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found
- `409` - Conflict (duplicate data)
- `500` - Internal server error

### Validation Errors
```json
{
  "error": true,
  "message": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "username": ["Username is required"],
    "email": ["Invalid email format"],
    "password": ["Password must be at least 8 characters"]
  }
}
```

## Rate Limiting

### Default Limits
- Authentication endpoints: 5 requests per minute
- General API endpoints: 100 requests per minute
- Scoring endpoints: 200 requests per minute (higher for real-time scoring)

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1643723400
```

## Data Export API

### Export Competition Data
```
GET /competitions/<int:id>/export
Authorization: Admin Required
Query Parameters: ?format=csv|json|xlsx
```

### Export Member List
```
GET /members/export
Authorization: Admin Required
Query Parameters: ?format=csv|json&include_charges=true
```

### Export Event Attendance
```
GET /events/<int:id>/export
Authorization: Admin Required
Query Parameters: ?format=csv|json
```

## WebSocket API (Future Enhancement)

### Real-time Scoring Updates
```javascript
// Client-side WebSocket connection
const socket = io('/competitions');

// Listen for score updates
socket.on('score_update', function(data) {
    // Update UI with new score
    updateScoreDisplay(data.registration_id, data.total_score);
});

// Submit score update
socket.emit('update_score', {
    competition_id: 1,
    registration_id: 15,
    arrow_scores: [8, 9, 10, 7, 8, 9],
    round: 1
});
```

## API Client Examples

### Python Client
```python
import requests

class NockpointAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.session = requests.Session()
        self.login(username, password)
    
    def login(self, username, password):
        response = self.session.post(
            f"{self.base_url}/auth/login",
            data={'username': username, 'password': password}
        )
        return response.json()
    
    def get_competitions(self):
        response = self.session.get(f"{self.base_url}/competitions")
        return response.json()
    
    def submit_scores(self, competition_id, registration_id, scores):
        data = {f'arrow_{i+1}': score for i, score in enumerate(scores)}
        response = self.session.post(
            f"{self.base_url}/competitions/{competition_id}/score/{registration_id}",
            data=data
        )
        return response.json()

# Usage
api = NockpointAPI('http://localhost:5000', 'admin', 'password')
competitions = api.get_competitions()
result = api.submit_scores(1, 15, [8, 9, 10, 7, 8, 9])
```

### JavaScript Client
```javascript
class NockpointAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    async login(username, password) {
        const response = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: new URLSearchParams({username, password})
        });
        return response.json();
    }
    
    async getCompetitions() {
        const response = await fetch(`${this.baseUrl}/competitions`);
        return response.json();
    }
    
    async submitScores(competitionId, registrationId, scores) {
        const data = new URLSearchParams();
        scores.forEach((score, index) => {
            data.append(`arrow_${index + 1}`, score);
        });
        
        const response = await fetch(
            `${this.baseUrl}/competitions/${competitionId}/score/${registrationId}`,
            {method: 'POST', body: data}
        );
        return response.json();
    }
}
```
