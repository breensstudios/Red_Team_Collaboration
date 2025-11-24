<template>
  <div class="credentials-container">
    <div class="light-bg-grid"></div>

    <div class="detail-header">
      <div class="header-left">
        <el-button 
          class="light-btn-back" 
          :icon="ArrowLeft" 
          @click="goBack" 
          circle 
          title="返回上一页"
        />
        <div class="title-area">
          <h1>共享凭证管理</h1>
          <span class="subtitle">SHARED CREDENTIALS MANAGEMENT</span>
        </div>
      </div>
      <div class="header-right">
        <div class="user-badge">
          <el-avatar :size="28" icon="UserFilled" class="user-avatar" />
          <span class="user-info">{{ currentUser.username }}</span>
        </div>
      </div>
    </div>
    
    <div class="detail-content">
      <div class="content-wrapper">
        <div class="action-bar">
          <div class="left-actions">
            <el-button type="primary" icon="Plus" @click="showCreateDialog = true" class="tech-btn-primary">
              添加凭证
            </el-button>
            
            <el-button-group class="tech-btn-group">
              <el-button plain icon="Filter" @click="showFilterPanel = !showFilterPanel">
                {{ showFilterPanel ? '隐藏筛选' : '显示筛选' }}
              </el-button>
              <el-button plain icon="Refresh" @click="loadCredentials" />
            </el-button-group>
            
            <el-button
              v-if="hasActiveFilters"
              icon="Close"
              text
              @click="clearFilters"
            >
              清除筛选
            </el-button>
          </div>

          <div class="stats">
            <div class="stat-pill">
              <span class="label">Total</span>
              <span class="value">{{ credentials.length }}</span>
            </div>
          </div>
        </div>
        
        <el-collapse-transition>
          <div v-show="showFilterPanel" class="filter-panel">
            <el-form :model="filters" label-width="80px" size="small" class="filter-form">
              <el-row :gutter="24">
                <el-col :span="6">
                  <el-form-item label="分类">
                    <el-select v-model="filters.category" placeholder="全部" clearable class="tech-select">
                      <el-option label="全部" value="" />
                      <el-option label="VPN" value="VPN" />
                      <el-option label="云服务" value="云服务" />
                      <el-option label="开发工具" value="开发工具" />
                      <el-option label="测试平台" value="测试平台" />
                      <el-option label="办公软件" value="办公软件" />
                      <el-option label="其他" value="其他" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="平台">
                    <el-input v-model="filters.platform" placeholder="支持模糊搜索" clearable class="tech-input" />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="状态">
                    <el-select v-model="filters.is_active" placeholder="全部" clearable class="tech-select">
                      <el-option label="全部" value="" />
                      <el-option label="有效" value="true" />
                      <el-option label="无效" value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </el-collapse-transition>
        
        <div class="table-container tech-card">
          <el-table
            :data="filteredCredentials"
            v-loading="loading"
            stripe
            style="width: 100%"
            :height="tableHeight"
            class="tech-table"
            header-cell-class-name="tech-table-header"
          >
            <el-table-column type="index" label="#" width="55" align="center" class-name="index-col" />
            
            <el-table-column prop="category" label="分类" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getCategoryColor(row.category)" size="small" effect="light">
                  {{ row.category }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="platform" label="平台名称" width="150">
              <template #default="{ row }">
                <span class="platform-name">{{ row.platform }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="url" label="URL" min-width="200">
              <template #default="{ row }">
                <div v-if="row.url" class="url-cell">
                  <el-link :href="row.url" target="_blank" type="primary" :underline="false" class="url-link">
                    {{ row.url }}
                    <el-icon><Link /></el-icon>
                  </el-link>
                </div>
                <span v-else class="no-url">-</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="username" label="用户名" width="180">
              <template #default="{ row }">
                <el-text class="username-text" copyable>{{ row.username }}</el-text>
              </template>
            </el-table-column>
            
            <el-table-column prop="password" label="密码" width="150" align="center">
              <template #default="{ row }">
                <el-button
                  size="small"
                  icon="View"
                  @click="viewPassword(row)"
                  link
                >
                  查看密码
                </el-button>
              </template>
            </el-table-column>
            
            <el-table-column prop="description" label="备注" min-width="200">
              <template #default="{ row }">
                <span class="description-text">{{ row.description || '-' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="is_active" label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '有效' : '无效' }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="creator_name" label="创建者" width="100" align="center" />
            
            <el-table-column prop="created_at" label="创建时间" width="160" align="center">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="150" align="center" fixed="right">
              <template #default="{ row }">
                <div class="row-actions">
                  <el-button
                    type="primary"
                    size="small"
                    icon="Edit"
                    @click="editCredential(row)"
                    text
                  >
                    编辑
                  </el-button>
                  <el-button
                    type="danger"
                    size="small"
                    icon="Delete"
                    @click="deleteCredential(row.id)"
                    text
                  >
                    删除
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
    
    <el-dialog
      v-model="showCreateDialog"
      :title="editingCredential ? '编辑凭证' : '添加凭证'"
      width="600px"
      class="tech-dialog"
    >
      <el-form :model="credentialForm" label-width="100px" class="tech-form">
        <el-form-item label="平台名称" required>
          <el-input v-model="credentialForm.platform" placeholder="例如：GitHub" />
        </el-form-item>
        
        <el-form-item label="平台URL">
          <el-input v-model="credentialForm.url" placeholder="例如：https://github.com" />
        </el-form-item>
        
        <el-form-item label="分类" required>
          <el-select v-model="credentialForm.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="VPN" value="VPN" />
            <el-option label="云服务" value="云服务" />
            <el-option label="开发工具" value="开发工具" />
            <el-option label="测试平台" value="测试平台" />
            <el-option label="办公软件" value="办公软件" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="用户名" required>
          <el-input v-model="credentialForm.username" placeholder="登录用户名或邮箱" />
        </el-form-item>
        
        <el-form-item label="密码" required>
          <el-input
            v-model="credentialForm.password"
            type="password"
            placeholder="登录密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="备注说明">
          <el-input
            v-model="credentialForm.description"
            type="textarea"
            :rows="3"
            placeholder="可以添加一些说明信息"
          />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch v-model="credentialForm.is_active" active-text="有效" inactive-text="无效" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCredential" :loading="saving">
          {{ editingCredential ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="showPasswordDialog"
      title="查看密码"
      width="400px"
      class="tech-dialog"
    >
      <div class="password-view">
        <el-input
          v-model="currentPassword"
          type="text"
          readonly
          class="password-input"
        >
          <template #append>
            <el-button icon="CopyDocument" @click="copyPassword" />
          </template>
        </el-input>
      </div>
      
      <template #footer>
        <el-button @click="showPasswordDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
// 显式引入 ArrowLeft 图标
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '../utils/request'

export default {
  name: 'SharedCredentials',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const saving = ref(false)
    const showCreateDialog = ref(false)
    const showPasswordDialog = ref(false)
    const showFilterPanel = ref(false)
    const credentials = ref([])
    const editingCredential = ref(null)
    const currentPassword = ref('')
    const tableHeight = ref(window.innerHeight - 350)
    
    const credentialForm = reactive({
      platform: '',
      url: '',
      username: '',
      password: '',
      category: '其他',
      description: '',
      is_active: true
    })
    
    const filters = reactive({
      category: '',
      platform: '',
      is_active: ''
    })
    
    const currentUser = computed(() => {
      const user = localStorage.getItem('user')
      return user ? JSON.parse(user) : {}
    })
    
    const hasActiveFilters = computed(() => {
      return filters.category !== '' ||
             filters.platform !== '' ||
             filters.is_active !== ''
    })
    
    const filteredCredentials = computed(() => {
      let result = credentials.value
      
      if (filters.category) {
        result = result.filter(c => c.category === filters.category)
      }
      
      if (filters.platform) {
        const searchPlatform = filters.platform.toLowerCase()
        result = result.filter(c => 
          c.platform && c.platform.toLowerCase().includes(searchPlatform)
        )
      }
      
      if (filters.is_active) {
        const isActive = filters.is_active === 'true'
        result = result.filter(c => c.is_active === isActive)
      }
      
      return result
    })
    
    const clearFilters = () => {
      filters.category = ''
      filters.platform = ''
      filters.is_active = ''
    }
    
    const loadCredentials = async () => {
      loading.value = true
      try {
        const response = await request.get('/credentials')
        credentials.value = response.credentials
      } catch (error) {
        console.error('Load credentials error:', error)
        ElMessage.error('加载凭证列表失败')
      } finally {
        loading.value = false
      }
    }
    
    const saveCredential = async () => {
      if (!credentialForm.platform || !credentialForm.username || !credentialForm.password) {
        ElMessage.warning('请填写必填项')
        return
      }
      
      saving.value = true
      try {
        if (editingCredential.value) {
          await request.put(`/credentials/${editingCredential.value.id}`, credentialForm)
          ElMessage.success('凭证更新成功')
        } else {
          await request.post('/credentials', credentialForm)
          ElMessage.success('凭证创建成功')
        }
        
        showCreateDialog.value = false
        await loadCredentials()
      } catch (error) {
        console.error('Save credential error:', error)
        ElMessage.error('保存凭证失败')
      } finally {
        saving.value = false
      }
    }
    
    const editCredential = (credential) => {
      editingCredential.value = credential
      credentialForm.platform = credential.platform
      credentialForm.url = credential.url || ''
      credentialForm.username = credential.username
      credentialForm.password = ''  // 不显示原密码
      credentialForm.category = credential.category
      credentialForm.description = credential.description || ''
      credentialForm.is_active = credential.is_active
      showCreateDialog.value = true
    }
    
    const deleteCredential = async (id) => {
      try {
        await ElMessageBox.confirm(
          '确定要删除这个凭证吗？',
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await request.delete(`/credentials/${id}`)
        ElMessage.success('凭证删除成功')
        await loadCredentials()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Delete credential error:', error)
          ElMessage.error('删除凭证失败')
        }
      }
    }
    
    const viewPassword = async (credential) => {
      try {
        const response = await request.get(`/credentials/${credential.id}/password`)
        currentPassword.value = response.password
        showPasswordDialog.value = true
      } catch (error) {
        console.error('Get password error:', error)
        ElMessage.error('获取密码失败')
      }
    }
    
    const copyPassword = () => {
      navigator.clipboard.writeText(currentPassword.value)
      ElMessage.success('密码已复制到剪贴板')
    }
    
    const getCategoryColor = (category) => {
      const colors = {
        'VPN': 'success',
        '云服务': 'primary',
        '开发工具': 'warning',
        '测试平台': 'danger',
        '办公软件': 'info',
        '其他': ''
      }
      return colors[category] || ''
    }
    
    const formatTime = (time) => {
      if (!time) return '-'
      return time.replace('T', ' ').substring(0, 19)
    }
    
    const goBack = () => {
      router.back()
    }
    
    onMounted(() => {
      loadCredentials()
      
      window.addEventListener('resize', () => {
        tableHeight.value = window.innerHeight - 350
      })
    })
    
    return {
      loading,
      saving,
      showCreateDialog,
      showPasswordDialog,
      showFilterPanel,
      credentials,
      filteredCredentials,
      credentialForm,
      filters,
      editingCredential,
      currentPassword,
      currentUser,
      tableHeight,
      hasActiveFilters,
      clearFilters,
      loadCredentials,
      saveCredential,
      editCredential,
      deleteCredential,
      viewPassword,
      copyPassword,
      getCategoryColor,
      formatTime,
      goBack,
      // 导出图标
      ArrowLeft
    }
  }
}
</script>

<style lang="scss" scoped>
/* 样式部分 */
$primary-color: #2b5afb;
$text-main: #1d2129;
$text-sub: #4e5969;
$border-color: #e5e6eb;
$card-bg: #ffffff;
$shadow-soft: 0 2px 12px rgba(0, 0, 0, 0.04);

.credentials-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  position: relative;
  overflow: hidden;
}

.light-bg-grid {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(43, 90, 251, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(43, 90, 251, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
  z-index: 0;
}

.detail-header {
  position: relative;
  z-index: 1;
  padding: 24px 32px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid $border-color;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
    
    /* * 修改重点：返回按钮的科技风样式
     * 增加边框、阴影和悬浮动效
     */
    .light-btn-back {
      background: #ffffff;
      border: 1px solid #dcdfe6;
      color: #303133;
      width: 36px;
      height: 36px;
      font-size: 16px;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      
      &:hover {
        border-color: $primary-color;
        color: $primary-color;
        background: #ecf5ff;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(43, 90, 251, 0.15);
      }
      
      &:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(43, 90, 251, 0.1);
      }
    }
    
    .title-area {
      h1 {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
        color: $text-main;
        letter-spacing: -0.5px;
      }
      
      .subtitle {
        font-size: 12px;
        color: $text-sub;
        font-weight: 500;
        letter-spacing: 1px;
      }
    }
  }
  
  .header-right {
    .user-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      background: #f7f8fa;
      border-radius: 20px;
      border: 1px solid $border-color;
      
      .user-info {
        font-size: 14px;
        color: $text-main;
        font-weight: 500;
      }
    }
  }
}

.detail-content {
  position: relative;
  z-index: 1;
  padding: 24px 32px;
  
  .content-wrapper {
    max-width: 1600px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    
    .action-bar {
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      
      .left-actions {
        display: flex;
        gap: 10px;
        align-items: center;
        flex-wrap: wrap;
        
        .tech-btn-group {
          .el-button {
            border-radius: 0;
            border-color: #dcdfe6;
            &:first-child { border-top-left-radius: 4px; border-bottom-left-radius: 4px; }
            &:last-child { border-top-right-radius: 4px; border-bottom-right-radius: 4px; }
            &:hover, &:focus {
              color: $primary-color;
              border-color: lighten($primary-color, 20%);
              background-color: lighten($primary-color, 45%);
              z-index: 1;
            }
          }
        }
        
        .tech-btn-primary {
          background: $primary-color;
          border-color: $primary-color;
          box-shadow: 0 4px 10px rgba(43, 90, 251, 0.2);
          transition: all 0.2s;
          &:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 15px rgba(43, 90, 251, 0.3);
          }
        }
      }
      
      .stats {
        display: flex;
        gap: 12px;
        
        .stat-pill {
          padding: 8px 16px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 20px;
          display: flex;
          align-items: center;
          gap: 8px;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
          
          .label {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.9);
            font-weight: 500;
          }
          
          .value {
            font-size: 16px;
            color: #ffffff;
            font-weight: 700;
          }
        }
      }
    }
    
    .filter-panel {
      margin-bottom: 16px;
      padding: 20px;
      background: $card-bg;
      border-radius: 8px;
      border: 1px solid $border-color;
      box-shadow: $shadow-soft;
    }
    
    .table-container {
      flex: 1;
      background: $card-bg;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid $border-color;
      box-shadow: $shadow-soft;
      
      .platform-name {
        font-weight: 500;
        color: $text-main;
      }
      
      .url-cell {
        .url-link {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 13px;
          max-width: 100%;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          
          .el-icon {
            flex-shrink: 0;
          }
        }
      }
      
      .no-url {
        color: $text-sub;
      }
      
      .username-text {
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
        color: #303133;
        background: #f4f4f5;
        padding: 2px 6px;
        border-radius: 4px;
      }
      
      .description-text {
        color: $text-sub;
        font-size: 13px;
      }
      
      .row-actions {
        display: flex;
        gap: 4px;
        justify-content: center;
        flex-wrap: wrap;
      }
    }
  }
}

.password-view {
  padding: 20px 0;
  
  .password-input {
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 16px;
  }
}
</style>