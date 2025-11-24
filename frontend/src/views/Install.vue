<template>
  <div class="install-container">
    <div class="tech-grid-bg"></div>
    <div class="tech-orb"></div>

    <div class="install-box">
      <div class="install-header">
        <div class="logo-area">
          <div class="logo-icon">
            <el-icon><SetUp /></el-icon>
          </div>
        </div>
        <h1>SYSTEM INITIALIZATION</h1>
        <p class="subtitle">系统初始化配置向导</p>
      </div>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="install-form"
      >
        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="Database Host" prop="host">
              <el-input v-model="form.host" placeholder="例如: 127.0.0.1" class="tech-input">
                <template #prefix><el-icon><Connection /></el-icon></template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Port" prop="port">
              <el-input v-model.number="form.port" placeholder="3306" class="tech-input" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="Username" prop="user">
          <el-input v-model="form.user" placeholder="数据库用户名" class="tech-input">
            <template #prefix><el-icon><User /></el-icon></template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="Password" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="数据库密码"
            show-password
            class="tech-input"
          >
            <template #prefix><el-icon><Lock /></el-icon></template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="Database Name" prop="database">
          <el-input v-model="form.database" placeholder="例如: asset_platform" class="tech-input">
             <template #prefix><el-icon><DataLine /></el-icon></template>
          </el-input>
        </el-form-item>
        
        <el-form-item style="margin-top: 30px;">
          <el-button
            type="primary"
            :loading="loading"
            @click="handleInstall"
            class="install-btn"
          >
            开始部署 / DEPLOY
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="install-tips">
        <div class="terminal-header">
           <span class="dot red"></span>
           <span class="dot yellow"></span>
           <span class="dot green"></span>
           <span class="term-title">system_log.txt</span>
        </div>
        <div class="terminal-body">
          <p>> 等待配置参数...</p>
          <p>> 安装完成后将自动构建数据结构</p>
          <p>> 默认管理员: <span class="highlight">admin</span> / <span class="highlight">admin123</span></p>
        </div>
      </div>
    </div>

    <div class="footer-copyright">
      SECURE ASSET PLATFORM © 2025
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../utils/request'
import { SetUp, Connection, User, Lock, DataLine } from '@element-plus/icons-vue' // 引入图标

export default {
  name: 'Install',
  components: { SetUp, Connection, User, Lock, DataLine },
  setup() {
    const router = useRouter()
    const formRef = ref(null)
    const loading = ref(false)
    
    const form = reactive({
      host: 'localhost',
      port: 3306,
      user: 'root',
      password: '',
      database: 'asset_platform'
    })
    
    const rules = {
      host: [{ required: true, message: '请输入数据库地址', trigger: 'blur' }],
      port: [{ required: true, message: '请输入端口', trigger: 'blur' }],
      user: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
      database: [{ required: true, message: '请输入数据库名', trigger: 'blur' }]
    }
    
    // 检查系统是否已安装
    const checkInstalled = async () => {
      try {
        const response = await request.get('/check-install')
        if (response.installed) {
          ElMessage.warning('系统已安装，无法访问安装页面')
          router.push('/login')
        }
      } catch (error) {
        console.error('Check install error:', error)
      }
    }
    
    const handleInstall = async () => {
      try {
        await formRef.value.validate()
        loading.value = true
        
        const response = await request.post('/install', form)
        
        ElMessage.success(response.message)
        
        setTimeout(() => {
          router.push('/login')
        }, 1500)
      } catch (error) {
        console.error('Install error:', error)
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      checkInstalled()
    })
    
    return {
      formRef,
      form,
      rules,
      loading,
      handleInstall
    }
  }
}
</script>

<style lang="scss" scoped>
/* 变量定义 - 白色科技风 */
$bg-color: #f5f7fa;
$card-bg: #ffffff;
$primary-color: #2b5afb;
$text-main: #2c3e50;
$text-sub: #909399;
$border-color: #ebeef5;

.install-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: $bg-color;
  position: relative;
  overflow: hidden;
  
  /* 科技网格背景 */
  .tech-grid-bg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
      linear-gradient(#eef1f6 1px, transparent 1px),
      linear-gradient(90deg, #eef1f6 1px, transparent 1px);
    background-size: 30px 30px;
    z-index: 0;
  }

  /* 装饰光晕 */
  .tech-orb {
    position: absolute;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(43, 90, 251, 0.05) 0%, transparent 70%);
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 0;
    pointer-events: none;
  }

  .install-box {
    width: 480px;
    background: $card-bg;
    border-radius: 16px;
    padding: 40px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.05);
    position: relative;
    z-index: 1;
    border: 1px solid rgba(255,255,255,0.8);
    backdrop-filter: blur(10px);
    
    .install-header {
      text-align: center;
      margin-bottom: 35px;
      
      .logo-area {
        display: flex;
        justify-content: center;
        margin-bottom: 15px;
        
        .logo-icon {
          width: 50px;
          height: 50px;
          background: linear-gradient(135deg, #4a7dff 0%, #2b5afb 100%);
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 24px;
          box-shadow: 0 8px 16px rgba(43, 90, 251, 0.2);
        }
      }
      
      h1 {
        font-size: 20px;
        color: $text-main;
        margin: 0 0 5px 0;
        font-weight: 700;
        letter-spacing: 0.5px;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
      }
      
      .subtitle {
        color: $text-sub;
        font-size: 12px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 0;
      }
    }
    
    .install-form {
      :deep(.el-form-item__label) {
        color: $text-main;
        font-weight: 500;
        font-size: 13px;
        padding-bottom: 4px;
      }

      .tech-input {
        :deep(.el-input__wrapper) {
          background-color: #f8fafc;
          box-shadow: none;
          border: 1px solid #e4e7ed;
          transition: all 0.3s;
          padding: 4px 10px;
          
          &:hover {
            border-color: #c0c4cc;
          }
          
          &.is-focus {
            background-color: #fff;
            border-color: $primary-color;
            box-shadow: 0 0 0 3px rgba(43, 90, 251, 0.1);
          }
        }
        
        :deep(.el-input__inner) {
            font-family: 'Consolas', monospace;
            font-size: 13px;
            color: #333;
        }
      }

      .install-btn {
        width: 100%;
        height: 48px;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 1px;
        background: linear-gradient(90deg, #4a7dff 0%, #2b5afb 100%);
        border: none;
        border-radius: 8px;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(43, 90, 251, 0.25);
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(43, 90, 251, 0.35);
        }
        
        &:active {
          transform: translateY(0);
        }
      }
    }
    
    .install-tips {
      margin-top: 30px;
      background: #f0f2f5;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid #e4e7ed;
      
      .terminal-header {
        background: #e4e7ed;
        padding: 6px 10px;
        display: flex;
        align-items: center;
        gap: 6px;
        
        .dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          &.red { background: #ff5f56; }
          &.yellow { background: #ffbd2e; }
          &.green { background: #27c93f; }
        }
        
        .term-title {
          margin-left: 10px;
          font-size: 11px;
          color: #606266;
          font-family: monospace;
        }
      }
      
      .terminal-body {
        padding: 15px;
        font-family: 'Consolas', monospace;
        font-size: 12px;
        color: #606266;
        line-height: 1.6;
        
        p {
          margin: 0;
        }
        
        .highlight {
          color: $primary-color;
          font-weight: bold;
          background: rgba(43, 90, 251, 0.1);
          padding: 0 4px;
          border-radius: 2px;
        }
      }
    }
  }

  .footer-copyright {
    position: absolute;
    bottom: 20px;
    font-size: 10px;
    color: #c0c4cc;
    letter-spacing: 1px;
  }
}
</style>