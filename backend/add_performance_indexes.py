#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化脚本：为数据库添加索引以提升查询性能
"""

import pymysql
import json
import os

# 读取配置
CONFIG_FILE = 'config.json'

if not os.path.exists(CONFIG_FILE):
    print("❌ 配置文件不存在，请先安装系统")
    exit(1)

with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = json.load(f)

print("=" * 80)
print("数据库性能优化 - 添加索引")
print("=" * 80)
print()

try:
    # 连接数据库
    conn = pymysql.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database'],
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # 检查并添加索引的函数
    def add_index_if_not_exists(table, index_name, columns, index_type='INDEX'):
        try:
            # 检查索引是否存在
            cursor.execute(f"""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = %s
                AND INDEX_NAME = %s
            """, (config['database'], table, index_name))
            
            result = cursor.fetchone()
            if result[0] > 0:
                print(f"⚠️  索引 {index_name} 已存在，跳过")
                return False
            
            # 创建索引
            if index_type == 'FULLTEXT':
                sql = f"ALTER TABLE {table} ADD FULLTEXT INDEX {index_name} ({columns})"
            else:
                sql = f"ALTER TABLE {table} ADD INDEX {index_name} ({columns})"
            
            print(f"创建索引: {index_name} on {table}({columns})...")
            cursor.execute(sql)
            print(f"✅ 索引 {index_name} 创建成功")
            return True
        except Exception as e:
            print(f"❌ 创建索引 {index_name} 失败: {str(e)}")
            return False
    
    print("=" * 80)
    print("优化 assets 表")
    print("=" * 80)
    
    # 1. 组合索引：project_id + asset_type（常用组合查询）
    add_index_if_not_exists('assets', 'idx_project_type', 'project_id, asset_type')
    
    # 2. 组合索引：project_id + status（按状态筛选）
    add_index_if_not_exists('assets', 'idx_project_status', 'project_id, status')
    
    # 3. 组合索引：project_id + risk_level（按风险等级筛选）
    add_index_if_not_exists('assets', 'idx_project_risk', 'project_id, risk_level')
    
    # 4. 组合索引：project_id + created_at（分页排序）
    add_index_if_not_exists('assets', 'idx_project_created', 'project_id, created_at DESC')
    
    # 5. asset_value 索引（模糊搜索优化）
    add_index_if_not_exists('assets', 'idx_asset_value', 'asset_value(100)')
    
    # 6. port 索引（端口筛选）
    add_index_if_not_exists('assets', 'idx_port', 'port')
    
    # 7. protocol 索引（协议筛选）
    add_index_if_not_exists('assets', 'idx_protocol', 'protocol')
    
    # 8. created_by 索引（创建者筛选）
    add_index_if_not_exists('assets', 'idx_created_by', 'created_by')
    
    # 9. 组合索引：project_id + ip（IP筛选优化）
    add_index_if_not_exists('assets', 'idx_project_ip', 'project_id, ip')
    
    # 10. title 索引（标题搜索）
    add_index_if_not_exists('assets', 'idx_title', 'title(100)')
    
    print()
    print("=" * 80)
    print("优化 curl_tasks 表")
    print("=" * 80)
    
    # 11. 组合索引：project_id + enabled（启用状态筛选）
    add_index_if_not_exists('curl_tasks', 'idx_project_enabled', 'project_id, enabled')
    
    # 12. 组合索引：project_id + template_type（模板类型筛选）
    add_index_if_not_exists('curl_tasks', 'idx_project_template', 'project_id, template_type')
    
    # 13. last_run_time 索引（按运行时间排序）
    add_index_if_not_exists('curl_tasks', 'idx_last_run_time', 'last_run_time')
    
    # 14. last_run_status 索引（按运行状态筛选）
    add_index_if_not_exists('curl_tasks', 'idx_last_run_status', 'last_run_status')
    
    print()
    print("=" * 80)
    print("优化 curl_task_logs 表")
    print("=" * 80)
    
    # 15. 组合索引：task_id + created_at（日志查询优化）
    add_index_if_not_exists('curl_task_logs', 'idx_task_created', 'task_id, created_at DESC')
    
    print()
    print("=" * 80)
    print("优化 projects 表")
    print("=" * 80)
    
    # 16. created_by 索引（创建者筛选）
    add_index_if_not_exists('projects', 'idx_created_by', 'created_by')
    
    # 17. created_at 索引（按创建时间排序）
    add_index_if_not_exists('projects', 'idx_created_at', 'created_at DESC')
    
    # 18. name 索引（项目名称搜索）
    add_index_if_not_exists('projects', 'idx_name', 'name(50)')
    
    print()
    print("=" * 80)
    print("优化 users 表")
    print("=" * 80)
    
    # 19. username 已有唯一索引，无需添加
    print("⚠️  username 已有唯一索引，跳过")
    
    print()
    print("=" * 80)
    print("优化 invite_codes 表")
    print("=" * 80)
    
    # 20. 组合索引：user_id + is_used（邀请码查询优化）
    add_index_if_not_exists('invite_codes', 'idx_user_used', 'user_id, is_used')
    
    # 21. expires_at 索引（过期时间查询）
    add_index_if_not_exists('invite_codes', 'idx_expires_at', 'expires_at')
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print()
    print("=" * 80)
    print("✅ 索引优化完成！")
    print("=" * 80)
    print()
    print("建议：")
    print("1. 定期使用 ANALYZE TABLE 命令更新表统计信息")
    print("2. 监控慢查询日志，持续优化")
    print("3. 对于超大数据量，考虑分区表")
    print()
    
except Exception as e:
    print(f"❌ 错误: {str(e)}")
    exit(1)
