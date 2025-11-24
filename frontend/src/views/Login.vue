<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <img :src="logoImg" class="logo-img" alt="Logo" />
        <h1>红队资产协作平台</h1>
        <p>RED team Asset Collaboration Platform</p>
      </div>
      
      <el-tabs v-model="activeTab" class="login-tabs" stretch>
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                prefix-icon="User"
                size="large"
                class="minimal-input"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                size="large"
                show-password
                class="minimal-input"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="loginLoading"
                @click="handleLogin"
                class="login-btn"
                size="large"
                round
              >
                登 录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="注册" name="register">
          <el-alert
            v-if="!allowRegistration"
            title="系统当前不允许公开注册"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
          >
            <template #default>
              请联系管理员获取邀请码进行注册
            </template>
          </el-alert>
          
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名 (3-50个字符)"
                prefix-icon="User"
                size="large"
                class="minimal-input"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码 (至少6个字符)"
                prefix-icon="Lock"
                size="large"
                show-password
                class="minimal-input"
              />
            </el-form-item>
            
            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                prefix-icon="Lock"
                size="large"
                show-password
                class="minimal-input"
              />
            </el-form-item>
            
            <el-form-item prop="inviteCode">
              <el-input
                v-model="registerForm.inviteCode"
                placeholder="邀请码（可选）"
                prefix-icon="Ticket"
                size="large"
                class="minimal-input"
                @keyup.enter="handleRegister"
              />
            </el-form-item>
            
            <el-alert
              v-if="registerForm.inviteCode"
              title="将加入协作团队"
              type="success"
              :closable="false"
              show-icon
              class="minimal-alert"
            />
            
            <el-form-item>
              <el-button
                type="success"
                :loading="registerLoading"
                @click="handleRegister"
                class="login-btn"
                size="large"
                round
              >
                注 册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <div class="login-footer">
        <span @click="goToInstall">系统未安装？点击安装</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../utils/request'
// 引入图片：请确保 logo.jpg 在 src/assets/ 目录下
// 如果你的目录结构不同，请修改这里的路径
import logoImg from '../assets/logo.png'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const activeTab = ref('login')
    const loginFormRef = ref(null)
    const registerFormRef = ref(null)
    const loginLoading = ref(false)
    const registerLoading = ref(false)
    
    const loginForm = reactive({
      username: '',
      password: ''
    })
    
    const registerForm = reactive({
      username: '',
      password: '',
      confirmPassword: '',
      inviteCode: ''
    })
    
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    const loginRules = {
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
    }
    
    const registerRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 50, message: '用户名长度在3-50个字符之间', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码至少6个字符', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请确认密码', trigger: 'blur' },
        { validator: validateConfirmPassword, trigger: 'blur' }
      ]
    }
    
    const allowRegistration = ref(true)
    
    const checkInstall = async () => {
      try {
        const response = await request.get('/check-install')
        if (!response.installed) {
          ElMessage.warning('系统未安装，请先完成安装')
          router.push('/install')
        } else {
          // 检查是否允许注册
          const settingResponse = await request.get('/settings/registration')
          if (settingResponse.success) {
            allowRegistration.value = settingResponse.allow_registration
          }
        }
      } catch (error) {
        console.error('Check install error:', error)
      }
    }
    
    const handleLogin = async () => {
      try {
        await loginFormRef.value.validate()
        loginLoading.value = true
        
        const response = await request.post('/login', loginForm)
        
        // 保存JWT token和用户信息
        localStorage.setItem('token', response.token)
        localStorage.setItem('user', JSON.stringify(response.user))
        ElMessage.success(response.message)
        
        router.push('/dashboard')
      } catch (error) {
        console.error('Login error:', error)
      } finally {
        loginLoading.value = false
      }
    }
    
    const handleRegister = async () => {
      try {
        await registerFormRef.value.validate()
        registerLoading.value = true
        
        const payload = {
          username: registerForm.username,
          password: registerForm.password
        }
        
        if (registerForm.inviteCode) {
          payload.invite_code = registerForm.inviteCode
        }
        
        const response = await request.post('/register', payload)
        
        ElMessage.success(response.message)
        
        loginForm.username = registerForm.username
        loginForm.password = registerForm.password
        activeTab.value = 'login'
        
        registerForm.username = ''
        registerForm.password = ''
        registerForm.confirmPassword = ''
        registerForm.inviteCode = ''
      } catch (error) {
        console.error('Register error:', error)
      } finally {
        registerLoading.value = false
      }
    }
    
    const goToInstall = () => {
      router.push('/install')
    }
    
    onMounted(() => {
      checkInstall()
      
      const urlParams = new URLSearchParams(window.location.search)
      const inviteCode = urlParams.get('invite_code')
      if (inviteCode) {
        registerForm.inviteCode = inviteCode
        activeTab.value = 'register'
        ElMessage.info('检测到邀请码，请完成注册')
      }
    })
    
    return {
      activeTab,
      loginFormRef,
      registerFormRef,
      loginForm,
      registerForm,
      loginRules,
      registerRules,
      loginLoading,
      registerLoading,
      allowRegistration,
      handleLogin,
      handleRegister,
      goToInstall,
      logoImg // 导出图片变量
    }
  }
}
</script>

<style lang="scss" scoped>
/* 极简风格配色变量 */
$bg-color: #f5f7fa;
$card-bg: #ffffff;
$primary-color: #409eff;
$text-main: #303133;
$text-secondary: #909399;

.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $bg-color;
  background-image: radial-gradient(#e1e6ed 1px, transparent 1px);
  background-size: 20px 20px;
  
  .login-box {
    width: 400px;
    background: $card-bg;
    border-radius: 12px;
    padding: 40px 35px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.5);
    position: relative;
    transition: all 0.3s ease;
    
    &:hover {
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
    }
    
    .login-header {
      text-align: center;
      margin-bottom: 35px;
      
      /* Logo 样式 */
      .logo-img {
        height: 64px; /* 你可以根据实际效果调整这个高度 */
        width: auto;
        margin-bottom: 16px;
        display: block;
        margin-left: auto;
        margin-right: auto;
        object-fit: contain;
      }
      
      h1 {
        font-size: 24px;
        color: $text-main;
        margin-bottom: 8px;
        font-weight: 500;
        letter-spacing: 1px;
      }
      
      p {
        color: $text-secondary;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 400;
      }
    }
    
    .login-tabs {
      :deep(.el-tabs__nav-wrap::after) {
        height: 0;
      }
      
      :deep(.el-tabs__item) {
        font-size: 15px;
        color: $text-secondary;
        font-weight: 400;
        
        &.is-active {
          color: $primary-color;
          font-weight: 600;
        }
      }
      
      :deep(.el-tabs__active-bar) {
        height: 3px;
        border-radius: 3px;
      }
    }
    
    .login-form {
      margin-top: 25px;
      
      :deep(.el-input__wrapper) {
        box-shadow: 0 0 0 1px #dcdfe6 inset;
        background-color: #fbfbfb;
        transition: all 0.2s;
        
        &:hover {
          background-color: #fff;
        }
        
        &.is-focus {
          background-color: #fff;
          box-shadow: 0 0 0 1px $primary-color inset;
        }
      }

      .minimal-alert {
        margin-bottom: 20px;
        background-color: #f0f9eb;
        border: none;
      }
      
      .login-btn {
        width: 100%;
        height: 44px;
        font-size: 15px;
        letter-spacing: 4px;
        margin-top: 10px;
        font-weight: 500;
        box-shadow: 0 4px 10px rgba(64, 158, 255, 0.2);
        
        &:active {
          transform: translateY(1px);
        }
      }
    }
    
    .login-footer {
      text-align: center;
      margin-top: 25px;
      
      span {
        font-size: 13px;
        color: #909399;
        cursor: pointer;
        transition: color 0.3s;
        
        &:hover {
          color: $primary-color;
          text-decoration: underline;
        }
      }
    }
  }
}
</style>