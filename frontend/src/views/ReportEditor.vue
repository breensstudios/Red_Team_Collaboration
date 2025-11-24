<template>
  <div class="report-editor-container">
    <div class="editor-header">
      <div class="header-left">
        <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
        <h2>{{ report.name }}</h2>
        <el-tag v-if="report.status === 'draft'" type="warning">草稿</el-tag>
        <el-tag v-else type="success">已完成</el-tag>
      </div>
      <div class="header-right">
        <el-button @click="saveReport" type="primary" :loading="saving">
          <el-icon><DocumentCopy /></el-icon> 保存
        </el-button>
        <el-button @click="exportReport" type="success">
          <el-icon><Download /></el-icon> 导出Word
        </el-button>
      </div>
    </div>

    <div class="editor-content" v-loading="loading">
      <el-tabs v-model="activeTab" class="editor-tabs">
        <!-- 基本信息标签页 -->
        <el-tab-pane label="基本信息" name="basic">
          <div class="form-section">
            <h3>占位符填充</h3>
            <el-form label-width="120px">
              <el-form-item
                v-for="placeholder in placeholders"
                :key="placeholder"
                :label="placeholder"
              >
                <el-input
                  v-model="content.placeholders[placeholder]"
                  type="textarea"
                  :rows="2"
                  :placeholder="`请输入${placeholder}`"
                  @change="autoSave"
                />
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 漏洞列表标签页 -->
        <el-tab-pane label="漏洞列表" name="vulnerabilities">
          <div class="vuln-section">
            <div class="vuln-header">
              <h3>漏洞列表</h3>
              <el-button type="primary" @click="addVulnerability">
                <el-icon><Plus /></el-icon> 添加漏洞
              </el-button>
            </div>

            <div class="vuln-list">
              <el-card
                v-for="(vuln, index) in content.vulnerabilities"
                :key="index"
                class="vuln-card"
                shadow="hover"
              >
                <template #header>
                  <div class="vuln-card-header">
                    <span>漏洞 #{{ index + 1 }}</span>
                    <div class="vuln-actions">
                      <el-button
                        v-if="index > 0"
                        size="small"
                        @click="moveVulnerability(index, 'up')"
                        icon="Top"
                      />
                      <el-button
                        v-if="index < content.vulnerabilities.length - 1"
                        size="small"
                        @click="moveVulnerability(index, 'down')"
                        icon="Bottom"
                      />
                      <el-button
                        size="small"
                        type="primary"
                        @click="copyVulnerability(index)"
                        icon="DocumentCopy"
                      >
                        复制
                      </el-button>
                      <el-button
                        size="small"
                        type="danger"
                        @click="deleteVulnerability(index)"
                        icon="Delete"
                      />
                    </div>
                  </div>
                </template>

                <el-form label-width="100px">
                  <el-form-item label="漏洞名称">
                    <el-input v-model="vuln.name" placeholder="请输入漏洞名称" @change="autoSave" />
                  </el-form-item>
                  
                  <el-form-item label="危害等级">
                    <el-select v-model="vuln.severity" placeholder="请选择危害等级" @change="autoSave">
                      <el-option label="严重" value="critical" />
                      <el-option label="高危" value="high" />
                      <el-option label="中危" value="medium" />
                      <el-option label="低危" value="low" />
                      <el-option label="信息" value="info" />
                    </el-select>
                  </el-form-item>

                  <el-form-item label="漏洞描述">
                    <el-input
                      v-model="vuln.description"
                      type="textarea"
                      :rows="4"
                      placeholder="请输入漏洞描述"
                      @change="autoSave"
                    />
                  </el-form-item>

                  <el-form-item label="复现步骤">
                    <el-input
                      v-model="vuln.reproduction"
                      type="textarea"
                      :rows="6"
                      placeholder="请输入复现步骤"
                      @change="autoSave"
                    />
                  </el-form-item>

                  <el-form-item label="修复建议">
                    <el-input
                      v-model="vuln.solution"
                      type="textarea"
                      :rows="4"
                      placeholder="请输入修复建议"
                      @change="autoSave"
                    />
                  </el-form-item>

                  <el-form-item label="截图">
                    <div class="image-upload-area">
                      <el-upload
                        :action="`/api/reports/${reportId}/upload-image`"
                        :headers="uploadHeaders"
                        :on-success="(response) => handleImageSuccess(response, index)"
                        :before-upload="beforeImageUpload"
                        list-type="picture-card"
                        :file-list="vuln.images || []"
                      >
                        <el-icon><Plus /></el-icon>
                      </el-upload>
                      <div class="paste-tip">
                        提示：可以直接 Ctrl+V 粘贴图片
                      </div>
                    </div>
                  </el-form-item>
                </el-form>
              </el-card>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, DocumentCopy, Download, Plus, Top, Bottom, Delete } from '@element-plus/icons-vue'
import request from '../utils/request'

export default {
  name: 'ReportEditor',
  components: {
    ArrowLeft,
    DocumentCopy,
    Download,
    Plus,
    Top,
    Bottom,
    Delete
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const loading = ref(false)
    const saving = ref(false)
    const activeTab = ref('basic')
    const reportId = computed(() => route.params.id)
    
    const report = ref({
      name: '',
      status: 'draft'
    })
    
    const content = ref({
      placeholders: {},
      vulnerabilities: []
    })
    
    const placeholders = ref([])
    
    // 上传请求头
    const uploadHeaders = computed(() => {
      const user = localStorage.getItem('user')
      return {
        'user': user || ''
      }
    })

    // 加载报告
    const loadReport = async () => {
      loading.value = true
      try {
        const response = await request.get(`/reports/${reportId.value}`)
        report.value = response.report
        
        // 解析内容
        if (response.report.content) {
          content.value = JSON.parse(response.report.content)
        }
        
        // 解析占位符
        if (response.report.placeholders) {
          placeholders.value = JSON.parse(response.report.placeholders)
        }
      } catch (error) {
        console.error('Load report error:', error)
        ElMessage.error('加载报告失败')
      } finally {
        loading.value = false
      }
    }

    // 自动保存
    let autoSaveTimer = null
    const autoSave = () => {
      if (autoSaveTimer) {
        clearTimeout(autoSaveTimer)
      }
      autoSaveTimer = setTimeout(() => {
        saveReport(true)
      }, 2000)
    }

    // 保存报告
    const saveReport = async (silent = false) => {
      if (!silent) {
        saving.value = true
      }
      
      try {
        const response = await request.put(`/reports/${reportId.value}`, {
          content: content.value
        })
        
        if (response.success && !silent) {
          ElMessage.success('保存成功')
        }
      } catch (error) {
        console.error('Save report error:', error)
        if (!silent) {
          ElMessage.error('保存失败')
        }
      } finally {
        if (!silent) {
          saving.value = false
        }
      }
    }

    // 添加漏洞
    const addVulnerability = () => {
      content.value.vulnerabilities.push({
        name: '',
        severity: 'medium',
        description: '',
        reproduction: '',
        solution: '',
        images: []
      })
      autoSave()
    }

    // 复制漏洞
    const copyVulnerability = (index) => {
      const vuln = JSON.parse(JSON.stringify(content.value.vulnerabilities[index]))
      content.value.vulnerabilities.splice(index + 1, 0, vuln)
      ElMessage.success('漏洞已复制')
      autoSave()
    }

    // 删除漏洞
    const deleteVulnerability = async (index) => {
      try {
        await ElMessageBox.confirm('确定要删除这个漏洞吗？', '提示', {
          type: 'warning'
        })
        content.value.vulnerabilities.splice(index, 1)
        ElMessage.success('漏洞已删除')
        autoSave()
      } catch (error) {
        // 用户取消
      }
    }

    // 移动漏洞
    const moveVulnerability = (index, direction) => {
      const newIndex = direction === 'up' ? index - 1 : index + 1
      const temp = content.value.vulnerabilities[index]
      content.value.vulnerabilities[index] = content.value.vulnerabilities[newIndex]
      content.value.vulnerabilities[newIndex] = temp
      autoSave()
    }

    // 图片上传成功
    const handleImageSuccess = (response, vulnIndex) => {
      if (response.success) {
        if (!content.value.vulnerabilities[vulnIndex].images) {
          content.value.vulnerabilities[vulnIndex].images = []
        }
        content.value.vulnerabilities[vulnIndex].images.push({
          name: response.attachment_id,
          url: response.url
        })
        ElMessage.success('图片上传成功')
        autoSave()
      }
    }

    // 图片上传前检查
    const beforeImageUpload = (file) => {
      const isImage = file.type.startsWith('image/')
      const isLt5M = file.size / 1024 / 1024 < 5

      if (!isImage) {
        ElMessage.error('只能上传图片文件!')
        return false
      }
      if (!isLt5M) {
        ElMessage.error('图片大小不能超过 5MB!')
        return false
      }
      return true
    }

    // 导出报告
    const exportReport = async () => {
      try {
        ElMessage.info('正在生成报告，请稍候...')
        
        // 先保存当前内容
        await saveReport(true)
        
        // 调用导出接口
        const response = await request.get(`/reports/${reportId.value}/export`, {
          responseType: 'blob'
        })
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${report.value.name}.docx`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('报告导出成功')
      } catch (error) {
        console.error('Export report error:', error)
        ElMessage.error('导出失败，请稍后重试')
      }
    }

    // 返回
    const goBack = () => {
      router.push('/report-templates')
    }

    // 监听粘贴事件，支持直接粘贴图片
    const handlePaste = async (e) => {
      const items = e.clipboardData.items
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          const file = items[i].getAsFile()
          
          // 上传图片
          const formData = new FormData()
          formData.append('file', file)
          
          try {
            const response = await request.post(
              `/reports/${reportId.value}/upload-image`,
              formData,
              {
                headers: {
                  'Content-Type': 'multipart/form-data'
                }
              }
            )
            
            if (response.success) {
              // 添加到当前激活的漏洞
              if (activeTab.value === 'vulnerabilities' && content.value.vulnerabilities.length > 0) {
                const lastIndex = content.value.vulnerabilities.length - 1
                if (!content.value.vulnerabilities[lastIndex].images) {
                  content.value.vulnerabilities[lastIndex].images = []
                }
                content.value.vulnerabilities[lastIndex].images.push({
                  name: response.attachment_id,
                  url: response.url
                })
                ElMessage.success('图片已粘贴')
                autoSave()
              }
            }
          } catch (error) {
            console.error('Paste image error:', error)
            ElMessage.error('粘贴图片失败')
          }
          
          e.preventDefault()
          break
        }
      }
    }

    onMounted(() => {
      loadReport()
      // 监听粘贴事件
      document.addEventListener('paste', handlePaste)
    })

    // 组件卸载时移除监听
    const onUnmounted = () => {
      document.removeEventListener('paste', handlePaste)
      if (autoSaveTimer) {
        clearTimeout(autoSaveTimer)
      }
    }

    return {
      loading,
      saving,
      activeTab,
      reportId,
      report,
      content,
      placeholders,
      uploadHeaders,
      loadReport,
      autoSave,
      saveReport,
      addVulnerability,
      copyVulnerability,
      deleteVulnerability,
      moveVulnerability,
      handleImageSuccess,
      beforeImageUpload,
      exportReport,
      goBack,
      onUnmounted
    }
  }
}
</script>

<style lang="scss" scoped>
.report-editor-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;

  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    background: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

    .header-left {
      display: flex;
      align-items: center;
      gap: 15px;

      h2 {
        margin: 0;
        font-size: 20px;
      }
    }

    .header-right {
      display: flex;
      gap: 10px;
    }
  }

  .editor-content {
    flex: 1;
    overflow: auto;
    padding: 20px;

    .editor-tabs {
      background: white;
      border-radius: 8px;
      padding: 20px;
      min-height: calc(100vh - 140px);
    }

    .form-section {
      h3 {
        margin-bottom: 20px;
        color: #303133;
      }
    }

    .vuln-section {
      .vuln-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;

        h3 {
          margin: 0;
        }
      }

      .vuln-list {
        display: flex;
        flex-direction: column;
        gap: 20px;

        .vuln-card {
          .vuln-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;

            .vuln-actions {
              display: flex;
              gap: 5px;
            }
          }

          .image-upload-area {
            .paste-tip {
              margin-top: 10px;
              color: #909399;
              font-size: 12px;
            }
          }
        }
      }
    }
  }
}
</style>
