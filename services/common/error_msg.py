# Common error messages for global use

INVALID_URL = {"code": 400, "message": "The provided URL is not accessible or invalid. Please check the URL and try again."}
MISSING_URL_OR_FILE = {"code": 400, "message": "Please provide either a valid URL or a file to parse the OpenAPI document."}
CREATE_FAILED = {"code": 500, "message": "Failed to create resource. Please try again later."}
NOT_FOUND = {"code": 404, "message": "The requested resource was not found."}
NO_PERMISSION = {"code": 403, "message": "You do not have permission to perform this action."}
DELETE_FAILED = {"code": 403, "message": "Delete failed, resource not found or no permission."}
MODIFY_FAILED = {"code": 403, "message": "Modify failed, resource not found or no permission."}
PARAM_REQUIRED = {"code": 400, "message": "Required parameter is missing."}
INTERNAL_ERROR = {"code": 500, "message": "An unexpected error occurred while processing your request. Please try again later."}
