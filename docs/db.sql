SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for mcp_service
-- ----------------------------
DROP TABLE IF EXISTS `mcp_service`;
CREATE TABLE `mcp_service` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键，自增唯一标识',
  `service_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'MCP 服务唯一标识（UUID 格式）',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '服务名称',
  `slug_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '服务名称的唯一标识（Slug 格式）',
  `short_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '服务简短描述',
  `long_description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '服务详细描述（Markdown 格式）',
  `auth_method` enum('free','apikey','token') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '鉴权方式：free（免费）、apikey（API 密钥）、token（令牌）',
  `auth_header` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '鉴权请求头名称',
  `auth_token` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '鉴权令牌值',
  `charge_type` enum('free','per_call','per_token') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '计费方式：free（免费）、per_call（按调用次数）、per_token（按令牌数量）',
  `price` decimal(10,2) NOT NULL COMMENT '服务价格（保留两位小数）',
  `enabled` tinyint NULL DEFAULT NULL COMMENT '是否启用：0（禁用）、1（启用）',
  `created_at` timestamp NULL DEFAULT NULL COMMENT '记录创建时间',
  `updated_at` timestamp NULL DEFAULT NULL COMMENT '记录最后更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_service_id` (`service_id` ASC) USING BTREE COMMENT '服务 ID 唯一索引',
  UNIQUE INDEX `uk_slug_name` (`slug_name` ASC) USING BTREE COMMENT '服务 Slug 名称唯一索引'
) ENGINE = InnoDB AUTO_INCREMENT = 353 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = 'MCP 服务信息表，用于存储服务的基本信息及配置' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for mcp_tool_api
-- ----------------------------
DROP TABLE IF EXISTS `mcp_tool_api`;
CREATE TABLE `mcp_tool_api` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键，自增唯一标识',
  `tool_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'MCP 工具唯一标识（UUID 格式）',
  `service_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '关联的 MCP 服务唯一标识（UUID 格式）',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'API 名称',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'API 功能描述',
  `url` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'API 请求地址（URL）',
  `method` enum('GET','POST','PUT','DELETE','PATCH') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'HTTP 请求方法',
  `headers` json NULL COMMENT '请求头信息（JSON 格式，可选）',
  `params` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '请求参数定义',
  `request_body` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '请求体内容',
  `request_schema` json NULL COMMENT '请求体结构定义（JSON Schema 格式）',
  `response_schema` json NULL COMMENT '响应体结构定义（JSON Schema 格式）',
  `request_demo` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '请求示例',
  `response_demo` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '响应示例',
  `enabled` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用：0（禁用）、1（启用）',
  `is_deleted` tinyint NOT NULL DEFAULT 0 COMMENT '是否逻辑删除：0（正常）、1（已删除）',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录最后更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_tool_id` (`tool_id` ASC) USING BTREE COMMENT '工具 ID 唯一索引'
) ENGINE = InnoDB AUTO_INCREMENT = 6634 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = 'MCP 工具 API 注册表，用于存储 API 的详细信息及配置' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for sys_config
-- ----------------------------
DROP TABLE IF EXISTS `sys_config`;
CREATE TABLE `sys_config` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键，自增唯一标识',
  `key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '配置键名',
  `value` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '配置值',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '配置项描述',
  `created_at` timestamp NULL DEFAULT NULL COMMENT '记录创建时间',
  `updated_at` timestamp NULL DEFAULT NULL COMMENT '记录最后更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_key` (`key` ASC) USING BTREE COMMENT '配置键名唯一索引'
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '系统参数配置表，用于存储系统级配置信息' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键，自增唯一标识',
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户唯一标识（UUID 格式）',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户名',
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户邮箱地址',
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户头像 URL',
  `is_active` tinyint NOT NULL DEFAULT 1 COMMENT '用户状态：0（停用）、1（正常）',
  `is_deleted` tinyint NOT NULL COMMENT '是否逻辑删除：0（正常）、1（已删除）',
  `register_type` enum('google','email') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '注册方式：google（谷歌账号）、email（邮箱注册）',
  `role_id` int NOT NULL COMMENT '角色 ID：1（管理员）、2（普通用户）',
  `last_login_at` timestamp NULL DEFAULT NULL COMMENT '最近登录时间',
  `last_login_ip` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '最近登录 IP 地址',
  `created_at` timestamp NULL DEFAULT NULL COMMENT '记录创建时间',
  `updated_at` timestamp NULL DEFAULT NULL COMMENT '记录最后更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_email` (`email` ASC) USING BTREE COMMENT '邮箱地址唯一索引',
  UNIQUE INDEX `uk_user_id` (`user_id` ASC) USING BTREE COMMENT '用户 ID 唯一索引'
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户信息表，用于存储用户基本信息及状态' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_access_token
-- ----------------------------
DROP TABLE IF EXISTS `user_access_token`;
CREATE TABLE `user_access_token` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键，自增唯一标识',
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户唯一标识（UUID 格式）',
  `token` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '访问令牌',
  `expire_at` timestamp NOT NULL COMMENT '令牌过期时间',
  `created_at` timestamp NULL DEFAULT NULL COMMENT '记录创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_token` (`token` ASC) USING BTREE COMMENT '访问令牌唯一索引'
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户访问令牌表，用于存储用户认证令牌信息' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_wallet
-- ----------------------------
DROP TABLE IF EXISTS `user_wallet`;
CREATE TABLE `user_wallet` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键，自增唯一标识',
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户唯一标识（UUID 格式）',
  `balance` decimal(10,2) NOT NULL COMMENT '钱包余额（保留两位小数）',
  `frozen_balance` decimal(10,2) NOT NULL COMMENT '冻结余额（保留两位小数）',
  `created_at` timestamp NULL DEFAULT NULL COMMENT '记录创建时间',
  `updated_at` timestamp NULL DEFAULT NULL COMMENT '记录最后更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_id` (`user_id` ASC) USING BTREE COMMENT '用户 ID 唯一索引'
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户钱包表，用于存储用户余额及冻结金额信息' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_wallet_history
-- ----------------------------
DROP TABLE IF EXISTS `user_wallet_history`;
CREATE TABLE `user_wallet_history` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键，自增唯一标识',
  `history_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '变更记录唯一标识（UUID 格式）',
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户唯一标识（UUID 格式）',
  `payment_method` enum('platform','stripe','alipay','wechat') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '支付方式：platform（平台）、stripe（Stripe）、alipay（支付宝）、wechat（微信）',
  `amount` decimal(10,2) NOT NULL COMMENT '变更金额（正数表示充值，负数表示扣费/消费，保留两位小数）',
  `balance_after` decimal(10,2) NOT NULL COMMENT '变更后余额（保留两位小数）',
  `type` enum('deposit','consume','refund') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '变更类型：deposit（充值）、consume（消费）、refund（退款）',
  `status` tinyint NOT NULL COMMENT '订单状态：0（新建）、1（已完成）、2（待完成）',
  `transaction_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '支付平台交易标识',
  `channel_user_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '支付渠道用户标识',
  `callback_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '支付回调信息',
  `created_at` timestamp NULL DEFAULT NULL COMMENT '记录创建时间',
  `updated_at` timestamp NULL DEFAULT NULL COMMENT '记录最后更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_transaction_id` (`transaction_id` ASC) USING BTREE COMMENT '交易 ID 唯一索引'
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户钱包变更记录表，用于记录用户钱包的充值、消费和退款历史' ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;