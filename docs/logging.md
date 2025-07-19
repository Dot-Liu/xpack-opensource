# Logging Configuration

## Overview

XPack project uses a unified logging configuration that supports different log levels and service-specific log files. All log messages are in English and follow a consistent format.

## Log Format

```
2024-01-15 10:30:45,123 - [SERVICE_NAME] - [LEVEL] - [MODULE_NAME] - Message content
```

## Directory Structure

```
logs/
├── admin_service/
│   ├── debug.log
│   ├── info.log
│   ├── warn.log
│   └── error.log
├── api_service/
│   ├── debug.log
│   ├── info.log
│   ├── warn.log
│   └── error.log
└── common/
    ├── debug.log
    ├── info.log
    ├── warn.log
    └── error.log
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_TO_FILE` | `true` | Whether to output logs to files |
| `LOG_MAX_SIZE` | `10` | Maximum log file size in MB |
| `LOG_BACKUP_COUNT` | `5` | Number of backup log files to keep |

## Usage

### In Service Code

```python
from services.common.logging_config import setup_logging, get_logger

# Setup logging for the service
setup_logging("admin_service")

# Get logger instance
logger = get_logger(__name__)

# Use logger
logger.info("Service started successfully")
logger.error("An error occurred", exc_info=True)
```

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about program execution
- **WARNING**: Warning messages for potentially problematic situations
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical errors that may prevent the program from running

## Features

### Log Rotation
- Log files are automatically rotated when they reach the maximum size
- Old log files are kept as backups (default: 5 files)
- Each log level has its own file

### Third-party Library Logging
- Third-party libraries (uvicorn, starlette, httpx, pika, sqlalchemy, redis) are set to WARNING level to reduce noise
- This can be customized in the logging configuration

### Service-specific Logging
- Each service (admin_service, api_service) has its own log directory
- Logs are separated by service name for easier debugging

## Configuration

The logging configuration is centralized in `services/common/logging_config.py`. To modify the configuration:

1. Edit the `LoggingConfig` class in `services/common/logging_config.py`
2. Update environment variables as needed
3. Restart the services

## Example Log Messages

```
2024-01-15 10:30:45,123 - [admin_service] - [INFO] - [services.admin_service.main] - Admin Service starting...
2024-01-15 10:30:45,124 - [api_service] - [INFO] - [services.api_service.main] - MCP Streamable HTTP Service starting... Port: 8002
2024-01-15 10:30:45,125 - [admin_service] - [ERROR] - [services.admin_service.consumers.billing_message_consumer] - Failed to establish RabbitMQ connection
2024-01-15 10:30:45,126 - [api_service] - [DEBUG] - [services.api_service.services.mcp_server_factory] - Authentication info: {'api_key': '***'}
```

## Troubleshooting

### Log Files Not Created
- Check if the `logs/` directory exists and has write permissions
- Verify that `LOG_TO_FILE=true` is set

### Log Level Issues
- Ensure `LOG_LEVEL` is set to the desired level
- Check that the log level is one of: DEBUG, INFO, WARNING, ERROR, CRITICAL

### File Size Issues
- Adjust `LOG_MAX_SIZE` if log files are too large
- Increase `LOG_BACKUP_COUNT` if you need more backup files 