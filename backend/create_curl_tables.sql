-- 创建curl_tasks表
CREATE TABLE IF NOT EXISTS `curl_tasks` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `project_id` INT NOT NULL,
    `name` VARCHAR(200) NOT NULL COMMENT '任务名称',
    `curl_command` TEXT NOT NULL COMMENT 'curl命令',
    `extract_pattern` VARCHAR(500) DEFAULT NULL COMMENT '提取模式（正则表达式）',
    `schedule_type` ENUM('manual', 'interval', 'cron') DEFAULT 'manual' COMMENT '调度类型',
    `schedule_config` TEXT DEFAULT NULL COMMENT '调度配置（JSON）',
    `enabled` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    `last_run_time` DATETIME DEFAULT NULL COMMENT '上次运行时间',
    `last_run_status` ENUM('success', 'failed', 'running') DEFAULT NULL COMMENT '上次运行状态',
    `last_run_result` TEXT DEFAULT NULL COMMENT '上次运行结果',
    `assets_extracted` INT DEFAULT 0 COMMENT '提取的资产数量',
    `created_by` INT NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_enabled (enabled),
    INDEX idx_schedule_type (schedule_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='curl任务表';

-- 创建curl_task_logs表
CREATE TABLE IF NOT EXISTS `curl_task_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `task_id` INT NOT NULL,
    `status` ENUM('success', 'failed') NOT NULL COMMENT '执行状态',
    `response_content` LONGTEXT DEFAULT NULL COMMENT '响应内容',
    `assets_extracted` INT DEFAULT 0 COMMENT '提取的资产数量',
    `error_message` TEXT DEFAULT NULL COMMENT '错误信息',
    `execution_time` INT DEFAULT 0 COMMENT '执行时间（毫秒）',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES curl_tasks(id) ON DELETE CASCADE,
    INDEX idx_task_id (task_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='curl任务执行日志表';
