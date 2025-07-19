-- 初始化 Stripe 支付渠道配置示例
-- 在 payment_channel 表中插入 Stripe 配置

INSERT INTO `payment_channel` (`id`, `name`, `status`, `config`, `update_at`) 
VALUES (
    'stripe',
    'Stripe支付',
    1,  -- 启用状态
    '{"secret": "sk_live12345622222", "webhook_secret": "77582587777778"}',
    NOW()
) ON DUPLICATE KEY UPDATE 
    `name` = VALUES(`name`),
    `config` = VALUES(`config`),
    `update_at` = NOW();

-- 如果需要更新现有配置，可以使用以下语句：
-- UPDATE `payment_channel` 
-- SET `config` = '{"secret": "sk_live12345622222", "webhook_secret": "77582587777778"}',
--     `update_at` = NOW()
-- WHERE `id` = 'stripe';
