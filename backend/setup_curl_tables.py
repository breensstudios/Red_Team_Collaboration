#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速创建curl任务表
"""

import pymysql
import json
import os

CONFIG_FILE = 'config.json'

print("=" * 80)
print("创建curl任务表")
print("=" * 80)
print()

# 加载配置
if not os.path.exists(CONFIG_FILE):
    print("❌ 配置文件不存在")
    exit(1)

with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = json.load(f)

print(f"数据库: {config['db_name']}")
print()

try:
    # 连接数据库
    conn = pymysql.connect(
        host=config['db_host'],
        user=config['db_user'],
        password=config['db_password'],
        database=config['db_name'],
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # 创建curl_tasks表
    print("创建 curl_tasks 表...")
    cursor.execute("""
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
        COMMENT='curl任务表'
    """)
    print("✅ curl_tasks 表创建成功")
    
    # 创建curl_task_logs表
    print("创建 curl_task_logs 表...")
    cursor.execute("""
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
        COMMENT='curl任务执行日志表'
    """)
    print("✅ curl_task_logs 表创建成功")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print()
    print("=" * 80)
    print("✅ 所有表创建成功！")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ 错误: {str(e)}")
    exit(1)
