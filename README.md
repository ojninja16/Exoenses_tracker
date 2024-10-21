# Daily Expenses Sharing Application API Documentation

## Authentication Overview

This project uses **JWT (JSON Web Token)** for authentication. Here's how the JWT authentication process works:

1. **User Login:**
   - The user sends a POST request with their credentials (email and password) to the `/api/token/` endpoint.
   - Example:
     ```bash
     curl -X POST http://localhost:8000/api/token/ -d "email=user@example.com&password=yourpassword"
     ```
   - Response:
     ```json
     {
       "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci...",
       "access": "eyJ0eXAiOiJKV1QiLCJhbGci..."
     }
     ```

2. **Accessing Protected Routes:**
   - Use the access token to make authenticated requests to protected endpoints.
   - Example (fetching user expenses):
     ```bash
     curl -H "Authorization: Bearer <access_token>" http://localhost:8000/api/users/<user_email>/expenses/
     ```

3. **Token Refresh:**
   - When the access token expires, use the refresh token to obtain a new access token by sending a POST request to the `/api/token/refresh/` endpoint.
   - Example:
     ```bash
     curl -X POST http://localhost:8000/api/token/refresh/ -d "refresh=<refresh_token>"
     ```
# Database Setup with Docker

The project uses PostgreSQL as the database, and the `docker-compose.yml` is already provided in the repository.

## Steps to Set Up the Database

1. Ensure Docker is installed on your system.
2. Navigate to the project directory where `docker-compose.yml` is located.
3. Run the following command to start the database:
   ```bash
   docker-compose up

## Base URL
```
http://localhost:8000/api/
```

## User Endpoints

### Create New User
```http
POST /api/users/
{
    "email": "user@example.com",
    "username": "user1",
    "password": "password123",
    "mobile_number": "1234567890",
    "first_name": "John",
    "last_name": "Doe"
}
```

### Get User Details
```http
GET /api/users/{email}/
```

### Update User Details
```http
PUT /api/users/{email}/
{
    "mobile_number": "9876543210",
    "first_name": "John Updated"
}
```

### Get User's Expenses
```http
GET /api/users/{email}/expenses/
```

## Expense Endpoints

### Create New Expense (Equal Split)
```http
POST /api/expenses/
{
    "title": "Dinner",
    "amount": "3000.00",
    "split_type": "EQUAL",
    "paid_by_email": "user@example.com",
    "splits": [
        {"user_email": "user1@example.com"},
        {"user_email": "user2@example.com"},
        {"user_email": "user3@example.com"}
    ]
}
```

### Create New Expense (Exact Split)
```http
POST /api/expenses/
{
    "title": "Shopping",
    "amount": "4299.00",
    "split_type": "EXACT",
    "paid_by_email": "user@example.com",
    "splits": [
        {"user_email": "user1@example.com", "amount": "799.00"},
        {"user_email": "user2@example.com", "amount": "2000.00"},
        {"user_email": "user3@example.com", "amount": "1500.00"}
    ]
}
```

### Create New Expense (Percentage Split)
```http
POST /api/expenses/
{
    "title": "Party",
    "amount": "1000.00",
    "split_type": "PERCENTAGE",
    "paid_by_email": "user@example.com",
    "splits": [
        {"user_email": "user1@example.com", "percentage": "50"},
        {"user_email": "user2@example.com", "percentage": "25"},
        {"user_email": "user3@example.com", "percentage": "25"}
    ]
}
```

### Get All Expenses
```http
GET /api/expenses/
```

### Get Single Expense
```http
GET /api/expenses/{expense_id}/
```

### Get Expense Summary for User
```http
GET /api/expenses/summary/?user_email=user@example.com
```

### Get Overall Summary (All Users)
```http
GET /api/expenses/summary/
```

### Download Balance Sheet (CSV)
```http
GET /api/expenses/download_balance_sheet/
```

### Get User-Specific Balance Sheet
```http
GET /api/expenses/get_user_balance_sheet/?user_email=user@example.com
```

## Response Examples

### User Summary Response
```json
{
    "user_email": "user@example.com",
    "total_paid": 3000.00,
    "total_owed": 1000.00,
    "net_balance": 2000.00,
    "expense_breakdown": [
        {
            "expense__title": "Dinner",
            "expense__amount": 3000.00,
            "expense__split_type": "EQUAL",
            "amount": 750.00,
            "percentage": null,
            "expense__paid_by__email": "user@example.com"
        }
    ]
}
```

### Balance Sheet Response
```json
{
    "user_email": "user@example.com",
    "expenses_involved": [
        {
            "date": "2024-02-20 14:30",
            "description": "Dinner",
            "total_amount": 3000.00,
            "paid_by": "user@example.com",
            "split_type": "EQUAL",
            "your_share": 750.00,
            "your_percentage": null
        }
    ],
    "expenses_paid": [
        {
            "date": "2024-02-20 14:30",
            "description": "Dinner",
            "total_amount": 3000.00,
            "split_type": "EQUAL",
            "splits": [
                {
                    "user": "user1@example.com",
                    "amount": 750.00,
                    "percentage": null
                }
            ]
        }
    ]
}
```

## Error Responses

### Validation Error
```json
{
    "detail": "Error message describing the validation failure"
}
```

### Not Found Error
```json
{
    "detail": "Not found."
}
```

## Notes
- All amounts are in decimal format with 2 decimal places
- Percentages must sum to 100% for percentage splits
- Exact amounts must sum to total expense amount
- All dates are in ISO format
- Authentication is required for all endpoints 
