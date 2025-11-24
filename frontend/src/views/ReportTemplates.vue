<template>
  <div class="report-templates-container">
    <div class="header">
      <h2>报告模板管理</h2>
      <el-button type="primary" @click="showUploadDialog">
        <el-icon><Upload /></el-icon> 上传模板
      </el-button>
    </div>

    <div class="content">
      <el-table :data="templates" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="模板名称" width="200" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="file_name" label="文件名" width="200" />
        <el-table-column label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="占位符" width="150">
          <template #default="{ row }">
            <el-tag v-if="row.placeholders" size="small">
              {{ JSON.parse(row.placeholders).length }} 个
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="createReport(row)">
              创建报告
            </el-button>
            <el-button size="small" type="primary" @click="downloadTemplate(row)">
              下载
            </el-button>
            <el-button size="small" type="danger" @click="deleteTemplate(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 创建报告对话框 -->
    <el-dialog v-model="createReportDialogVisible" title="创建报告" width="500px">
      <el-form :model="reportForm" label-width="100px">
        <el-form-item label="报告名称" required>
          <el-input v-model="reportForm.name" placeholder="请输入报告名称" />
        </el-form-item>
        <el-form-item label="关联项目">
          <el-select v-model="reportForm.project_id" placeholder="请选择项目（可选）" clearable style="width: 100%">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createReportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCreateReport" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 上传模板对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传报告模板" width="500px">
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="模板名称" required>
          <el-input v-model="uploadForm.name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="模板描述">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模板描述（可选）"
          />
        </el-form-item>
        <el-form-item label="选择文件" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            accept=".docx"
          >
            <el-button type="primary">选择 .docx 文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                只支持 .docx 格式的 Word 文档
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="uploadTemplate" :loading="uploading">
          上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'

export default {
  name: 'ReportTemplates',
  components: {
    Upload
  },
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const templates = ref([])
    const projects = ref([])
    const uploadDialogVisible = ref(false)
    const uploading = ref(false)
    const uploadRef = ref(null)
    const selectedFile = ref(null)
    const createReportDialogVisible = ref(false)
    const creating = ref(false)
    const selectedTemplate = ref(null)
    
    const uploadForm = ref({
      name: '',
      description: ''
    })
    
    const reportForm = ref({
      name: '',
      project_id: null
    })

    // 加载模板列表
    const loadTemplates = async () => {
      loading.value = true
      try {
        const response = await request.get('/report-templates')
        templates.value = response.templates
      } catch (error) {
        console.error('Load templates error:', error)
        ElMessage.error('加载模板列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 加载项目列表
    const loadProjects = async () => {
      try {
        const response = await request.get('/projects')
        projects.value = response.projects
      } catch (error) {
        console.error('Load projects error:', error)
      }
    }
    
    // 创建报告
    const createReport = (template) => {
      selectedTemplate.value = template
      reportForm.value.name = `${template.name} - ${new Date().toLocaleDateString()}`
      reportForm.value.project_id = null
      createReportDialogVisible.value = true
    }
    
    // 确认创建报告
    const confirmCreateReport = async () => {
      if (!reportForm.value.name) {
        ElMessage.warning('请输入报告名称')
        return
      }
      
      creating.value = true
      try {
        const response = await request.post('/reports', {
          template_id: selectedTemplate.value.id,
          name: reportForm.value.name,
          project_id: reportForm.value.project_id
        })
        
        if (response.success) {
          ElMessage.success(response.message)
          createReportDialogVisible.value = false
          // 跳转到报告编辑页面
          router.push(`/reports/${response.report_id}/edit`)
        }
      } catch (error) {
        console.error('Create report error:', error)
        ElMessage.error('创建报告失败')
      } finally {
        creating.value = false
      }
    }

    // 显示上传对话框
    const showUploadDialog = () => {
      uploadForm.value.name = ''
      uploadForm.value.description = ''
      selectedFile.value = null
      uploadDialogVisible.value = true
    }

    // 文件选择变化
    const handleFileChange = (file) => {
      selectedFile.value = file.raw
    }

    // 文件超出限制
    const handleExceed = () => {
      ElMessage.warning('只能上传一个文件')
    }

    // 上传模板
    const uploadTemplate = async () => {
      if (!uploadForm.value.name) {
        ElMessage.warning('请输入模板名称')
        return
      }

      if (!selectedFile.value) {
        ElMessage.warning('请选择要上传的文件')
        return
      }

      uploading.value = true
      try {
        const formData = new FormData()
        formData.append('file', selectedFile.value)
        formData.append('name', uploadForm.value.name)
        formData.append('description', uploadForm.value.description)

        const response = await request.post('/report-templates', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        if (response.success) {
          ElMessage.success(response.message)
          uploadDialogVisible.value = false
          loadTemplates()
        }
      } catch (error) {
        console.error('Upload error:', error)
        ElMessage.error('上传失败')
      } finally {
        uploading.value = false
      }
    }

    // 下载模板
    const downloadTemplate = async (template) => {
      try {
        const response = await request.get(`/report-templates/${template.id}/download`, {
          responseType: 'blob'
        })

        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', template.file_name)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        ElMessage.success('下载成功')
      } catch (error) {
        console.error('Download error:', error)
        ElMessage.error('下载失败')
      }
    }

    // 删除模板
    const deleteTemplate = async (template) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除模板"${template.name}"吗？`,
          '提示',
          {
            type: 'warning'
          }
        )

        const response = await request.delete(`/report-templates/${template.id}`)
        if (response.success) {
          ElMessage.success(response.message)
          loadTemplates()
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Delete error:', error)
          ElMessage.error('删除失败')
        }
      }
    }

    // 格式化文件大小
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }

    // 格式化时间
    const formatTime = (time) => {
      if (!time) return ''
      const date = new Date(time)
      return date.toLocaleString('zh-CN')
    }

    onMounted(() => {
      loadTemplates()
      loadProjects()
    })

    return {
      loading,
      templates,
      projects,
      uploadDialogVisible,
      uploading,
      uploadRef,
      uploadForm,
      createReportDialogVisible,
      creating,
      reportForm,
      showUploadDialog,
      handleFileChange,
      handleExceed,
      uploadTemplate,
      createReport,
      confirmCreateReport,
      downloadTemplate,
      deleteTemplate,
      formatFileSize,
      formatTime
    }
  }
}
</script>

<style lang="scss" scoped>
.report-templates-container {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

    h2 {
      margin: 0;
      font-size: 24px;
      color: #303133;
    }
  }

  .content {
    flex: 1;
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    overflow: auto;
  }
}
</style>
