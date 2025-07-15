SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for mcp_service
-- ----------------------------
DROP TABLE IF EXISTS `mcp_service`;
CREATE TABLE `mcp_service` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Primary key, auto-incremented ID',
  `service_id` CHAR(36) NOT NULL COMMENT 'Unique MCP service ID (UUID)',
  `name` VARCHAR(100) NOT NULL COMMENT 'Service name',
  `slug_name` VARCHAR(100) NOT NULL COMMENT 'Unique slug for the service',
  `short_description` VARCHAR(500) NOT NULL COMMENT 'Short service description',
  `long_description` TEXT COMMENT 'Detailed description in Markdown',
  `auth_method` ENUM('none', 'apikey', 'token') NOT NULL DEFAULT 'none' COMMENT 'Authentication method',
  `auth_header` VARCHAR(100) DEFAULT NULL COMMENT 'Authentication header name',
  `auth_token` VARCHAR(255) DEFAULT NULL COMMENT 'Static authentication token',
  `charge_type` ENUM('free', 'per_call', 'per_token') NOT NULL DEFAULT 'free' COMMENT 'Billing method',
  `price` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Price per unit',
  `enabled` BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Service status: 0=disabled, 1=enabled',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `uk_service_id` (`service_id`),
  UNIQUE INDEX `uk_slug_name` (`slug_name`),
  INDEX `idx_enabled` (`enabled`)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='MCP service registry' ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Table structure for mcp_tool_api
-- ----------------------------
DROP TABLE IF EXISTS `mcp_tool_api`;
CREATE TABLE `mcp_tool_api` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Primary key, auto-incremented ID',
  `tool_id` CHAR(36) NOT NULL COMMENT 'Unique MCP tool ID (UUID)',
  `service_id` CHAR(36) NOT NULL COMMENT 'MCP service ID (UUID)',
  `name` VARCHAR(100) NOT NULL COMMENT 'API name',
  `description` VARCHAR(500) NOT NULL COMMENT 'API description',
  `url` VARCHAR(512) NOT NULL COMMENT 'API endpoint URL',
  `method` ENUM('GET', 'POST', 'PUT', 'DELETE', 'PATCH') NOT NULL COMMENT 'HTTP request method',
  `headers` JSON DEFAULT NULL COMMENT 'Request headers (JSON format)',
  `params` TEXT COMMENT 'Request parameters',
  `request_body` TEXT COMMENT 'Request body template',
  `request_schema` JSON DEFAULT NULL COMMENT 'Request schema (JSON)',
  `response_schema` JSON DEFAULT NULL COMMENT 'Response schema (JSON)',
  `request_demo` TEXT COMMENT 'Example request',
  `response_demo` TEXT COMMENT 'Example response',
  `enabled` BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'API status: 0=disabled, 1=enabled',
  `is_deleted` BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Soft delete flag: 0=active, 1=deleted',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `uk_tool_id` (`tool_id`),
  INDEX `idx_service_id` (`service_id`),
  INDEX `idx_enabled` (`enabled`),
  CONSTRAINT `fk_service_id` FOREIGN KEY (`service_id`) REFERENCES `mcp_service` (`service_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='API registry for MCP tools' ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Table structure for sys_config
-- ----------------------------
DROP TABLE IF EXISTS `sys_config`;
CREATE TABLE `sys_config` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Primary key, auto-incremented ID',
  `key` VARCHAR(100) NOT NULL COMMENT 'Configuration key',
  `value` TEXT NOT NULL COMMENT 'Configuration value',
  `description` VARCHAR(500) NOT NULL COMMENT 'Configuration description',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `uk_key` (`key`)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='System configuration settings' ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Primary key, auto-incremented ID',
  `user_id` CHAR(36) NOT NULL COMMENT 'Unique user ID (UUID)',
  `name` VARCHAR(100) NOT NULL COMMENT 'Username',
  `email` VARCHAR(255) NOT NULL COMMENT 'Email address',
  `avatar` VARCHAR(255) DEFAULT NULL COMMENT 'Avatar URL',
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Account status: 0=disabled, 1=active',
  `is_deleted` BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Soft delete flag: 0=active, 1=deleted',
  `register_type` ENUM('email', 'google') NOT NULL COMMENT 'Registration method',
  `user_type` ENUM('user', 'admin') NOT NULL DEFAULT 'user' COMMENT 'User role',
  `last_login_at` TIMESTAMP NULL DEFAULT NULL COMMENT 'Last login timestamp',
  `last_login_ip` VARCHAR(45) DEFAULT NULL COMMENT 'Last login IP (IPv4/IPv6 compatible)',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `uk_email` (`email`),
  UNIQUE INDEX `uk_user_id` (`user_id`),
  INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='User registry' ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Table structure for user_access_token
-- ----------------------------
DROP TABLE IF EXISTS `user_access_token`;
CREATE TABLE `user_access_token` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Primary key, auto-incremented ID',
  `user_id` CHAR(36) NOT NULL COMMENT 'User ID (UUID)',
  `token` VARCHAR(255) NOT NULL COMMENT 'Access token',
  `expire_at` TIMESTAMP NOT NULL COMMENT 'Token expiration timestamp',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `uk_token` (`token`),
  INDEX `idx_user_id` (`user_id`),
  CONSTRAINT `fk_user_id_token` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='User access tokens' ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Table structure for user_wallet
-- ----------------------------
DROP TABLE IF EXISTS `user_wallet`;
CREATE TABLE `user_wallet` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Primary key, auto-incremented ID',
  `user_id` CHAR(36) NOT NULL COMMENT 'User ID (UUID)',
  `balance` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Wallet balance',
  `frozen_balance` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Frozen balance',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `uk_user_id` (`user_id`),
  CONSTRAINT `fk_user_id_wallet` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='User wallet balances' ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Table structure for user_wallet_history
-- ----------------------------
DROP TABLE IF EXISTS `user_wallet_history`;
CREATE TABLE `user_wallet_history` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Primary key, auto-incremented ID',
  `history_id` CHAR(36) NOT NULL COMMENT 'Unique transaction history ID (UUID)',
  `user_id` CHAR(36) NOT NULL COMMENT 'User ID (UUID)',
  `payment_method` ENUM('platform', 'stripe', 'alipay', 'wechat') NOT NULL COMMENT 'Payment method',
  `amount` DECIMAL(10, 2) NOT NULL COMMENT 'Transaction amount (positive=deposit, negative=consumption)',
  `balance_after` DECIMAL(10, 2) NOT NULL COMMENT 'Balance after transaction',
  `type` ENUM('deposit', 'consume', 'refund') NOT NULL COMMENT 'Transaction type',
  `status` TINYINT UNSIGNED NOT NULL COMMENT 'Transaction status: 0=new, 1=completed, 2=pending',
  `transaction_id` VARCHAR(255) DEFAULT NULL COMMENT 'Payment platform transaction ID',
  `channel_user_id` VARCHAR(255) DEFAULT NULL COMMENT 'Payment channel user ID',
  `callback_data` TEXT COMMENT 'Payment callback data',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `uk_history_id` (`history_id`),
  UNIQUE INDEX `uk_transaction_id` (`transaction_id`),
  INDEX `idx_user_id` (`user_id`),
  CONSTRAINT `fk_user_id_history` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='User wallet transaction history' ROW_FORMAT=DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;