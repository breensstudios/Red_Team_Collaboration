<template>
  <div class="settings-container">
    <div class="settings-header">
      <div class="header-left">
        <el-button icon="ArrowLeft" @click="goBack">返回</el-button>
        <h1>个人设置</h1>
      </div>
    </div>
    
    <div class="settings-content">
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>
        
        <el-form :model="userForm" label-width="100px" class="settings-form">
          <el-form-item label="用户ID">
            <el-input v-model="userForm.id" disabled />
          </el-form-item>
          
          <el-form-item label="当前用户名">
            <el-input v-model="userForm.username" disabled />
          </el-form-item>
          
          <el-form-item label="注册时间">
            <el-input v-model="formattedCreatedAt" disabled />
          </el-form-item>
        </el-form>
      </el-card>
      
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <span>修改用户名</span>
          </div>
        </template>
        
        <el-form
          ref="usernameFormRef"
          :model="usernameForm"
          :rules="usernameRules"
          label-width="100px"
          class="settings-form"
        >
          <el-form-item label="新用户名" prop="newUsername">
            <el-input
              v-model="usernameForm.newUsername"
              placeholder="请输入新用户名（3-50个字符）"
              clearable
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              @click="handleUpdateUsername"
              :loading="usernameLoading"
            >
              保存修改
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <span>邀请码管理</span>
          </div>
        </template>
        
        <div class="invite-section">
          <el-alert
            title="邀请协作"
            type="info"
            :closable="false"
            style="margin-bottom: 20px;"
          >
            <p>生成邀请码，邀请其他用户加入您的协作团队</p>
            <p>通过邀请码注册的用户可以查看和管理您的所有项目</p>
          </el-alert>
          
          <el-button
            type="primary"
            icon="Plus"
            @click="handleGenerateInviteCode"
            :loading="inviteLoading"
            style="margin-bottom: 20px;"
          >
            生成新邀请码
          </el-button>
          
          <el-table :data="inviteCodes" border style="width: 100%">
            <el-table-column prop="code" label="邀请码" min-width="200">
              <template #default="{ row }">
                <el-text copyable>{{ row.code }}</el-text>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="is_used" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.is_used ? 'info' : 'success'">
                  {{ row.is_used ? '已使用' : '未使用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="邀请链接" width="120" align="center">
              <template #default="{ row }">
                <el-button
                  size="small"
                  @click="copyInviteLink(row.code)"
                  :disabled="row.is_used"
                >
                  复制链接
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div style="margin-top: 20px;">
            <h4>协作成员 ({{ collaborators.length }})</h4>
            <el-table :data="collaborators" border style="width: 100%; margin-top: 10px;">
              <el-table-column prop="username" label="用户名" />
              <el-table-column prop="created_at" label="加入时间" width="180">
                <template #default="{ row }">
                  {{ formatTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" align="center">
                <template #default="{ row }">
                  <el-button
                    type="danger"
                    size="small"
                    @click="handleDeleteCollaborator(row.id)"
                    :loading="deletingCollaboratorId === row.id"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-card>
      
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <span>修改密码</span>
          </div>
        </template>
        
        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-width="100px"
          class="settings-form"
        >
          <el-form-item label="旧密码" prop="oldPassword">
            <el-input
              v-model="passwordForm.oldPassword"
              type="password"
              placeholder="请输入旧密码"
              show-password
              clearable
            />
          </el-form-item>
          
          <el-form-item label="新密码" prop="newPassword">
            <el-input
              v-model="passwordForm.newPassword"
              type="password"
              placeholder="请输入新密码（至少6个字符）"
              show-password
              clearable
            />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="passwordForm.confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
              show-password
              clearable
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              @click="handleUpdatePassword"
              :loading="passwordLoading"
            >
              修改密码
            </el-button>
            <el-button @click="resetPasswordForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'

export default {
  name: 'UserSettings',
  setup() {
    const router = useRouter()
    const usernameFormRef = ref(null)
    const passwordFormRef = ref(null)
    const usernameLoading = ref(false)
    const passwordLoading = ref(false)
    const inviteLoading = ref(false)
    const inviteCodes = ref([])
    const collaborators = ref([])
    const deletingCollaboratorId = ref(null)
    
    const currentUser = computed(() => {
      const user = localStorage.getItem('user')
      return user ? JSON.parse(user) : {}
    })
    
    const userForm = reactive({
      id: '',
      username: '',
      created_at: ''
    })
    
    const usernameForm = reactive({
      newUsername: ''
    })
    
    const passwordForm = reactive({
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    const usernameRules = {
      newUsername: [
        { required: true, message: '请输入新用户名', trigger: 'blur' },
        { min: 3, max: 50, message: '用户名长度必须在3-50个字符之间', trigger: 'blur' }
      ]
    }
    
    const passwordRules = {
      oldPassword: [
        { required: true, message: '请输入旧密码', trigger: 'blur' }
      ],
      newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入新密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== passwordForm.newPassword) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }
    
    const formattedCreatedAt = computed(() => {
      if (!userForm.created_at) return ''
      const date = new Date(userForm.created_at)
      return date.toLocaleString('zh-CN')
    })
    
    const loadUserInfo = async () => {
      try {
        const response = await request.get(`/users/${currentUser.value.id}`)
        if (response.success) {
          Object.assign(userForm, response.user)
        }
      } catch (error) {
        console.error('Load user info error:', error)
        ElMessage.error('加载用户信息失败')
      }
    }
    
    const handleUpdateUsername = async () => {
      try {
        await usernameFormRef.value.validate()
        
        if (usernameForm.newUsername === userForm.username) {
          ElMessage.warning('新用户名与当前用户名相同')
          return
        }
        
        usernameLoading.value = true
        
        const response = await request.put(`/users/${currentUser.value.id}/username`, {
          username: usernameForm.newUsername
        })
        
        ElMessage.success(response.message)
        
        // 更新本地存储的用户信息
        const updatedUser = {
          ...currentUser.value,
          username: usernameForm.newUsername
        }
        localStorage.setItem('user', JSON.stringify(updatedUser))
        
        // 刷新用户信息
        await loadUserInfo()
        usernameForm.newUsername = ''
        
      } catch (error) {
        console.error('Update username error:', error)
      } finally {
        usernameLoading.value = false
      }
    }
    
    const handleUpdatePassword = async () => {
      try {
        await passwordFormRef.value.validate()
        
        passwordLoading.value = true
        
        const response = await request.put(`/users/${currentUser.value.id}/password`, {
          old_password: passwordForm.oldPassword,
          new_password: passwordForm.newPassword
        })
        
        ElMessage.success(response.message + '，请重新登录')
        
        // 清除本地存储，跳转到登录页
        setTimeout(() => {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          router.push('/login')
        }, 1500)
        
      } catch (error) {
        console.error('Update password error:', error)
      } finally {
        passwordLoading.value = false
      }
    }
    
    const resetPasswordForm = () => {
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
      passwordFormRef.value?.clearValidate()
    }
    
    const loadInviteCodes = async () => {
      try {
        const response = await request.get(`/users/${currentUser.value.id}/invite-codes`)
        if (response.success) {
          inviteCodes.value = response.invite_codes
        }
      } catch (error) {
        console.error('Load invite codes error:', error)
      }
    }
    
    const loadCollaborators = async () => {
      try {
        const response = await request.get(`/users/${currentUser.value.id}/collaborators`)
        if (response.success) {
          collaborators.value = response.collaborators
        }
      } catch (error) {
        console.error('Load collaborators error:', error)
      }
    }
    
    const handleGenerateInviteCode = async () => {
      try {
        inviteLoading.value = true
        const response = await request.post(`/users/${currentUser.value.id}/invite-code`)
        ElMessage.success(response.message)
        await loadInviteCodes()
      } catch (error) {
        console.error('Generate invite code error:', error)
      } finally {
        inviteLoading.value = false
      }
    }
    
    const copyInviteLink = (code) => {
      const link = `${window.location.origin}/login?invite_code=${code}`
      
      // 检查 clipboard API 是否可用
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(link).then(() => {
          ElMessage.success('邀请链接已复制到剪贴板')
        }).catch(() => {
          fallbackCopy(link)
        })
      } else {
        // 降级方案：使用传统方法
        fallbackCopy(link)
      }
    }
    
    const fallbackCopy = (text) => {
      const textarea = document.createElement('textarea')
      textarea.value = text
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      try {
        document.execCommand('copy')
        ElMessage.success('邀请链接已复制到剪贴板')
      } catch (err) {
        ElMessage.error('复制失败，请手动复制: ' + text)
      }
      document.body.removeChild(textarea)
    }
    
    const formatTime = (time) => {
      if (!time) return ''
      const date = new Date(time)
      return date.toLocaleString('zh-CN')
    }
    
    const handleDeleteCollaborator = async (collaboratorId) => {
      try {
        await ElMessageBox.confirm(
          '确定要删除该协作者吗？删除后该用户将无法访问您的项目。',
          '删除协作者',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        deletingCollaboratorId.value = collaboratorId
        
        const response = await request.delete(
          `/users/${currentUser.value.id}/collaborators/${collaboratorId}`
        )
        
        ElMessage.success(response.message)
        await loadCollaborators()
        
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Delete collaborator error:', error)
        }
      } finally {
        deletingCollaboratorId.value = null
      }
    }
    
    const goBack = () => {
      router.push('/dashboard')
    }
    
    onMounted(() => {
      loadUserInfo()
      loadInviteCodes()
      loadCollaborators()
    })
    
    return {
      usernameFormRef,
      passwordFormRef,
      usernameLoading,
      passwordLoading,
      inviteLoading,
      inviteCodes,
      collaborators,
      deletingCollaboratorId,
      userForm,
      usernameForm,
      passwordForm,
      usernameRules,
      passwordRules,
      formattedCreatedAt,
      handleUpdateUsername,
      handleUpdatePassword,
      handleGenerateInviteCode,
      handleDeleteCollaborator,
      copyInviteLink,
      formatTime,
      resetPasswordForm,
      goBack
    }
  }
}
</script>

<style lang="scss" scoped>
.settings-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  
  .settings-header {
    height: 70px;
    background: white;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 30px;
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 15px;
      
      h1 {
        font-size: 20px;
        color: #333;
        margin: 0;
      }
    }
  }
  
  .settings-content {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
    
    .settings-card {
      max-width: 800px;
      margin: 0 auto 20px;
      
      .card-header {
        font-size: 16px;
        font-weight: 600;
        color: #333;
      }
      
      .settings-form {
        padding: 20px 0;
        
        :deep(.el-form-item__label) {
          font-weight: 500;
        }
        
        :deep(.el-input) {
          max-width: 400px;
        }
      }
    }
  }
}
</style>
