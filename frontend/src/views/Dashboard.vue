<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <div class="header-left">
        <div class="logo-area">
          <span class="logo-icon">📊</span>
          <h1>红队资产协作平台</h1>
        </div>
        <span class="divider">/</span>
        <span class="welcome-text">Hi, {{ currentUser.username }}</span>
      </div>
      <div class="header-right">
        <el-button v-if="currentUser.is_super_admin" @click="goToAdmin" type="warning" link icon="Tools">超级管理员</el-button>
        <el-button @click="goToBigScreen" type="primary" link icon="DataAnalysis">数据大屏</el-button>
        <el-button @click="goToCredentials" type="success" link icon="Key">共享凭证</el-button>
        <el-button @click="goToReportTemplates" type="primary" link icon="Document">报告生成(开发中)</el-button>
        <el-button @click="goToSettings" type="info" link icon="Setting">设置</el-button>
        <el-button @click="handleLogout" type="danger" link>退出</el-button>
      </div>
    </div>
    
    <div class="dashboard-content">
      <div class="content-wrapper">
        <div class="action-bar">
          <div class="bar-left">
            <h2>我的项目</h2>
            <span class="project-count" v-if="projects.length">共 {{ projects.length }} 个</span>
          </div>
          <div class="bar-right">
            <el-select
              v-model="timeFilter"
              placeholder="按时间分类"
              style="width: 150px; margin-right: 12px;"
              @change="handleTimeFilterChange"
            >
              <el-option label="全部项目" value="all" />
              <el-option label="今天" value="today" />
              <el-option label="本周" value="week" />
              <el-option label="本月" value="month" />
              <el-option label="三个月内" value="quarter" />
              <el-option label="半年内" value="halfYear" />
              <el-option label="一年内" value="year" />
            </el-select>
            <el-button 
              :icon="Refresh" 
              circle 
              @click="loadProjects" 
              title="刷新列表"
              class="tech-icon-btn"
            />
            <el-button
              v-if="projects.length > 1"
              type="warning"
              @click="showMergeDialog = true"
              class="merge-btn"
            >
              合并项目
            </el-button>
            <el-button
              type="primary"
              :icon="Plus"
              @click="showCreateDialog = true"
              class="create-btn"
            >
              新建项目
            </el-button>
          </div>
        </div>
        
        <div class="projects-grid" v-loading="loading">
          <el-empty v-if="projects.length === 0 && !loading" description="暂无项目，点击新建项目开始" />
          
          <div
            v-for="project in projects"
            :key="project.id"
            class="project-card"
            @click="goToProject(project.id)"
          >
            <div class="card-header">
              <div class="title-group">
                <div class="project-icon">{{ project.name.charAt(0).toUpperCase() }}</div>
                <div class="title-wrapper">
                  <h3>{{ project.name }}</h3>
                  <el-tag v-if="project.is_collaboration_task" type="warning" size="small" effect="plain">
                    协同任务
                  </el-tag>
                </div>
              </div>
              <el-dropdown @command="handleCommand" trigger="click">
                <div class="more-btn" @click.stop>
                  <el-icon><MoreFilled /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      :command="{ action: 'edit', project: project }"
                      icon="Edit"
                    >
                      编辑项目
                    </el-dropdown-item>
                    <el-dropdown-item
                      :command="{ action: 'delete', id: project.id }"
                      icon="Delete"
                      class="danger-item"
                    >
                      删除项目
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            
            <div class="card-body">
              <p class="description">{{ project.description || '暂无描述信息...' }}</p>
              <p v-if="project.is_collaboration_task && project.assigner_name" class="task-info">
                任务下发人: {{ project.assigner_name }}
              </p>
            </div>
            
            <div class="card-footer">
              <div class="tags-group">
                <span class="mini-tag asset-tag">{{ project.asset_count }} 资产</span>
                <span class="mini-tag user-tag">{{ project.creator_name }}</span>
              </div>
              <span class="time">{{ formatTime(project.created_at).split(' ')[0] }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <el-dialog
      v-model="showCreateDialog"
      title="新建项目"
      width="480px"
      class="minimal-dialog"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-position="top"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input
            v-model="createForm.name"
            placeholder="给项目起个名字"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="2"
            placeholder="简单介绍一下这个项目（可选）"
            maxlength="500"
            show-word-limit
            resize="none"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="handleCreate" :loading="createLoading">
            立即创建
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="showEditDialog"
      title="编辑项目"
      width="480px"
      class="minimal-dialog"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="createRules"
        label-position="top"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input
            v-model="editForm.name"
            placeholder="给项目起个名字"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="2"
            placeholder="简单介绍一下这个项目（可选）"
            maxlength="500"
            show-word-limit
            resize="none"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="handleEdit" :loading="editLoading">
            保存修改
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="showMergeDialog"
      title="合并项目"
      width="600px"
      class="minimal-dialog"
    >
      <el-form label-position="top">
        <el-form-item label="选择源项目（将被合并）">
          <el-select
            v-model="mergeForm.source_project_ids"
            multiple
            placeholder="请选择要合并的项目"
            style="width: 100%"
          >
            <el-option
              v-for="project in projects.filter(p => p.id !== mergeForm.target_project_id)"
              :key="project.id"
              :label="`${project.name} (${project.asset_count} 资产)`"
              :value="project.id"
            />
          </el-select>
          <div style="margin-top: 8px; font-size: 12px; color: #909399;">
            已选择 {{ mergeForm.source_project_ids.length }} 个项目
          </div>
        </el-form-item>
        
        <el-form-item label="选择目标项目（合并到）">
          <el-select
            v-model="mergeForm.target_project_id"
            placeholder="请选择目标项目"
            style="width: 100%"
          >
            <el-option
              v-for="project in projects.filter(p => !mergeForm.source_project_ids.includes(p.id))"
              :key="project.id"
              :label="`${project.name} (${project.asset_count} 资产)`"
              :value="project.id"
            />
          </el-select>
          <div style="margin-top: 8px; font-size: 12px; color: #909399;">
            源项目的资产将合并到此项目中
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="mergeForm.delete_source">
            合并后删除源项目
          </el-checkbox>
          <div style="margin-top: 4px; font-size: 12px; color: #f56c6c;">
            ⚠️ 删除后无法恢复，请谨慎操作
          </div>
        </el-form-item>
        
        <el-alert
          title="合并说明"
          type="info"
          :closable="false"
          show-icon
        >
          <ul style="margin: 0; padding-left: 20px; font-size: 12px;">
            <li>相同资产值的资产会自动合并，标签和备注会累加</li>
            <li>所有资产字段（类型、IP、端口、协议等）都会保留</li>
            <li>创建者信息会更新为当前用户</li>
          </ul>
        </el-alert>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showMergeDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="handleMerge" 
            :loading="mergeLoading"
            :disabled="!mergeForm.source_project_ids.length || !mergeForm.target_project_id"
          >
            确认合并
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
// 引入图标，确保渲染
import { MoreFilled, Refresh, Plus } from '@element-plus/icons-vue'
import request from '../utils/request'

export default {
  name: 'Dashboard',
  components: {
    MoreFilled
  },
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const createLoading = ref(false)
    const editLoading = ref(false)
    const showCreateDialog = ref(false)
    const showEditDialog = ref(false)
    const showMergeDialog = ref(false)
    const mergeLoading = ref(false)
    const createFormRef = ref(null)
    const editFormRef = ref(null)
    const projects = ref([])
    const allProjects = ref([])
    const timeFilter = ref('all')
    
    const currentUser = computed(() => {
      const user = localStorage.getItem('user')
      return user ? JSON.parse(user) : {}
    })
    
    const createForm = reactive({
      name: '',
      description: ''
    })
    
    const editForm = reactive({
      id: null,
      name: '',
      description: ''
    })
    
    const mergeForm = reactive({
      source_project_ids: [],
      target_project_id: null,
      delete_source: false
    })
    
    const createRules = {
      name: [
        { required: true, message: '请输入项目名称', trigger: 'blur' },
        { min: 2, max: 100, message: '项目名称长度在2-100个字符之间', trigger: 'blur' }
      ]
    }
    
    const loadProjects = async () => {
      loading.value = true
      try {
        const response = await request.get('/projects')
        allProjects.value = response.projects
        filterProjectsByTime()
      } catch (error) {
        console.error('Load projects error:', error)
      } finally {
        loading.value = false
      }
    }
    
    const filterProjectsByTime = () => {
      if (timeFilter.value === 'all') {
        projects.value = allProjects.value
        return
      }
      
      const now = new Date()
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      
      let startDate
      switch (timeFilter.value) {
        case 'today':
          startDate = today
          break
        case 'week':
          startDate = new Date(today)
          startDate.setDate(today.getDate() - 7)
          break
        case 'month':
          startDate = new Date(today)
          startDate.setMonth(today.getMonth() - 1)
          break
        case 'quarter':
          startDate = new Date(today)
          startDate.setMonth(today.getMonth() - 3)
          break
        case 'halfYear':
          startDate = new Date(today)
          startDate.setMonth(today.getMonth() - 6)
          break
        case 'year':
          startDate = new Date(today)
          startDate.setFullYear(today.getFullYear() - 1)
          break
        default:
          startDate = new Date(0)
      }
      
      projects.value = allProjects.value.filter(project => {
        const projectDate = new Date(project.created_at)
        return projectDate >= startDate
      })
    }
    
    const handleTimeFilterChange = () => {
      filterProjectsByTime()
    }
    
    const handleCreate = async () => {
      try {
        await createFormRef.value.validate()
        createLoading.value = true
        
        const response = await request.post('/projects', {
          ...createForm,
          user_id: currentUser.value.id
        })
        
        ElMessage.success(response.message)
        showCreateDialog.value = false
        createForm.name = ''
        createForm.description = ''
        
        await loadProjects()
      } catch (error) {
        console.error('Create project error:', error)
      } finally {
        createLoading.value = false
      }
    }
    
    const handleCommand = async (command) => {
      if (command.action === 'edit') {
        editForm.id = command.project.id
        editForm.name = command.project.name
        editForm.description = command.project.description || ''
        showEditDialog.value = true
      } else if (command.action === 'delete') {
        try {
          await ElMessageBox.confirm('确定要删除这个项目吗？删除后无法恢复！', '警告', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          })
          
          await request.delete(`/projects/${command.id}`)
          ElMessage.success('项目删除成功')
          await loadProjects()
        } catch (error) {
          if (error !== 'cancel') {
            console.error('Delete project error:', error)
          }
        }
      }
    }
    
    const handleEdit = async () => {
      try {
        await editFormRef.value.validate()
        editLoading.value = true
        
        const response = await request.put(`/projects/${editForm.id}`, {
          name: editForm.name,
          description: editForm.description
        })
        
        ElMessage.success(response.message)
        showEditDialog.value = false
        editForm.id = null
        editForm.name = ''
        editForm.description = ''
        
        await loadProjects()
      } catch (error) {
        console.error('Edit project error:', error)
      } finally {
        editLoading.value = false
      }
    }
    
    const goToProject = (id) => {
      router.push(`/project/${id}`)
    }
    
    const goToSettings = () => {
      router.push('/settings')
    }
    
    const goToAdmin = () => {
      router.push('/admin')
    }
    
    const goToBigScreen = () => {
      router.push('/bigscreen')
    }
    
    const goToCredentials = () => {
      router.push('/credentials')
    }
    
    const goToReportTemplates = () => {
      router.push('/report-templates')
    }
    
    const handleLogout = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      ElMessage.success('已退出登录')
      router.push('/login')
    }
    
    const handleMerge = async () => {
      if (!mergeForm.source_project_ids.length) {
        ElMessage.warning('请选择要合并的源项目')
        return
      }
      
      if (!mergeForm.target_project_id) {
        ElMessage.warning('请选择目标项目')
        return
      }
      
      try {
        const confirmMsg = mergeForm.delete_source 
          ? `确定要合并 ${mergeForm.source_project_ids.length} 个项目并删除源项目吗？此操作不可恢复！`
          : `确定要合并 ${mergeForm.source_project_ids.length} 个项目吗？`
        
        await ElMessageBox.confirm(confirmMsg, '确认合并', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        mergeLoading.value = true
        
        const response = await request.post('/projects/merge', {
          source_project_ids: mergeForm.source_project_ids,
          target_project_id: mergeForm.target_project_id,
          delete_source: mergeForm.delete_source
        })
        
        ElMessage.success(response.message || '项目合并成功')
        showMergeDialog.value = false
        mergeForm.source_project_ids = []
        mergeForm.target_project_id = null
        mergeForm.delete_source = false
        await loadProjects()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Merge projects error:', error)
          ElMessage.error('项目合并失败')
        }
      } finally {
        mergeLoading.value = false
      }
    }
    
    const formatTime = (time) => {
      if (!time) return ''
      const date = new Date(time)
      return date.toLocaleString('zh-CN')
    }
    
    onMounted(() => {
      loadProjects()
    })
    
    return {
      loading,
      createLoading,
      editLoading,
      showCreateDialog,
      showEditDialog,
      showMergeDialog,
      mergeLoading,
      createFormRef,
      editFormRef,
      projects,
      timeFilter,
      currentUser,
      createForm,
      editForm,
      mergeForm,
      createRules,
      loadProjects,
      handleCreate,
      handleEdit,
      handleMerge,
      handleTimeFilterChange,
      handleCommand,
      goToProject,
      goToSettings,
      goToAdmin,
      goToBigScreen,
      goToCredentials,
      goToReportTemplates,
      handleLogout,
      formatTime,
      // 导出图标供 template 使用
      Refresh,
      Plus
    }
  }
}
</script>

<style lang="scss" scoped>
// 变量定义
$primary-color: #2b5afb; // 统一使用你的科技蓝
$bg-color: #f5f7fa;
$text-primary: #1f2d3d;
$text-regular: #5e6d82;
$text-secondary: #909399;
$border-color: #e4e7ed;

.dashboard-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: $bg-color;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;

  .dashboard-header {
    height: 64px;
    background: white;
    border-bottom: 1px solid darken($bg-color, 5%); 
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    z-index: 10;

    .header-left {
      display: flex;
      align-items: center;
      
      .logo-area {
        display: flex;
        align-items: center;
        gap: 8px;
        .logo-icon { font-size: 20px; }
        h1 {
          font-size: 18px;
          color: $text-primary;
          margin: 0;
          font-weight: 600;
          letter-spacing: -0.5px;
        }
      }

      .divider {
        margin: 0 16px;
        color: $border-color;
        font-size: 16px;
      }

      .welcome-text {
        color: $text-regular;
        font-size: 14px;
      }
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .dashboard-content {
    flex: 1;
    overflow-y: auto;
    padding: 40px;
    
    .content-wrapper {
      max-width: 1400px;
      margin: 0 auto;
    }

    .action-bar {
      margin-bottom: 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;

      .bar-left {
        display: flex;
        align-items: baseline;
        gap: 12px;
        h2 {
          font-size: 24px;
          color: $text-primary;
          margin: 0;
          font-weight: 600;
        }
        .project-count {
          font-size: 13px;
          color: $text-secondary;
        }
      }
      
      .bar-right {
        display: flex;
        gap: 12px;
        
        /* * 修改样式 1：刷新按钮的科技风样式
         * 纯白背景 + 边框 + 阴影 = 清晰可见
         */
        .tech-icon-btn {
          background: #ffffff;
          border: 1px solid #dcdfe6;
          color: #606266;
          width: 36px;
          height: 36px;
          font-size: 16px;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08); // 关键：加上阴影让它浮起来
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          
          &:hover {
            color: $primary-color;
            border-color: $primary-color;
            background: #ecf5ff;
            transform: translateY(-1px); // 悬浮上浮
            box-shadow: 0 4px 12px rgba(43, 90, 251, 0.15);
          }
          
          &:active {
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(43, 90, 251, 0.1);
          }
        }

        /* * 修改样式 2：新建按钮增强
         * 增加阴影和动效，与刷新按钮风格统一
         */
        .create-btn {
          padding-left: 24px;
          padding-right: 24px;
          border-radius: 6px;
          font-weight: 500;
          background: $primary-color;
          border-color: $primary-color;
          box-shadow: 0 4px 12px rgba(43, 90, 251, 0.25); // 蓝色投影
          transition: all 0.3s;
          
          &:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(43, 90, 251, 0.35);
            background: lighten($primary-color, 5%);
          }
        }
      }
    }

    .projects-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 24px;
      min-height: 400px;
      align-content: flex-start;
      
      :deep(.el-empty) {
        grid-column: 1 / -1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100%;
      }

      .project-card {
        background: white;
        border-radius: 12px;
        border: 1px solid transparent;
        background-clip: padding-box;
        position: relative;
        cursor: pointer;
        transition: all 0.25s ease;
        display: flex;
        flex-direction: column;
        padding: 16px;
        height: auto;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.04), 0 2px 4px rgba(0,0,0,0.02);

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 0 0 1px rgba($primary-color, 0.1), 0 12px 32px rgba(0, 0, 0, 0.08);
          
          .card-header .more-btn {
            opacity: 1;
          }
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 12px;

          .title-group {
            display: flex;
            align-items: center;
            gap: 10px;
            
            .project-icon {
              width: 32px;
              height: 32px;
              background: lighten($primary-color, 35%);
              color: $primary-color;
              border-radius: 6px;
              display: flex;
              align-items: center;
              justify-content: center;
              font-weight: 600;
              font-size: 14px;
            }
            
            .title-wrapper {
              display: flex;
              align-items: center;
              gap: 8px;
              
              h3 {
                font-size: 16px;
                color: $text-primary;
                margin: 0;
                font-weight: 600;
                line-height: 1.4;
              }
            }
          }

          .more-btn {
            color: $text-secondary;
            padding: 4px;
            border-radius: 4px;
            opacity: 1;
            transition: all 0.2s;
            
            &:hover {
              background: #f0f2f5;
              color: $text-primary;
            }
          }
        }

        .card-body {
          margin-bottom: 24px;
          
          .description {
            color: $text-regular;
            font-size: 14px;
            line-height: 1.5;
            margin: 0;
            display: -webkit-box;
            -webkit-line-clamp: 1;
            line-clamp: 1;
            -webkit-box-orient: vertical;
            overflow: hidden;
            height: 21px;
          }
          
          .task-info {
            color: #909399;
            font-size: 12px;
            margin: 8px 0 0 0;
          }
        }

        .card-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-top: auto;
          
          .tags-group {
            display: flex;
            gap: 8px;
            
            .mini-tag {
              font-size: 12px;
              padding: 2px 8px;
              border-radius: 4px;
              background: #f5f7fa;
              color: $text-regular;
              
              &.asset-tag {
                color: $primary-color;
                background: lighten($primary-color, 38%);
              }
            }
          }

          .time {
            font-size: 12px;
            color: #c0c4cc;
          }
        }
      }
    }
  }
}

:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
  
  .el-dialog__header {
    padding: 24px 24px 0;
    margin-bottom: 20px;
    .el-dialog__title {
      font-weight: 600;
    }
  }
  
  .el-dialog__body {
    padding: 0 24px;
  }
  
  .el-dialog__footer {
    padding: 24px;
    background: #fcfcfc;
  }
}

.danger-item {
  color: #f56c6c;
}
</style>