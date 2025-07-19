# Unified Exception Handling System

This document describes how to use the new unified exception handling system in XPack.

## Overview

The new exception handling system provides:
- **Consistent error responses** across all APIs
- **Simplified error handling** in controllers  
- **Automatic exception processing** through global middleware
- **English-only error messages** for internationalization
- **Structured logging** with proper error levels

## Architecture Components

### 1. Custom Exception Classes (`services/common/exceptions.py`)

- `BaseAPIException` - Base class for all custom exceptions
- `ValidationException` - For input validation errors (400)
- `UnauthorizedException` - For authentication errors (401)
- `ForbiddenException` - For authorization errors (403)
- `NotFoundException` - For resource not found (404)
- `ConflictException` - For resource conflicts (409)
- `BusinessException` - For business logic errors (422)
- `InternalServerException` - For internal server errors (500)
- `ServiceUnavailableException` - For service unavailable (503)

### 2. Global Exception Middleware (`services/common/middleware/exception_middleware.py`)

Automatically catches and converts all exceptions to standardized responses.

### 3. Validation Utilities (`services/common/utils/validation_utils.py`)

Common validation functions that throw appropriate exceptions.

### 4. Enhanced Response Utils (`services/common/utils/response_utils.py`)

Improved response formatting with consistent structure.

### 5. Standardized Error Messages (`services/common/error_msg.py`)

Simplified, English-only error message definitions.

## How to Use

### 1. In Controllers

**Before (Old Way):**
```python
@router.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    try:
        if not user_id:
            return ResponseUtils.error(error_msg=error_msg.PARAM_REQUIRED)
        
        user = user_service.get_user(user_id)
        if not user:
            return ResponseUtils.error(error_msg=error_msg.NOT_FOUND)
            
        return ResponseUtils.success(data=user)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return ResponseUtils.error(error_msg=error_msg.INTERNAL_ERROR)
```

**After (New Way):**
```python
@router.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    # Just validate and throw exceptions - middleware handles the rest
    ValidationUtils.require_non_empty_string(user_id, "user_id")
    
    user = user_service.get_user(user_id)
    ValidationUtils.require_resource_exists(user, "user")
    
    return ResponseUtils.success(data=user)
```

### 2. Using Validation Utils

```python
from services.common.utils.validation_utils import ValidationUtils

# Validate required parameters
user_id = ValidationUtils.require_non_empty_string(user_id, "user_id")

# Validate email format
email = ValidationUtils.validate_email(email_input)

# Validate pagination
page, page_size = ValidationUtils.validate_pagination(page, page_size)

# Validate resource exists
user = ValidationUtils.require_resource_exists(user, "user")
```

### 3. Throwing Custom Exceptions

```python
from services.common.exceptions import (
    ValidationException,
    NotFoundException, 
    BusinessException
)

# Validation error
if not email_is_valid(email):
    raise ValidationException("Invalid email format")

# Business logic error  
if user_already_exists(email):
    raise BusinessException("User with this email already exists")

# Resource not found
if not user:
    raise NotFoundException("User not found")
```

### 4. Adding Exception Middleware to Services

**For admin_service (`services/admin_service/main.py`):**
```python
from services.common.middleware.exception_middleware import ExceptionHandlingMiddleware

app = FastAPI()
app.add_middleware(ExceptionHandlingMiddleware)
```

**For api_service (`services/api_service/main.py`):**
```python
from services.common.middleware.exception_middleware import ExceptionHandlingMiddleware

app = FastAPI()
app.add_middleware(ExceptionHandlingMiddleware)
```

## Response Format

All APIs now return responses in this standardized format:

**Success Response:**
```json
{
  "success": true,
  "code": "200",
  "message": "Success", 
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "code": "400",
  "message": "Invalid request parameters",
  "data": null
}
```

**Paginated Response:**
```json
{
  "success": true,
  "code": "200", 
  "message": "Success",
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total": 25,
    "total_pages": 3
  }
}
```

## Benefits

1. **Consistency** - All APIs return the same response format
2. **Simplicity** - Controllers focus on business logic, not error handling
3. **Maintainability** - Error handling logic is centralized
4. **Reliability** - No more forgotten try-catch blocks
5. **Internationalization** - All error messages in English
6. **Observability** - Structured logging with proper error levels

## Migration Guide

1. Add exception middleware to your FastAPI app
2. Replace manual error handling with exception throwing
3. Use ValidationUtils for parameter validation
4. Update logging to use English messages
5. Remove try-catch blocks from controllers (let middleware handle)

## Example Controller

See `services/common/controllers/example_controller.py` for complete examples of how to use the new exception handling system.
