<template>
  <div class="curl-tasks-container">
    <div class="header">
      <el-button icon="ArrowLeft" @click="goBack">返回</el-button>
      <h2>curl任务管理</h2>
      <el-button type="primary" icon="Plus" @click="showCreateDialog = true">创建任务</el-button>
    </div>
    
    <div class="content">
      <el-table :data="tasks" v-loading="loading" stripe border style="width: 100%">
        <el-table-column type="index" label="#" width="60" align="center" />
        
        <el-table-column prop="name" label="任务名称" min-width="150" />
        
        <el-table-column prop="curl_command" label="curl命令" min-width="300" show-overflow-tooltip />
        
        <el-table-column prop="extract_pattern" label="提取模式" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="schedule_type" label="调度类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.schedule_type === 'manual'" type="info">手动</el-tag>
            <el-tag v-else-if="row.schedule_type === 'interval'" type="success">定时</el-tag>
            <el-tag v-else-if="row.schedule_type === 'cron'" type="warning">Cron</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="enabled" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch 
              :model-value="row.enabled" 
              @click="toggleEnabled(row)" 
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="last_run_status" label="上次运行" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.last_run_status === 'success'" type="success">成功</el-tag>
            <el-tag v-else-if="row.last_run_status === 'failed'" type="danger">失败</el-tag>
            <el-tag v-else-if="row.last_run_status === 'running'" type="warning">运行中</el-tag>
            <span v-else style="color: #999;">-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="assets_extracted" label="提取资产数" width="110" align="center" />
        
        <el-table-column prop="last_run_time" label="上次运行时间" width="160">
          <template #default="{ row }">
            {{ row.last_run_time ? formatTime(row.last_run_time) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="250" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" icon="VideoPlay" @click="executeTask(row)" :loading="row.executing">
              执行
            </el-button>
            <el-button size="small" icon="Edit" @click="editTask(row)">编辑</el-button>
            <el-button size="small" icon="Document" @click="viewLogs(row)">日志</el-button>
            <el-button type="danger" size="small" icon="Delete" @click="deleteTask(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 创建/编辑任务对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingTask ? '编辑任务' : '创建任务'"
      width="700px"
    >
      <el-form :model="taskForm" label-width="120px">
        <el-form-item label="任务名称" required>
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="模板类型" required>
          <el-radio-group v-model="taskForm.template_type">
            <el-radio label="custom">自定义curl命令</el-radio>
            <el-radio label="lighthouse">灯塔导入</el-radio>
            <el-radio label="fofa">FOFA查询</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- 灯塔导入配置 -->
        <template v-if="taskForm.template_type === 'lighthouse'">
          <el-form-item label="灯塔URL" required>
            <el-input v-model="taskForm.lighthouse_url" placeholder="例如: https://xxxxx:5003" />
            <div style="color: #999; font-size: 12px; margin-top: 5px;">
              灯塔系统的访问地址（包含协议和端口）
            </div>
          </el-form-item>
          
          <el-form-item label="用户名" required>
            <el-input v-model="taskForm.lighthouse_username" placeholder="请输入灯塔系统用户名" />
          </el-form-item>
          
          <el-form-item label="密码" required>
            <el-input v-model="taskForm.lighthouse_password" type="password" placeholder="请输入灯塔系统密码" show-password />
          </el-form-item>
        </template>
        
        <!-- FOFA查询配置 -->
        <template v-if="taskForm.template_type === 'fofa'">
          <el-form-item label="Email" required>
            <el-input v-model="taskForm.fofa_email" placeholder="请输入FOFA账号Email" />
            <div style="color: #999; font-size: 12px; margin-top: 5px;">
              FOFA账号的注册邮箱
            </div>
          </el-form-item>
          
          <el-form-item label="API Key" required>
            <el-input v-model="taskForm.fofa_api_key" type="password" placeholder="请输入FOFA API Key" show-password />
            <div style="color: #999; font-size: 12px; margin-top: 5px;">
              在FOFA个人中心获取API Key
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="taskForm.save_fofa_credentials">
              保存FOFA凭证到我的账号，下次自动填充
            </el-checkbox>
          </el-form-item>
          
          <el-form-item label="查询模式" required>
            <el-radio-group v-model="taskForm.fofa_query_mode">
              <el-radio label="syntax">语法查询</el-radio>
              <el-radio label="batch">批量查询</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <!-- 语法查询模式 -->
          <el-form-item v-if="taskForm.fofa_query_mode === 'syntax'" label="查询语法" required>
            <el-input
              v-model="taskForm.fofa_query"
              type="textarea"
              :rows="3"
              placeholder="例如: domain=&quot;example.com&quot; || ip=&quot;1.1.1.1&quot;"
            />
            <div style="color: #999; font-size: 12px; margin-top: 5px;">
              FOFA查询语法，支持复杂查询条件<br/>
              域名格式: domain="xxx.com"，IP格式: ip="1.1.1.1"<br/>
              示例: domain="example.com" && port="443"
            </div>
          </el-form-item>
          
          <!-- 批量查询模式 -->
          <el-form-item v-if="taskForm.fofa_query_mode === 'batch'" label="批量输入" required>
            <el-input
              v-model="taskForm.fofa_batch_input"
              type="textarea"
              :rows="8"
              placeholder="每行一个域名或IP，例如：&#10;example.com&#10;test.com&#10;1.1.1.1&#10;2.2.2.2"
            />
            <div style="color: #999; font-size: 12px; margin-top: 5px;">
              每行输入一个域名或IP地址，系统会自动识别并拼接成FOFA查询语法<br/>
              支持域名（如 example.com）和IP地址（如 1.1.1.1）<br/>
              建议每次不超过20个目标
            </div>
          </el-form-item>
          
          <el-form-item label="返回字段">
            <el-input v-model="taskForm.fofa_fields" placeholder="默认: host,ip,port" />
            <div style="color: #999; font-size: 12px; margin-top: 5px;">
              可选字段，多个字段用逗号分隔，留空使用默认值
            </div>
          </el-form-item>
          
          <el-form-item label="查询数量">
            <el-input-number v-model="taskForm.fofa_size" :min="1" :max="10000" />
            <span style="margin-left: 10px;">条（最大10000）</span>
          </el-form-item>
          
          <el-form-item label="全量数据">
            <el-switch v-model="taskForm.fofa_full" />
            <span style="margin-left: 10px; color: #999; font-size: 12px;">
              默认搜索一年内数据，开启后搜索全部数据
            </span>
          </el-form-item>
        </template>
        
        <!-- 自定义curl命令配置 -->
        <template v-if="taskForm.template_type === 'custom'">
          <el-form-item label="curl命令" required>
            <el-input
              v-model="taskForm.curl_command"
              type="textarea"
              :rows="4"
              placeholder="例如: curl -X GET 'https://api.example.com/assets' -H 'Authorization: Bearer token'"
            />
            <div style="color: #E6A23C; font-size: 12px; margin-top: 5px;">
              ⚠️ 安全限制：只允许执行curl命令，不允许使用管道(|)、分号(;)、反引号(`)等特殊字符
            </div>
          </el-form-item>
          
          <el-form-item label="提取模式">
            <el-input
              v-model="taskForm.extract_pattern"
              placeholder="正则表达式，例如: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            />
            <div style="color: #999; font-size: 12px; margin-top: 5px;">
              使用正则表达式从响应内容中提取资产，留空则使用默认算法自动识别（按空格、逗号、分号分割）
            </div>
          </el-form-item>
        </template>
        
        <el-form-item label="调度类型">
          <el-radio-group v-model="taskForm.schedule_type">
            <el-radio label="manual">手动执行</el-radio>
            <el-radio label="interval">定时执行</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="taskForm.schedule_type === 'interval'" label="执行间隔">
          <el-input-number v-model="taskForm.interval_minutes" :min="1" :max="1440" />
          <span style="margin-left: 10px;">分钟</span>
        </el-form-item>
        
        <el-form-item label="启用">
          <el-switch v-model="taskForm.enabled" />
        </el-form-item>
        
        <el-form-item label="批量标签">
          <el-input 
            v-model="taskForm.batch_tags" 
            placeholder="输入标签，多个标签用逗号、空格或分号分隔，例如：重点资产,高危,测试"
          >
            <template #prefix>
              <span style="color: #909399;">#</span>
            </template>
          </el-input>
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">
            这些标签将自动添加到通过此任务导入的所有资产上
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTask" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 日志对话框 -->
    <el-dialog v-model="showLogsDialog" title="执行日志" width="900px">
      <el-table :data="logs" stripe border max-height="500">
        <el-table-column type="index" label="#" width="60" align="center" />
        
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'success'" type="success">成功</el-tag>
            <el-tag v-else type="danger">失败</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="assets_extracted" label="提取资产数" width="110" align="center" />
        
        <el-table-column prop="execution_time" label="执行时间" width="100" align="center">
          <template #default="{ row }">
            {{ row.execution_time }} ms
          </template>
        </el-table-column>
        
        <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="created_at" label="执行时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'

export default {
  name: 'CurlTasks',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const loading = ref(false)
    const saving = ref(false)
    const tasks = ref([])
    const logs = ref([])
    const showCreateDialog = ref(false)
    const showLogsDialog = ref(false)
    const editingTask = ref(null)
    
    const taskForm = ref({
      name: '',
      template_type: 'custom',
      lighthouse_url: '',
      lighthouse_username: '',
      lighthouse_password: '',
      fofa_email: '',
      fofa_api_key: '',
      fofa_query_mode: 'batch',
      fofa_query: '',
      fofa_batch_input: '',
      fofa_fields: 'host,ip,port',
      fofa_size: 100,
      fofa_full: false,
      save_fofa_credentials: false,
      curl_command: '',
      extract_pattern: '',
      schedule_type: 'manual',
      interval_minutes: 60,
      enabled: true,
      batch_tags: ''
    })
    
    // 加载FOFA凭证
    const loadFofaCredentials = async () => {
      try {
        const response = await request.get('/user/fofa-credentials')
        if (response.success && response.fofa_email) {
          taskForm.value.fofa_email = response.fofa_email
          taskForm.value.fofa_api_key = response.fofa_api_key
        }
      } catch (error) {
        console.error('Load FOFA credentials error:', error)
      }
    }
    
    // 保存FOFA凭证
    const saveFofaCredentials = async (email, apiKey) => {
      try {
        await request.put('/user/fofa-credentials', {
          fofa_email: email,
          fofa_api_key: apiKey
        })
      } catch (error) {
        console.error('Save FOFA credentials error:', error)
      }
    }
    
    const projectId = computed(() => route.params.id)
    
    const loadTasks = async () => {
      loading.value = true
      try {
        const response = await request.get(`/projects/${projectId.value}/curl-tasks`)
        tasks.value = response.tasks
      } catch (error) {
        console.error('Load tasks error:', error)
        ElMessage.error('加载任务列表失败')
      } finally {
        loading.value = false
      }
    }
    
    const saveTask = async () => {
      if (!taskForm.value.name) {
        ElMessage.warning('请填写任务名称')
        return
      }
      
      if (taskForm.value.template_type === 'custom' && !taskForm.value.curl_command) {
        ElMessage.warning('请填写curl命令')
        return
      }
      
      if (taskForm.value.template_type === 'lighthouse') {
        if (!taskForm.value.lighthouse_url || !taskForm.value.lighthouse_username || !taskForm.value.lighthouse_password) {
          ElMessage.warning('请填写完整的灯塔配置信息')
          return
        }
      }
      
      if (taskForm.value.template_type === 'fofa') {
        if (!taskForm.value.fofa_email || !taskForm.value.fofa_api_key) {
          ElMessage.warning('请填写完整的FOFA配置信息')
          return
        }
        
        if (taskForm.value.fofa_query_mode === 'syntax' && !taskForm.value.fofa_query) {
          ElMessage.warning('请输入查询语法')
          return
        }
        
        if (taskForm.value.fofa_query_mode === 'batch' && !taskForm.value.fofa_batch_input) {
          ElMessage.warning('请输入要查询的域名或IP')
          return
        }
      }
      
      saving.value = true
      try {
        // 如果选择保存FOFA凭证
        if (taskForm.value.template_type === 'fofa' && taskForm.value.save_fofa_credentials) {
          await saveFofaCredentials(taskForm.value.fofa_email, taskForm.value.fofa_api_key)
        }
        
        const data = {
          name: taskForm.value.name,
          template_type: taskForm.value.template_type,
          schedule_type: taskForm.value.schedule_type,
          enabled: taskForm.value.enabled
        }
        
        // 解析批量标签
        if (taskForm.value.batch_tags && taskForm.value.batch_tags.trim()) {
          const tags = taskForm.value.batch_tags
            .split(/[,;，；\s]+/)
            .map(tag => tag.trim())
            .filter(tag => tag.length > 0)
          data.batch_tags = tags
        }
        
        if (taskForm.value.template_type === 'lighthouse') {
          data.template_config = {
            url: taskForm.value.lighthouse_url,
            username: taskForm.value.lighthouse_username,
            password: taskForm.value.lighthouse_password
          }
        } else if (taskForm.value.template_type === 'fofa') {
          let finalQuery = ''
          
          if (taskForm.value.fofa_query_mode === 'syntax') {
            // 语法查询模式，直接使用用户输入的语法
            finalQuery = taskForm.value.fofa_query
          } else {
            // 批量查询模式，自动拼接语法
            const lines = taskForm.value.fofa_batch_input
              .split('\n')
              .map(line => line.trim())
              .filter(line => line.length > 0)
            
            if (lines.length === 0) {
              ElMessage.warning('请输入至少一个域名或IP')
              return
            }
            
            // 自动识别域名和IP，拼接成FOFA语法
            const queries = lines.map(line => {
              // 简单判断是否为IP地址（包含数字和点）
              const isIP = /^\d+\.\d+\.\d+\.\d+$/.test(line)
              if (isIP) {
                return `ip="${line}"`
              } else {
                return `domain="${line}"`
              }
            })
            
            finalQuery = queries.join(' || ')
          }
          
          data.template_config = {
            email: taskForm.value.fofa_email,
            api_key: taskForm.value.fofa_api_key,
            query: finalQuery,
            fields: taskForm.value.fofa_fields || 'host,ip,port',
            size: taskForm.value.fofa_size || 100,
            full: taskForm.value.fofa_full || false
          }
        } else {
          data.curl_command = taskForm.value.curl_command
          data.extract_pattern = taskForm.value.extract_pattern
        }
        
        if (taskForm.value.schedule_type === 'interval') {
          data.schedule_config = {
            interval_minutes: taskForm.value.interval_minutes
          }
        }
        
        if (editingTask.value) {
          await request.put(`/curl-tasks/${editingTask.value.id}`, data)
          ElMessage.success('任务更新成功')
        } else {
          await request.post(`/projects/${projectId.value}/curl-tasks`, data)
          ElMessage.success('任务创建成功')
        }
        
        showCreateDialog.value = false
        await loadTasks()
      } catch (error) {
        console.error('Save task error:', error)
        ElMessage.error('保存任务失败')
      } finally {
        saving.value = false
      }
    }
    
    const editTask = (task) => {
      editingTask.value = task
      
      let template_config = {}
      if (task.template_config) {
        try {
          template_config = typeof task.template_config === 'string' ? JSON.parse(task.template_config) : task.template_config
        } catch (e) {
          console.error('Parse template_config error:', e)
        }
      }
      
      // 解析查询语法，判断是语法模式还是批量模式
      let queryMode = 'syntax'
      let batchInput = ''
      const query = template_config.query || ''
      
      // 尝试解析是否为批量模式生成的语法
      if (query) {
        const parts = query.split(' || ')
        const allSimple = parts.every(part => {
          return /^(domain|ip)="[^"]+"$/.test(part.trim())
        })
        
        if (allSimple && parts.length > 0) {
          // 可能是批量模式，提取域名和IP
          queryMode = 'batch'
          batchInput = parts.map(part => {
            const match = part.match(/^(domain|ip)="([^"]+)"$/)
            return match ? match[2] : ''
          }).filter(v => v).join('\n')
        }
      }
      
      taskForm.value = {
        name: task.name,
        template_type: task.template_type || 'custom',
        lighthouse_url: template_config.url || '',
        lighthouse_username: template_config.username || '',
        lighthouse_password: template_config.password || '',
        fofa_email: template_config.email || '',
        fofa_api_key: template_config.api_key || '',
        fofa_query_mode: queryMode,
        fofa_query: queryMode === 'syntax' ? query : '',
        fofa_batch_input: batchInput,
        fofa_fields: template_config.fields || 'host,ip,port',
        fofa_size: template_config.size || 100,
        fofa_full: template_config.full || false,
        curl_command: task.curl_command || '',
        extract_pattern: task.extract_pattern || '',
        schedule_type: task.schedule_type,
        interval_minutes: task.schedule_config?.interval_minutes || 60,
        enabled: task.enabled
      }
      showCreateDialog.value = true
    }
    
    const deleteTask = async (task) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除任务 "${task.name}" 吗？`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await request.delete(`/curl-tasks/${task.id}`)
        ElMessage.success('任务删除成功')
        await loadTasks()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Delete task error:', error)
          ElMessage.error('删除任务失败')
        }
      }
    }
    
    const executeTask = async (task) => {
      task.executing = true
      try {
        const response = await request.post(`/curl-tasks/${task.id}/execute`)
        ElMessage.success(response.message)
        await loadTasks()
      } catch (error) {
        console.error('Execute task error:', error)
        ElMessage.error('执行任务失败')
      } finally {
        task.executing = false
      }
    }
    
    const toggleEnabled = async (task) => {
      const newEnabled = !task.enabled
      try {
        await request.put(`/curl-tasks/${task.id}`, {
          enabled: newEnabled
        })
        task.enabled = newEnabled
        ElMessage.success(newEnabled ? '任务已启用' : '任务已禁用')
      } catch (error) {
        console.error('Toggle enabled error:', error)
        ElMessage.error('更新状态失败')
      }
    }
    
    const viewLogs = async (task) => {
      try {
        const response = await request.get(`/curl-tasks/${task.id}/logs`)
        logs.value = response.logs
        showLogsDialog.value = true
      } catch (error) {
        console.error('Load logs error:', error)
        ElMessage.error('加载日志失败')
      }
    }
    
    const formatTime = (time) => {
      if (!time) return ''
      const date = new Date(time)
      return date.toLocaleString('zh-CN')
    }
    
    const goBack = () => {
      router.push(`/project/${projectId.value}`)
    }
    
    // 监听模板类型变化，切换到FOFA时自动加载凭证
    watch(() => taskForm.value.template_type, (newType) => {
      if (newType === 'fofa' && !taskForm.value.fofa_email) {
        loadFofaCredentials()
      }
    })
    
    onMounted(() => {
      loadTasks()
    })
    
    return {
      loading,
      saving,
      tasks,
      logs,
      showCreateDialog,
      showLogsDialog,
      editingTask,
      taskForm,
      loadTasks,
      saveTask,
      editTask,
      deleteTask,
      executeTask,
      toggleEnabled,
      viewLogs,
      formatTime,
      goBack,
      loadFofaCredentials
    }
  }
}
</script>

<style lang="scss" scoped>
.curl-tasks-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  
  .header {
    height: 70px;
    background: white;
    padding: 0 30px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    
    h2 {
      flex: 1;
      margin: 0;
      font-size: 20px;
      color: #303133;
    }
  }
  
  .content {
    flex: 1;
    padding: 20px;
    overflow: auto;
  }
}
</style>
