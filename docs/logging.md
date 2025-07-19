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

## Log Message Guidelines

### Language Requirements
All log messages MUST be in English to ensure consistency and international collaboration.

### Message Format Standards

#### Correct Examples ✅
```python
logger.info("Starting to download content from URL: {url}")
logger.error("Failed to process request: {error_message}")
logger.warning("Invalid content type detected: {content_type}")
logger.debug("Processing user authentication for: {user_id}")
```

#### Incorrect Examples ❌
```python
logger.info(f"开始从URL下载内容: {url}")  # Chinese message
logger.error(f"处理请求失败: {error_message}")  # Chinese message
logger.warning(f"内容类型可能不正确: {content_type}")  # Chinese message
```

### Message Content Guidelines

1. **Use descriptive English messages**
   - Keep messages clear and concise
   - Use standard technical terminology
   - Maintain consistent tense

2. **Include contextual information**
   - Provide sufficient information for debugging
   - Include key variables and states
   - Use structured message format

3. **Follow consistent patterns**
   - Use present continuous (-ing) for ongoing operations
   - Use past tense for completed operations
   - Start error messages with "Failed to"

### Common Message Patterns

#### Network Operations
```python
logger.info(f"Starting to download content from URL: {url}")
logger.error(f"Network request failed: {error}")
logger.error(f"Request timeout for URL: {url}")
logger.info(f"Successfully downloaded content, size: {len(content)} characters")
```

#### Database Operations
```python
logger.info(f"Starting to query user data: {user_id}")
logger.error(f"Database connection failed: {error}")
logger.info(f"Successfully updated user information: {user_id}")
```

#### Business Logic
```python
logger.info(f"Starting to process order: {order_id}")
logger.error(f"Failed to process order: {error}")
logger.warning(f"Insufficient permissions for user: {user_id}")
```

#### Authentication & Authorization
```python
logger.info(f"User login successful: {username}")
logger.error(f"Authentication failed for user: {username}")
logger.warning(f"Token expiring soon: {token_id}")
```

### Security Considerations
- Never log sensitive information (passwords, API keys, tokens)
- Use placeholder text like "***" for sensitive data
- Be careful with user data and follow privacy guidelines

## Example Log Messages

```
2024-01-15 10:30:45,123 - [admin_service] - [INFO] - [services.admin_service.main] - Admin Service starting...
2024-01-15 10:30:45,124 - [api_service] - [INFO] - [services.api_service.main] - MCP Streamable HTTP Service starting... Port: 8002
2024-01-15 10:30:45,125 - [admin_service] - [ERROR] - [services.admin_service.consumers.billing_message_consumer] - Failed to establish RabbitMQ connection
2024-01-15 10:30:45,126 - [api_service] - [DEBUG] - [services.api_service.services.mcp_server_factory] - Authentication info: {'api_key': '***'}
```

## Code Review Checklist

Before submitting code, ensure:

- [ ] All log messages are in English
- [ ] Message format is consistent across the codebase
- [ ] Necessary contextual information is included
- [ ] Appropriate log level is used
- [ ] No sensitive information is logged (passwords, API keys, etc.)
- [ ] Messages are clear and helpful for debugging

## Automated Checks

You can use these methods to find Chinese log messages that need translation:

### Using grep (Linux/macOS/WSL)
```bash
# Find logger statements with Chinese characters
grep -r "logger\.[a-zA-Z]*.*[\u4e00-\u9fff]" services/
```

### Using Python script
```python
import re
import os

def check_chinese_logs(directory):
    """Check for Chinese characters in logger statements"""
    pattern = r'logger\.[a-zA-Z]+\(.*[\u4e00-\u9fff].*\)'
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = re.findall(pattern, content)
                    if matches:
                        print(f"File: {file_path}")
                        for match in matches:
                            print(f"  - {match}")
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