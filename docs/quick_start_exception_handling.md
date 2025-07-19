# Quick Start Guide - Unified Exception Handling

## ✅ What's Been Done

The unified exception handling system has been successfully integrated into XPack:

### 1. Core Components Added:
- ✅ Custom exception classes (`services/common/exceptions.py`)
- ✅ Global exception middleware (`services/common/middleware/exception_middleware.py`)
- ✅ Validation utilities (`services/common/utils/validation_utils.py`)
- ✅ Enhanced response utils (`services/common/utils/response_utils.py`)
- ✅ Simplified error messages (`services/common/error_msg.py`)

### 2. Services Updated:
- ✅ Admin Service - Exception middleware added
- ✅ API Service - Exception middleware added

### 3. Example Controllers Migrated:
- ✅ `services/admin_service/controllers/web.py` - Fully migrated
- ✅ `services/admin_service/controllers/user_manager.py` - Partially migrated

## 🚀 How to Use

### Quick Controller Example:

**Old Way (Before):**
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

**New Way (After):**
```python
@router.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    # Validate input - throws ValidationException if invalid
    ValidationUtils.require_non_empty_string(user_id, "user_id")
    
    # Business logic - throws exception if fails
    user = user_service.get_user(user_id)
    ValidationUtils.require_resource_exists(user, "user")
    
    # Return success - middleware handles all exceptions automatically
    return ResponseUtils.success(data=user)
```

### Common Validation Patterns:

```python
from services.common.utils.validation_utils import ValidationUtils

# Required parameters
user_id = ValidationUtils.require_non_empty_string(user_id, "user_id")

# Email validation
email = ValidationUtils.validate_email(email_input)

# Pagination
page, page_size = ValidationUtils.validate_pagination(page, page_size)

# Resource existence
user = ValidationUtils.require_resource_exists(user, "user")

# URL validation
url = ValidationUtils.validate_url(url_input)
```

### Custom Exceptions:

```python
from services.common.exceptions import (
    ValidationException,
    NotFoundException, 
    BusinessException,
    UnauthorizedException
)

# Business logic errors
if user_already_exists(email):
    raise BusinessException("User with this email already exists")

# Authentication errors
if not valid_token(token):
    raise UnauthorizedException("Invalid authentication token")

# Not found errors
if not resource:
    raise NotFoundException("Resource not found")
```

## 📊 Standardized Response Format

All APIs now return consistent JSON responses:

**Success:**
```json
{
  "success": true,
  "code": "200",
  "message": "Success",
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "code": "400",
  "message": "Invalid request parameters",
  "data": null
}
```

**Pagination:**
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

## 🧪 Testing

Run the test script to verify everything works:

```bash
python test_exception_handling.py
```

This will test:
- ValidationUtils functions
- HTTP endpoint error handling
- Response format consistency

## 📝 Migration Checklist

For each controller you want to migrate:

1. ✅ Add imports:
   ```python
   from services.common.utils.validation_utils import ValidationUtils
   from services.common.logging_config import get_logger
   ```

2. ✅ Replace logging:
   ```python
   # Old
   import logging
   logger = logging.getLogger(__name__)
   
   # New
   from services.common.logging_config import get_logger
   logger = get_logger(__name__)
   ```

3. ✅ Remove try-catch blocks - let middleware handle exceptions

4. ✅ Use ValidationUtils for parameter validation

5. ✅ Use English log messages:
   ```python
   logger.info(f"Fetching user with ID: {user_id}")
   ```

6. ✅ Let exceptions bubble up - don't catch and return error responses

## 🔧 Benefits

- **Consistency**: All APIs return the same response format
- **Simplicity**: Controllers focus on business logic
- **Maintainability**: Centralized error handling
- **Reliability**: No forgotten try-catch blocks
- **Observability**: Structured English logging
- **Developer Experience**: Clear error messages and validation

## 📚 Next Steps

1. **Migrate more controllers** using the patterns shown above
2. **Update frontend code** to use the new response format
3. **Add more validation rules** to ValidationUtils as needed
4. **Consider internationalization** for error messages if needed
5. **Monitor logs** to ensure proper error handling

## 🆘 Need Help?

- Check `services/common/controllers/example_controller.py` for complete examples
- See `docs/unified_exception_handling.md` for detailed documentation
- Run `python test_exception_handling.py` to test your changes
