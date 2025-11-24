<template>
  <div class="admin-panel">
    <div class="admin-header">
      <h1>超级管理员控制台</h1>
      <el-button type="primary" @click="goBack">返回主页</el-button>
    </div>

    <el-tabs v-model="activeTab" class="admin-tabs">
      <el-tab-pane label="系统概览" name="stats">
        <el-row :gutter="20" class="stats-row">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-icon users-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.total_users }}</div>
                <div class="stat-label">总用户数</div>
                <div class="stat-trend">最近7天: +{{ stats.recent_users }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-icon projects-icon">
                <el-icon><Folder /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.total_projects }}</div>
                <div class="stat-label">总项目数</div>
                <div class="stat-trend">最近7天: +{{ stats.recent_projects }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-icon assets-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.total_assets }}</div>
                <div class="stat-label">总资产数</div>
                <div class="stat-trend">&nbsp;</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-icon vulns-icon">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.total_vulnerabilities }}</div>
                <div class="stat-label">总漏洞数</div>
                <div class="stat-trend">&nbsp;</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="用户管理" name="users">
        <div class="table-header">
          <h3>用户列表</h3>
          <div>
            <el-button type="success" @click="showCreateUserDialog">
              <el-icon><Plus /></el-icon> 创建用户
            </el-button>
            <el-button type="primary" @click="loadUsers" :loading="usersLoading">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
        </div>
        
        <el-table :data="users" style="width: 100%" v-loading="usersLoading">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" width="200" />
          <el-table-column label="角色" width="150">
            <template #default="scope">
              <el-tag v-if="scope.row.is_super_admin" type="danger" size="small">超级管理员</el-tag>
              <el-tag v-else-if="scope.row.is_admin" type="warning" size="small">管理员</el-tag>
              <el-tag v-else type="info" size="small">普通用户</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="project_count" label="项目数" width="100" />
          <el-table-column prop="asset_count" label="资产数" width="100" />
          <el-table-column prop="created_at" label="注册时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="400">
            <template #default="scope">
              <el-button 
                size="small" 
                type="primary"
                @click="showEditUserDialog(scope.row)"
              >
                编辑
              </el-button>
              <el-button 
                size="small" 
                :type="scope.row.is_super_admin ? 'danger' : 'success'"
                @click="toggleSuperAdmin(scope.row)"
                :disabled="scope.row.id === currentUser.id"
              >
                {{ scope.row.is_super_admin ? '取消超管' : '设为超管' }}
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteUser(scope.row)"
                :disabled="scope.row.id === currentUser.id"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="项目管理" name="projects">
        <div class="table-header">
          <h3>所有项目</h3>
          <el-button type="primary" @click="loadProjects" :loading="projectsLoading">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
        
        <el-table :data="projects" style="width: 100%" v-loading="projectsLoading">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="项目名称" width="200" />
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column prop="creator_name" label="创建者" width="150" />
          <el-table-column prop="asset_count" label="资产数" width="100" />
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button 
                size="small" 
                type="primary" 
                @click="viewProject(scope.row.id)"
              >
                查看
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteProject(scope.row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="系统设置" name="settings">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <span>系统配置</span>
              <el-button type="primary" @click="saveSettings" :loading="settingsLoading">
                保存设置
              </el-button>
            </div>
          </template>
          
          <el-form :model="settings" label-width="150px">
            <el-form-item label="网站名称">
              <el-input v-model="settings.site_name" placeholder="请输入网站名称" />
            </el-form-item>
            
            <el-form-item label="网站描述">
              <el-input v-model="settings.site_description" placeholder="请输入网站描述" />
            </el-form-item>
            
            <el-form-item label="允许用户注册">
              <el-switch 
                v-model="settings.allow_registration" 
                active-text="开启" 
                inactive-text="关闭"
              />
              <div class="form-tip">
                关闭后，新用户只能通过邀请码注册
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog 
      v-model="createUserDialogVisible" 
      title="创建新用户" 
      width="500px"
      @close="resetCreateUserForm"
    >
      <el-form :model="createUserForm" label-width="100px">
        <el-form-item label="用户名" required>
          <el-input 
            v-model="createUserForm.username" 
            placeholder="请输入用户名（3-50个字符）"
            maxlength="50"
          />
        </el-form-item>
        <el-form-item label="密码" required>
          <el-input 
            v-model="createUserForm.password" 
            type="password" 
            placeholder="请输入密码（至少6个字符）"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-checkbox v-model="createUserForm.is_super_admin">超级管理员</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createUserDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createUser" :loading="createUserLoading">
          创建
        </el-button>
      </template>
    </el-dialog>

    <el-dialog 
      v-model="editUserDialogVisible" 
      title="编辑用户" 
      width="500px"
      @close="resetEditUserForm"
    >
      <el-form :model="editUserForm" label-width="100px">
        <el-form-item label="用户ID">
          <el-input v-model="editUserForm.id" disabled />
        </el-form-item>
        <el-form-item label="用户名" required>
          <el-input 
            v-model="editUserForm.username" 
            placeholder="请输入用户名（3-50个字符）"
            maxlength="50"
          />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input 
            v-model="editUserForm.password" 
            type="password" 
            placeholder="留空则不修改密码"
            show-password
          />
          <div class="form-tip">留空则不修改密码</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editUserDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="updateUser" :loading="editUserLoading">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Folder, Document, Warning, Refresh, Plus } from '@element-plus/icons-vue'
import request from '../utils/request'

export default {
  name: 'AdminPanel',
  components: {
    User,
    Folder,
    Document,
    Warning,
    Refresh,
    Plus
  },
  setup() {
    const router = useRouter()
    const activeTab = ref('stats')
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
    
    const stats = reactive({
      total_users: 0,
      total_projects: 0,
      total_assets: 0,
      total_vulnerabilities: 0,
      recent_users: 0,
      recent_projects: 0
    })
    
    const users = ref([])
    const usersLoading = ref(false)
    
    const projects = ref([])
    const projectsLoading = ref(false)
    
    const settings = reactive({
      site_name: '',
      site_description: '',
      allow_registration: true
    })
    const settingsLoading = ref(false)
    
    // 创建用户相关
    const createUserDialogVisible = ref(false)
    const createUserLoading = ref(false)
    const createUserForm = reactive({
      username: '',
      password: '',
      is_super_admin: false
    })
    
    // 编辑用户相关
    const editUserDialogVisible = ref(false)
    const editUserLoading = ref(false)
    const editUserForm = reactive({
      id: null,
      username: '',
      password: ''
    })
    
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN')
    }
    
    const goBack = () => {
      router.push('/dashboard')
    }
    
    // 加载统计信息
    const loadStats = async () => {
      try {
        const response = await request.get('/admin/stats', {
          params: { admin_id: currentUser.id }
        })
        if (response.success) {
          Object.assign(stats, response.stats)
        }
      } catch (error) {
        console.error('加载统计信息失败:', error)
      }
    }
    
    // 加载用户列表
    const loadUsers = async () => {
      usersLoading.value = true
      try {
        const response = await request.get('/admin/users', {
          params: { admin_id: currentUser.id }
        })
        if (response.success) {
          users.value = response.users
        }
      } catch (error) {
        ElMessage.error('加载用户列表失败')
      } finally {
        usersLoading.value = false
      }
    }
    
    // 切换超级管理员权限
    const toggleSuperAdmin = async (user) => {
      try {
        await ElMessageBox.confirm(
          `确定要${user.is_super_admin ? '取消' : '设置'} ${user.username} 的超级管理员权限吗？`,
          '提示',
          { type: 'warning' }
        )
        
        const response = await request.put(`/admin/users/${user.id}`, {
          admin_id: currentUser.id,
          is_super_admin: !user.is_super_admin
        })
        
        if (response.success) {
          ElMessage.success(response.message)
          loadUsers()
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('操作失败')
        }
      }
    }
    
    // 显示创建用户对话框
    const showCreateUserDialog = () => {
      createUserDialogVisible.value = true
    }
    
    // 重置创建用户表单
    const resetCreateUserForm = () => {
      createUserForm.username = ''
      createUserForm.password = ''
      createUserForm.is_super_admin = false
    }
    
    // 创建用户
    const createUser = async () => {
      if (!createUserForm.username || !createUserForm.password) {
        ElMessage.warning('请填写用户名和密码')
        return
      }
      
      if (createUserForm.username.length < 3 || createUserForm.username.length > 50) {
        ElMessage.warning('用户名长度必须在3-50个字符之间')
        return
      }
      
      if (createUserForm.password.length < 6) {
        ElMessage.warning('密码长度至少为6个字符')
        return
      }
      
      createUserLoading.value = true
      try {
        const response = await request.post('/admin/users', {
          admin_id: currentUser.id,
          username: createUserForm.username,
          password: createUserForm.password,
          is_super_admin: createUserForm.is_super_admin
        })
        
        if (response.success) {
          ElMessage.success(response.message)
          createUserDialogVisible.value = false
          resetCreateUserForm()
          loadUsers()
          loadStats()
        }
      } catch (error) {
        ElMessage.error(error.message || '创建用户失败')
      } finally {
        createUserLoading.value = false
      }
    }
    
    // 显示编辑用户对话框
    const showEditUserDialog = (user) => {
      editUserForm.id = user.id
      editUserForm.username = user.username
      editUserForm.password = ''
      editUserDialogVisible.value = true
    }
    
    // 重置编辑用户表单
    const resetEditUserForm = () => {
      editUserForm.id = null
      editUserForm.username = ''
      editUserForm.password = ''
    }
    
    // 更新用户
    const updateUser = async () => {
      if (!editUserForm.username) {
        ElMessage.warning('请填写用户名')
        return
      }
      
      if (editUserForm.username.length < 3 || editUserForm.username.length > 50) {
        ElMessage.warning('用户名长度必须在3-50个字符之间')
        return
      }
      
      if (editUserForm.password && editUserForm.password.length < 6) {
        ElMessage.warning('密码长度至少为6个字符')
        return
      }
      
      editUserLoading.value = true
      try {
        const updateData = {
          admin_id: currentUser.id,
          username: editUserForm.username
        }
        
        // 只有填写了密码才更新密码
        if (editUserForm.password) {
          updateData.password = editUserForm.password
        }
        
        const response = await request.put(`/admin/users/${editUserForm.id}`, updateData)
        
        if (response.success) {
          ElMessage.success(response.message)
          editUserDialogVisible.value = false
          resetEditUserForm()
          loadUsers()
        }
      } catch (error) {
        ElMessage.error(error.message || '更新用户失败')
      } finally {
        editUserLoading.value = false
      }
    }
    
    // 删除用户
    const deleteUser = async (user) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除用户 ${user.username} 吗？此操作将同时删除该用户创建的所有项目和资产！`,
          '警告',
          { type: 'error', confirmButtonText: '确定删除' }
        )
        
        const response = await request.delete(`/admin/users/${user.id}`, {
          params: { admin_id: currentUser.id }
        })
        
        if (response.success) {
          ElMessage.success(response.message)
          loadUsers()
          loadStats()
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
    }
    
    // 加载项目列表
    const loadProjects = async () => {
      projectsLoading.value = true
      try {
        const response = await request.get('/admin/projects', {
          params: { admin_id: currentUser.id }
        })
        if (response.success) {
          projects.value = response.projects
        }
      } catch (error) {
        ElMessage.error('加载项目列表失败')
      } finally {
        projectsLoading.value = false
      }
    }
    
    // 查看项目
    const viewProject = (projectId) => {
      router.push(`/project/${projectId}`)
    }
    
    // 删除项目
    const deleteProject = async (project) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除项目 ${project.name} 吗？此操作将同时删除该项目的所有资产！`,
          '警告',
          { type: 'error', confirmButtonText: '确定删除' }
        )
        
        const response = await request.delete(`/admin/projects/${project.id}`, {
          params: { admin_id: currentUser.id }
        })
        
        if (response.success) {
          ElMessage.success(response.message)
          loadProjects()
          loadStats()
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
    }
    
    // 加载系统设置
    const loadSettings = async () => {
      try {
        const response = await request.get('/admin/settings', {
          params: { admin_id: currentUser.id }
        })
        if (response.success) {
          const settingsData = response.settings
          settings.site_name = settingsData.site_name?.value || ''
          settings.site_description = settingsData.site_description?.value || ''
          settings.allow_registration = settingsData.allow_registration?.value === 'true'
        }
      } catch (error) {
        ElMessage.error('加载系统设置失败')
      }
    }
    
    // 保存系统设置
    const saveSettings = async () => {
      settingsLoading.value = true
      try {
        const response = await request.put('/admin/settings', {
          admin_id: currentUser.id,
          settings: {
            site_name: settings.site_name,
            site_description: settings.site_description,
            allow_registration: settings.allow_registration ? 'true' : 'false'
          }
        })
        
        if (response.success) {
          ElMessage.success(response.message)
        }
      } catch (error) {
        ElMessage.error('保存设置失败')
      } finally {
        settingsLoading.value = false
      }
    }
    
    onMounted(() => {
      loadStats()
      loadUsers()
      loadProjects()
      loadSettings()
    })
    
    return {
      activeTab,
      currentUser,
      stats,
      users,
      usersLoading,
      projects,
      projectsLoading,
      settings,
      settingsLoading,
      createUserDialogVisible,
      createUserLoading,
      createUserForm,
      editUserDialogVisible,
      editUserLoading,
      editUserForm,
      formatDate,
      goBack,
      loadUsers,
      toggleSuperAdmin,
      showCreateUserDialog,
      resetCreateUserForm,
      createUser,
      showEditUserDialog,
      resetEditUserForm,
      updateUser,
      deleteUser,
      loadProjects,
      viewProject,
      deleteProject,
      saveSettings
    }
  }
}
</script>

<style scoped>
.admin-panel {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.admin-header h1 {
  margin: 0;
  font-size: 28px;
  color: #303133;
}

.admin-tabs {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stats-row {
  margin-top: 20px;
}

.stat-card {
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.users-icon {
  color: #409EFF;
}

.projects-icon {
  color: #67C23A;
}

.assets-icon {
  color: #E6A23C;
}

.vulns-icon {
  color: #F56C6C;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-trend {
  font-size: 12px;
  color: #67C23A;
  /* 【修改点】添加固定高度 */
  height: 17px;
  line-height: 17px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.settings-card {
  max-width: 800px;
  margin: 20px auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>