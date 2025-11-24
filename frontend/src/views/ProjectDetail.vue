<template>
  <div class="project-detail-container">
    <div class="light-bg-grid"></div>

    <div class="detail-header">
      <div class="header-left">
        <el-button 
          class="light-btn-back" 
          :icon="ArrowLeft" 
          @click="goBack" 
          circle 
          title="返回项目列表"
        />
        <div class="title-area">
          <h1>项目资产管理</h1>
          <span class="subtitle">ASSET MANAGEMENT DASHBOARD</span>
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
        
        <div class="top-section">
          <div class="action-bar">
            <div class="left-actions">
              <el-button type="primary" icon="Plus" @click="showAddDialog = true" class="tech-btn-primary">添加资产</el-button>
              
              <el-button-group class="tech-btn-group">
                <el-button type="primary" plain icon="Connection" @click="handleBatchResolveDNS" :disabled="selectedDomainAssets.length === 0">
                  解析IP {{ selectedDomainAssets.length > 0 ? `(${selectedDomainAssets.length})` : '' }}
                </el-button>
                <el-button type="primary" plain icon="Search" @click="showHttpProbeDialog" :disabled="selectedAssets.length === 0">
                  HTTP探测 {{ selectedAssets.length > 0 ? `(${selectedAssets.length})` : '' }}
                </el-button>
                <el-button type="info" plain icon="Document" @click="goToCurlTasks">
                  curl任务
                </el-button>
                 <el-button type="warning" plain icon="Share" @click="goToDomainMap">
                  域名透视
                </el-button>
                <el-button type="danger" plain icon="Warning" @click="goToVulnManagement">
                  漏洞管理
                </el-button>
              </el-button-group>

              <el-button-group class="tech-btn-group">
                <el-button plain icon="Filter" @click="showFilterPanel = !showFilterPanel">
                  {{ showFilterPanel ? '隐藏筛选' : '显示筛选' }}
                </el-button>
                <el-button plain icon="Refresh" @click="loadAssets" />
              </el-button-group>
              
              <el-button-group class="tech-btn-group">
                <el-button 
                  type="success" 
                  plain 
                  :icon="Download" 
                  @click="handleExportAll"
                >
                  导出全部
                </el-button>
                <el-button 
                  type="success" 
                  plain 
                  :icon="Download" 
                  @click="handleExportSelected"
                  :disabled="selectedAssets.length === 0"
                >
                  导出选中 {{ selectedAssets.length > 0 ? `(${selectedAssets.length})` : '' }}
                </el-button>
              </el-button-group>
              
              <el-button
                v-if="selectedAssets.length > 0"
                type="danger"
                plain
                icon="Delete"
                @click="handleBatchDelete"
                class="tech-btn-danger"
              >
                批量删除 ({{ selectedAssets.length }})
              </el-button>

              <el-button
                v-if="selectedAssets.length > 0"
                type="warning"
                plain
                icon="Share"
                @click="showAssignTaskDialog = true"
                class="tech-btn-warning"
              >
                任务下发 ({{ selectedAssets.length }})
              </el-button>

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
                <span class="value">{{ totalAssets }}</span>
              </div>
              <div class="stat-pill warning" v-if="hasActiveFilters">
                <span class="label">Filtered</span>
                <span class="value">{{ totalAssets }}</span>
              </div>
              <div class="stat-pill danger" v-if="selectedAssets.length > 0">
                <span class="label">Selected</span>
                <span class="value">{{ selectedAssets.length }}</span>
              </div>
            </div>
          </div>
          
          <el-collapse-transition>
            <div v-show="showFilterPanel" class="filter-panel">
              <el-form :model="filters" label-width="80px" size="small" class="filter-form">
                <el-row :gutter="24">
                  <el-col :span="6">
                    <el-form-item label="类型">
                      <el-select v-model="filters.asset_type" placeholder="全部" clearable class="tech-select">
                        <el-option label="全部" value="" />
                        <el-option label="域名" value="domain" />
                        <el-option label="HTTP" value="http" />
                        <el-option label="HTTPS" value="https" />
                        <el-option label="IP" value="ip" />
                        <el-option label="IP:Port" value="ip_port" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="6">
                    <el-form-item label="资产值">
                      <el-input v-model="filters.asset_value" placeholder="支持模糊搜索" clearable class="tech-input" />
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="6">
                    <el-form-item label="IP">
                      <el-input v-model="filters.ip" placeholder="支持模糊搜索" clearable class="tech-input" />
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="6">
                    <el-form-item label="端口">
                      <el-input v-model="filters.port" placeholder="精确匹配" clearable class="tech-input" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row :gutter="24">
                  <el-col :span="6">
                    <el-form-item label="协议">
                      <el-select v-model="filters.protocol" placeholder="全部" clearable class="tech-select">
                        <el-option label="全部" value="" />
                        <el-option label="HTTP" value="http" />
                        <el-option label="HTTPS" value="https" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="6">
                    <el-form-item label="标签">
                      <el-input v-model="filters.tag" placeholder="支持模糊搜索" clearable class="tech-input" />
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="6">
                    <el-form-item label="备注">
                      <el-input v-model="filters.notes" placeholder="支持模糊搜索" clearable class="tech-input" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="6">
                    <el-form-item label="创建者">
                      <el-input v-model="filters.creator_name" placeholder="支持模糊搜索" clearable class="tech-input" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row :gutter="24">
                  <el-col :span="6">
                    <el-form-item label="状态">
                      <el-select v-model="filters.status" placeholder="全部" clearable class="tech-select">
                        <el-option label="全部" value="" />
                        <el-option label="未测试" value="未测试" />
                        <el-option label="信息收集" value="信息收集" />
                        <el-option label="探测中" value="探测中" />
                        <el-option label="存在漏洞" value="存在漏洞" />
                        <el-option label="已验证可打点" value="已验证可打点" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="6">
                    <el-form-item label="风险等级">
                      <el-select v-model="filters.risk_level" placeholder="全部" clearable class="tech-select">
                        <el-option label="全部" value="" />
                        <el-option label="低风险" value="低风险" />
                        <el-option label="高危" value="高危" />
                        <el-option label="重点打点" value="重点打点" />
                        <el-option label="CDN" value="CDN" />
                        <el-option label="WAF" value="WAF" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="12">
                    <el-form-item label="创建时间">
                      <el-date-picker
                        v-model="filters.dateRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                        value-format="YYYY-MM-DD"
                        style="width: 100%"
                        class="tech-date-picker"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-form>
            </div>
          </el-collapse-transition>
        </div>
        
        <div class="table-main-container tech-card">
          <div class="table-wrapper">
            <el-table
              :data="paginatedAssets"
              v-loading="loading"
              stripe
              style="width: 100%; height: 100%; position: absolute; top: 0; left: 0;"
              @selection-change="handleSelectionChange"
              class="tech-table"
              header-cell-class-name="tech-table-header"
            >
              <el-table-column type="selection" width="45" align="center" />
              <el-table-column 
                type="index" 
                label="#" 
                width="55" 
                align="center" 
                class-name="index-col"
                :index="(index) => (pagination.currentPage - 1) * pagination.pageSize + index + 1"
              />
              
              <el-table-column prop="asset_type" label="类型" width="100" align="center">
                <template #default="{ row }">
                  <el-tag
                    :type="getTypeColor(row.asset_type)"
                    size="small"
                    effect="light"
                    class="type-tag"
                  >
                    {{ getTypeName(row.asset_type) }}
                  </el-tag>
                </template>
              </el-table-column>
              
              <el-table-column prop="asset_value" label="资产值" min-width="200">
                <template #default="{ row }">
                  <el-text class="asset-value-text" copyable>{{ row.asset_value }}</el-text>
                </template>
              </el-table-column>
              
              <el-table-column prop="ip" label="IP" width="140">
                <template #default="{ row }">
                  <span class="mono-text">{{ row.ip }}</span>
                </template>
              </el-table-column>
              
              <el-table-column prop="port" label="端口" width="80" align="center">
                 <template #default="{ row }">
                  <span class="mono-text">{{ row.port }}</span>
                </template>
              </el-table-column>
              
              <el-table-column prop="protocol" label="协议" width="80" align="center" />
              
              <el-table-column prop="title" label="指纹/标题" min-width="180" show-overflow-tooltip>
                <template #default="{ row }">
                  <span v-if="row.title" class="title-text">{{ row.title }}</span>
                  <span v-else class="empty-text">-</span>
                </template>
              </el-table-column>
              
              <el-table-column prop="content_length" label="大小" width="100" align="center">
                <template #default="{ row }">
                  <span v-if="row.content_length" class="mono-text size-text">{{ formatSize(row.content_length) }}</span>
                  <span v-else class="empty-text">-</span>
                </template>
              </el-table-column>
              
              <el-table-column prop="status" label="状态" width="120" align="center">
                <template #default="{ row }">
                  <el-select
                    v-model="row.status"
                    size="small"
                    @change="updateAsset(row)"
                    style="width: 100%;"
                    class="mini-select"
                  >
                    <el-option label="未测试" value="未测试" />
                    <el-option label="信息收集" value="信息收集" />
                    <el-option label="探测中" value="探测中" />
                    <el-option label="存在漏洞" value="存在漏洞" />
                    <el-option label="已验证" value="已验证可打点" />
                  </el-select>
                </template>
              </el-table-column>
              
              <el-table-column prop="risk_level" label="风险等级" width="110" align="center">
                <template #default="{ row }">
                  <el-select
                    v-model="row.risk_level"
                    size="small"
                    @change="updateAsset(row)"
                    placeholder="-"
                    clearable
                    style="width: 100%;"
                    class="mini-select"
                    :class="{'high-risk': row.risk_level === '高危'}"
                  >
                    <el-option label="低风险" value="低风险" />
                    <el-option label="高危" value="高危" />
                    <el-option label="重点" value="重点打点" />
                    <el-option label="CDN" value="CDN" />
                    <el-option label="WAF" value="WAF" />
                  </el-select>
                </template>
              </el-table-column>
              
              <el-table-column prop="tags" label="标签" width="200">
                <template #default="{ row }">
                  <div class="tags-container">
                    <el-tag
                      v-for="tag in row.tags"
                      :key="tag"
                      size="small"
                      closable
                      effect="plain"
                      @close="removeTag(row, tag)"
                      class="custom-tag"
                    >
                      {{ tag }}
                    </el-tag>
                    <el-button
                      size="small"
                      :icon="Plus"
                      circle
                      class="add-tag-btn"
                      title="添加标签"
                      @click="showTagDialog(row)"
                    />
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column prop="notes" label="备注" min-width="150">
                <template #default="{ row }">
                  <el-input
                    v-model="row.notes"
                    placeholder="点击添加..."
                    @blur="updateAsset(row)"
                    size="small"
                    class="note-input"
                  />
                </template>
              </el-table-column>
              
              <el-table-column prop="test_result" label="测试结果" width="100" align="center">
                <template #default="{ row }">
                  <el-button
                    size="small"
                    @click="showTestResultDialog(row)"
                    :type="row.test_result ? 'success' : 'info'"
                    :plain="!row.test_result"
                    text
                    bg
                    style="width: 100%"
                  >
                    {{ row.test_result ? '查看' : '添加' }}
                  </el-button>
                </template>
              </el-table-column>
              
              <el-table-column prop="creator_name" label="创建者" width="90" show-overflow-tooltip />
              
              <el-table-column prop="created_at" label="创建时间" width="150">
                <template #default="{ row }">
                  <span class="time-text">{{ formatTime(row.created_at) }}</span>
                </template>
              </el-table-column>
              
              <el-table-column label="操作" width="170" align="center" fixed="right">
                <template #default="{ row }">
                  <div class="row-actions">
                    <el-button
                      v-if="isDomainAsset(row)"
                      type="primary"
                      size="small"
                      icon="Connection"
                      text
                      bg
                      @click="handleResolveDNS(row)"
                    >
                      解析
                    </el-button>
                    <el-button
                      type="danger"
                      size="small"
                      icon="Delete"
                      text
                      bg
                      @click="handleDelete(row.id)"
                    >
                      删除
                    </el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="pagination.currentPage"
              v-model:page-size="pagination.pageSize"
              :page-sizes="pagination.pageSizes"
              :total="totalAssets"
              layout="total, sizes, prev, pager, next, jumper"
              background
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </div>
    </div>
    
    <el-dialog v-model="showAddDialog" title="批量添加资产" width="650px" class="tech-dialog">
        <div class="dialog-body-content">
        <el-alert title="智能识别格式" type="info" :closable="false" show-icon class="tech-alert">
           <template #default>
             <div class="alert-content-grid">
               <div><p><strong>标准格式：</strong></p><p class="code-sample">192.168.1.1</p></div>
               <div><p><strong>JSON / 混合：</strong></p><p class="code-sample">{"url":"..."}</p></div>
             </div>
           </template>
        </el-alert>
        <el-input v-model="assetText" type="textarea" :rows="10" placeholder="请在此粘贴资产列表..." class="tech-textarea" />
        
        <div style="margin-top: 16px;">
          <label style="display: block; margin-bottom: 8px; color: #606266; font-size: 14px;">
            批量标签（可选）
          </label>
          <el-input 
            v-model="batchTags" 
            placeholder="输入标签，多个标签用逗号、空格或分号分隔，例如：重点资产,高危,测试" 
            class="tech-input"
          >
            <template #prefix>
              <span style="color: #909399;">#</span>
            </template>
          </el-input>
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">
            这些标签将自动添加到所有新增的资产上
          </div>
        </div>
      </div>
      <template #footer><div class="dialog-footer"><el-button @click="showAddDialog = false">取消</el-button><el-button type="primary" @click="handleAddAssets" :loading="addLoading">确认添加</el-button></div></template>
    </el-dialog>
    
    <el-dialog v-model="showHttpProbeDialogVisible" title="HTTP探测配置" width="500px" class="tech-dialog"><div class="probe-config"><el-radio-group v-model="httpProbeMode" class="tech-radio-group"><div class="radio-card" :class="{ active: httpProbeMode === 'all' }" @click="httpProbeMode = 'all'"><el-radio label="all" size="large">全部探测</el-radio><p class="desc">对所有类型尝试 HTTP/HTTPS 请求</p></div><div class="radio-card" :class="{ active: httpProbeMode === 'http_only' }" @click="httpProbeMode = 'http_only'"><el-radio label="http_only" size="large">仅 Web 资产</el-radio><p class="desc">仅对已有协议的资产进行探测</p></div></el-radio-group></div><template #footer><el-button @click="showHttpProbeDialogVisible = false">取消</el-button><el-button type="primary" @click="handleHttpProbe" :loading="httpProbeLoading">开始扫描</el-button></template></el-dialog>
    
    <el-dialog v-model="showTagDialogVisible" title="添加标签" width="400px" class="tech-dialog"><el-input v-model="newTag" placeholder="输入新标签名称" @keyup.enter="handleAddTag" class="tech-input"><template #prefix>#</template></el-input><template #footer><el-button @click="showTagDialogVisible = false">取消</el-button><el-button type="primary" @click="handleAddTag">添加</el-button></template></el-dialog>
    
    <el-dialog v-model="showTestResultDialogVisible" title="测试结果记录" width="900px" class="tech-dialog wide-dialog" top="5vh"><div class="test-result-container"><el-tabs v-model="testResultTab" class="tech-tabs"><el-tab-pane label="编辑器 (Markdown)" name="edit"><el-input v-model="currentTestResult" type="textarea" :rows="18" class="tech-textarea code-font" /></el-tab-pane><el-tab-pane label="预览" name="preview"><div class="markdown-preview" v-html="renderedMarkdown"></div></el-tab-pane></el-tabs></div><template #footer><el-button @click="showTestResultDialogVisible = false">取消</el-button><el-button type="primary" @click="handleSaveTestResult" :loading="testResultSaving">保存记录</el-button></template></el-dialog>
    
    <el-dialog v-model="showAssignTaskDialog" title="任务下发" width="600px" class="tech-dialog">
      <div class="assign-task-content">
        <el-form :model="assignTaskForm" label-width="100px">
          <el-form-item label="选择接收人">
            <el-select 
              v-model="assignTaskForm.assignee_ids" 
              multiple 
              placeholder="请选择协作者" 
              style="width: 100%"
              :loading="inviteesLoading"
            >
              <el-option
                v-for="invitee in invitees"
                :key="invitee.id"
                :label="invitee.username"
                :value="invitee.id"
              />
            </el-select>
            <div style="margin-top: 8px; font-size: 12px; color: #909399;">
              已选择 {{ selectedAssets.length }} 个资产将被下发
            </div>
          </el-form-item>
          
          <el-form-item label="任务描述">
            <el-input
              v-model="assignTaskForm.task_description"
              type="textarea"
              :rows="3"
              placeholder="简要描述任务内容（可选）"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="项目可见性">
            <el-switch
              v-model="assignTaskForm.source_project_visible"
              active-text="源项目对接收人可见"
              inactive-text="源项目对接收人不可见"
            />
            <div style="margin-top: 8px; font-size: 12px; color: #909399;">
              控制接收人是否可以看到此源项目
            </div>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showAssignTaskDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAssignTask" :loading="assignTaskLoading">
          确认下发
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
// 引入图标
import { ArrowLeft, Plus, Download } from '@element-plus/icons-vue'
import request from '../utils/request'
import { marked } from 'marked'
import * as XLSX from 'xlsx'

export default {
  name: 'ProjectDetail',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const loading = ref(false)
    const addLoading = ref(false)
    const showAddDialog = ref(false)
    const showTagDialogVisible = ref(false)
    const showHttpProbeDialogVisible = ref(false)
    const showTestResultDialogVisible = ref(false)
    const showFilterPanel = ref(false)
    const assets = ref([])
    const totalAssets = ref(0)
    const selectedAssets = ref([])
    const assetText = ref('')
    const batchTags = ref('')
    const newTag = ref('')
    const currentAsset = ref(null)
    const currentTestResult = ref('')
    const testResultTab = ref('edit')
    const testResultSaving = ref(false)
    const httpProbeMode = ref('all')
    const httpProbeLoading = ref(false)
    const showAssignTaskDialog = ref(false)
    const assignTaskLoading = ref(false)
    const inviteesLoading = ref(false)
    const invitees = ref([])
    
    const assignTaskForm = reactive({
      assignee_ids: [],
      task_description: '',
      source_project_visible: true
    })
    
    const filters = reactive({
      asset_type: '',
      asset_value: '',
      ip: '',
      port: '',
      protocol: '',
      tag: '',
      notes: '',
      status: '',
      risk_level: '',
      creator_name: '',
      dateRange: null
    })
    
    const pagination = reactive({
      currentPage: 1,
      pageSize: 50,
      pageSizes: [20, 50, 100, 200, 500]
    })
    
    let filterDebounceTimer = null
    
    const projectId = computed(() => route.params.id)
    
    const currentUser = computed(() => {
      const user = localStorage.getItem('user')
      return user ? JSON.parse(user) : {}
    })
    
    const hasActiveFilters = computed(() => {
      return filters.asset_type !== '' ||
             filters.asset_value !== '' ||
             filters.ip !== '' ||
             filters.port !== '' ||
             filters.protocol !== '' ||
             filters.tag !== '' ||
             filters.notes !== '' ||
             filters.creator_name !== '' ||
             filters.dateRange !== null
    })
    
    const selectedDomainAssets = computed(() => {
      return selectedAssets.value.filter(asset => isDomainAsset(asset))
    })
    
    const renderedMarkdown = computed(() => {
      if (!currentTestResult.value) return '<p style="color: #999;">暂无内容</p>'
      try {
        return marked(currentTestResult.value)
      } catch (error) {
        return '<p style="color: #f56c6c;">Markdown 解析错误</p>'
      }
    })
    
    const paginatedAssets = computed(() => assets.value)
    
    const clearFilters = () => {
      filters.asset_type = ''
      filters.asset_value = ''
      filters.ip = ''
      filters.port = ''
      filters.protocol = ''
      filters.tag = ''
      filters.notes = ''
      filters.status = ''
      filters.risk_level = ''
      filters.creator_name = ''
      filters.dateRange = null
      pagination.currentPage = 1
      loadAssets()
    }
    
    const loadAssets = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.currentPage,
          page_size: pagination.pageSize
        }
        
        if (filters.asset_type) params.asset_type = filters.asset_type
        if (filters.asset_value) params.asset_value = filters.asset_value
        if (filters.ip) params.ip = filters.ip
        if (filters.port) params.port = filters.port
        if (filters.protocol) params.protocol = filters.protocol
        if (filters.tag) params.tag = filters.tag
        if (filters.notes) params.notes = filters.notes
        if (filters.status) params.status = filters.status
        if (filters.risk_level) params.risk_level = filters.risk_level
        if (filters.creator_name) params.creator_name = filters.creator_name
        if (filters.dateRange && filters.dateRange.length === 2) {
          params.start_date = filters.dateRange[0]
          params.end_date = filters.dateRange[1]
        }
        
        const response = await request.get(`/projects/${projectId.value}/assets`, { params })
        assets.value = response.assets
        totalAssets.value = response.total
      } catch (error) {
        console.error('Load assets error:', error)
        ElMessage.error('加载资产列表失败')
      } finally {
        loading.value = false
      }
    }
    
    const handleSizeChange = (val) => {
      pagination.pageSize = val
      pagination.currentPage = 1
      loadAssets()
    }
    
    const handleCurrentChange = (val) => {
      pagination.currentPage = val
      loadAssets()
    }
    
    watch(filters, () => {
      clearTimeout(filterDebounceTimer)
      filterDebounceTimer = setTimeout(() => {
        pagination.currentPage = 1
        loadAssets()
      }, 500)
    }, { deep: true })
    
    const handleAddAssets = async () => {
      if (!assetText.value.trim()) {
        ElMessage.warning('请输入资产信息')
        return
      }
      addLoading.value = true
      try {
        // 解析批量标签
        let tags = []
        if (batchTags.value.trim()) {
          // 支持逗号、分号、空格分隔
          tags = batchTags.value
            .split(/[,;，；\s]+/)
            .map(tag => tag.trim())
            .filter(tag => tag.length > 0)
        }
        
        const response = await request.post(`/projects/${projectId.value}/assets`, {
          asset_text: assetText.value,
          user_id: currentUser.value.id,
          batch_tags: tags
        })
        ElMessage.success(response.message)
        showAddDialog.value = false
        assetText.value = ''
        batchTags.value = ''
        await loadAssets()
      } catch (error) {
        console.error('Add assets error:', error)
      } finally {
        addLoading.value = false
      }
    }
    
    const showTagDialog = (asset) => {
      currentAsset.value = asset
      newTag.value = ''
      showTagDialogVisible.value = true
    }
    
    const handleAddTag = async () => {
      if (!newTag.value.trim()) {
        ElMessage.warning('请输入标签名称')
        return
      }
      if (currentAsset.value.tags.includes(newTag.value)) {
        ElMessage.warning('标签已存在')
        return
      }
      currentAsset.value.tags.push(newTag.value)
      await updateAsset(currentAsset.value)
      showTagDialogVisible.value = false
      newTag.value = ''
    }
    
    const removeTag = async (asset, tag) => {
      asset.tags = asset.tags.filter(t => t !== tag)
      await updateAsset(asset)
    }
    
    const updateAsset = async (asset) => {
      try {
        await request.put(`/assets/${asset.id}`, {
          tags: asset.tags,
          notes: asset.notes,
          status: asset.status,
          risk_level: asset.risk_level
        })
      } catch (error) {
        console.error('Update asset error:', error)
      }
    }
    
    const showTestResultDialog = (asset) => {
      currentAsset.value = asset
      currentTestResult.value = asset.test_result || ''
      testResultTab.value = 'edit'
      showTestResultDialogVisible.value = true
    }
    
    const handleSaveTestResult = async () => {
      if (!currentAsset.value) return
      testResultSaving.value = true
      try {
        await request.put(`/assets/${currentAsset.value.id}`, {
          tags: currentAsset.value.tags,
          notes: currentAsset.value.notes,
          status: currentAsset.value.status,
          risk_level: currentAsset.value.risk_level,
          test_result: currentTestResult.value
        })
        currentAsset.value.test_result = currentTestResult.value
        ElMessage.success('测试结果保存成功')
        showTestResultDialogVisible.value = false
      } catch (error) {
        console.error('Save test result error:', error)
      } finally {
        testResultSaving.value = false
      }
    }
    
    const handleDelete = async (id) => {
      try {
        await ElMessageBox.confirm('确定要删除这个资产吗？', '提示', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
        await request.delete(`/assets/${id}`)
        ElMessage.success('删除成功')
        await loadAssets()
      } catch (error) { if (error !== 'cancel') console.error('Delete asset error:', error) }
    }
    
    const handleSelectionChange = (selection) => {
      selectedAssets.value = selection
    }
    
    const handleBatchDelete = async () => {
      if (selectedAssets.value.length === 0) {
        ElMessage.warning('请先选择要删除的资产')
        return
      }
      try {
        await ElMessageBox.confirm(`确定要删除选中的 ${selectedAssets.value.length} 个资产吗？此操作不可恢复！`, '批量删除确认', { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning', distinguishCancelAndClose: true })
        loading.value = true
        const deletePromises = selectedAssets.value.map(asset => request.delete(`/assets/${asset.id}`))
        await Promise.all(deletePromises)
        ElMessage.success(`成功删除 ${selectedAssets.value.length} 个资产`)
        selectedAssets.value = []
        await loadAssets()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Batch delete error:', error)
          ElMessage.error('批量删除失败')
        }
      } finally {
        loading.value = false
      }
    }
    
    const loadInvitees = async () => {
      inviteesLoading.value = true
      try {
        const response = await request.get(`/users/${currentUser.value.id}/invitees`)
        invitees.value = response.invitees || []
      } catch (error) {
        console.error('Load invitees error:', error)
        ElMessage.error('加载协作者列表失败')
      } finally {
        inviteesLoading.value = false
      }
    }
    
    const handleAssignTask = async () => {
      if (assignTaskForm.assignee_ids.length === 0) {
        ElMessage.warning('请选择任务接收人')
        return
      }
      
      if (selectedAssets.value.length === 0) {
        ElMessage.warning('请选择要下发的资产')
        return
      }
      
      try {
        assignTaskLoading.value = true
        const asset_ids = selectedAssets.value.map(asset => asset.id)
        
        const response = await request.post(`/projects/${projectId.value}/assign-task`, {
          assignee_ids: assignTaskForm.assignee_ids,
          asset_ids: asset_ids,
          task_description: assignTaskForm.task_description,
          source_project_visible: assignTaskForm.source_project_visible
        })
        
        ElMessage.success(response.message || '任务下发成功')
        showAssignTaskDialog.value = false
        assignTaskForm.assignee_ids = []
        assignTaskForm.task_description = ''
        assignTaskForm.source_project_visible = true
        selectedAssets.value = []
      } catch (error) {
        console.error('Assign task error:', error)
        ElMessage.error('任务下发失败')
      } finally {
        assignTaskLoading.value = false
      }
    }
    
    watch(showAssignTaskDialog, (newVal) => {
      if (newVal) {
        loadInvitees()
      }
    })
    
    const getTypeName = (type) => {
      const typeMap = { 'ip': 'IP', 'ip_port': 'IP:Port', 'http': 'HTTP', 'https': 'HTTPS', 'domain': '域名' }
      return typeMap[type] || type
    }
    
    const getTypeColor = (type) => {
      const colorMap = { 'ip': 'info', 'ip_port': 'warning', 'http': 'success', 'https': 'danger', 'domain': 'primary' }
      return colorMap[type] || 'info'
    }
    
    const isDomainAsset = (asset) => {
      if (asset.asset_type === 'domain') return true
      if (asset.asset_type === 'http' || asset.asset_type === 'https') {
        const match = asset.asset_value.match(/https?:\/\/([^:/]+)/)
        if (match) {
          const host = match[1]
          const ipPattern = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/
          return !ipPattern.test(host)
        }
      }
      return false
    }
    
    const handleResolveDNS = async (asset) => {
      try {
        const response = await request.post(`/assets/${asset.id}/resolve-dns`)
        ElMessage.success(`${response.domain} 解析成功: ${response.ip}`)
        asset.ip = response.ip
        await loadAssets()
      } catch (error) { console.error('DNS resolution error:', error) }
    }
    
    const handleBatchResolveDNS = async () => {
      if (selectedDomainAssets.value.length === 0) {
        ElMessage.warning('请先选择需要解析的域名资产')
        return
      }
      try {
        await ElMessageBox.confirm(`确定要解析选中的 ${selectedDomainAssets.value.length} 个域名资产吗？`, '批量DNS解析', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'info' })
        const total = selectedDomainAssets.value.length
        let success = 0, failed = 0
        const loadingMessage = ElMessage({ message: `正在解析 0/${total}...`, type: 'info', duration: 0, showClose: false })
        const promises = selectedDomainAssets.value.map(async (asset) => {
          try {
            const response = await request.post(`/assets/${asset.id}/resolve-dns`)
            success++
            loadingMessage.message = `正在解析 ${success + failed}/${total}... (成功: ${success}, 失败: ${failed})`
            return { success: true, asset, response }
          } catch (error) {
            failed++
            loadingMessage.message = `正在解析 ${success + failed}/${total}... (成功: ${success}, 失败: ${failed})`
            return { success: false, asset, error }
          }
        })
        await Promise.all(promises)
        loadingMessage.close()
        if (failed === 0) ElMessage.success(`批量解析完成！成功解析 ${success} 个域名`)
        else if (success === 0) ElMessage.error(`批量解析失败！${failed} 个域名解析失败`)
        else ElMessage.warning(`批量解析完成！成功 ${success} 个，失败 ${failed} 个`)
        await loadAssets()
      } catch (error) { if (error !== 'cancel') console.error('Batch DNS resolution error:', error) }
    }
    
    const formatTime = (time) => {
      if (!time) return ''
      const date = new Date(time)
      return date.toLocaleString('zh-CN')
    }
    
    const formatSize = (bytes) => {
      if (!bytes) return '-'
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
    }
    
    const showHttpProbeDialog = () => {
      if (selectedAssets.value.length === 0) {
        ElMessage.warning('请先选择要探测的资产')
        return
      }
      showHttpProbeDialogVisible.value = true
    }
    
    const handleHttpProbe = async () => {
      try {
        await ElMessageBox.confirm(`确定要对选中的 ${selectedAssets.value.length} 个资产进行HTTP探测吗？`, '确认探测', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
        showHttpProbeDialogVisible.value = false
        httpProbeLoading.value = true
        let assetsToProbe = selectedAssets.value
        if (httpProbeMode.value === 'http_only') {
          assetsToProbe = selectedAssets.value.filter(asset => asset.asset_type === 'http' || asset.asset_type === 'https')
          if (assetsToProbe.length === 0) {
            ElMessage.warning('选中的资产中没有HTTP/HTTPS类型')
            httpProbeLoading.value = false
            return
          }
        }
        const total = assetsToProbe.length
        let success = 0, failed = 0
        const loadingMessage = ElMessage({ message: `正在探测 0/${total}... (成功: 0, 失败: 0)`, type: 'info', duration: 0, showClose: false })
        const promises = assetsToProbe.map(async (asset) => {
          try {
            const response = await request.post(`/assets/${asset.id}/http-probe`)
            if (response.success) {
              success++
              const assetIndex = assets.value.findIndex(a => a.id === asset.id)
              if (assetIndex !== -1 && response.best_result) {
                assets.value[assetIndex].title = response.best_result.title
                assets.value[assetIndex].content_length = response.best_result.content_length
              }
            } else failed++
            loadingMessage.message = `正在探测 ${success + failed}/${total}... (成功: ${success}, 失败: ${failed})`
            return { success: response.success, asset, response }
          } catch (error) {
            failed++
            loadingMessage.message = `正在探测 ${success + failed}/${total}... (成功: ${success}, 失败: ${failed})`
            return { success: false, asset, error }
          }
        })
        await Promise.all(promises)
        loadingMessage.close()
        httpProbeLoading.value = false
        if (failed === 0) ElMessage.success(`HTTP探测完成！成功探测 ${success} 个资产`)
        else if (success === 0) ElMessage.error(`HTTP探测失败！${failed} 个资产探测失败`)
        else ElMessage.warning(`HTTP探测完成！成功 ${success} 个，失败 ${failed} 个`)
        await loadAssets()
      } catch (error) {
        httpProbeLoading.value = false
        if (error !== 'cancel') console.error('HTTP probe error:', error)
      }
    }
    
    // 导出Excel功能
    const exportToExcel = (data, filename) => {
      // 准备导出数据
      const exportData = data.map((asset, index) => ({
        '序号': index + 1,
        '类型': getTypeName(asset.asset_type),
        '资产值': asset.asset_value,
        'IP': asset.ip || '-',
        '端口': asset.port || '-',
        '协议': asset.protocol || '-',
        'URL': asset.url || '-',
        '标题': asset.title || '-',
        '大小': asset.content_length ? formatSize(asset.content_length) : '-',
        '标签': asset.tags && asset.tags.length > 0 ? asset.tags.join(', ') : '-',
        '备注': asset.notes || '-',
        '状态': asset.status || '-',
        '风险等级': asset.risk_level || '-',
        '创建者': asset.creator_name || '-',
        '创建时间': formatTime(asset.created_at)
      }))
      
      // 创建工作表
      const ws = XLSX.utils.json_to_sheet(exportData)
      
      // 设置列宽
      const colWidths = [
        { wch: 6 },   // 序号
        { wch: 10 },  // 类型
        { wch: 30 },  // 资产值
        { wch: 15 },  // IP
        { wch: 8 },   // 端口
        { wch: 10 },  // 协议
        { wch: 40 },  // URL
        { wch: 30 },  // 标题
        { wch: 10 },  // 大小
        { wch: 20 },  // 标签
        { wch: 30 },  // 备注
        { wch: 12 },  // 状态
        { wch: 12 },  // 风险等级
        { wch: 12 },  // 创建者
        { wch: 20 }   // 创建时间
      ]
      ws['!cols'] = colWidths
      
      // 创建工作簿
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, '资产列表')
      
      // 导出文件
      XLSX.writeFile(wb, filename)
    }
    
    const handleExportAll = async () => {
      // 检查数据量
      if (totalAssets.value > 10000) {
        try {
          await ElMessageBox.confirm(
            '数据量过大，导出可能会卡顿，建议增加筛选，您是否要继续导出？',
            '数据量提醒',
            {
              confirmButtonText: '继续导出',
              cancelButtonText: '取消',
              type: 'warning'
            }
          )
        } catch {
          return // 用户取消
        }
      }
      
      const loadingMsg = ElMessage({
        message: '正在导出数据，请稍候...',
        type: 'info',
        duration: 0
      })
      
      try {
        // 获取所有资产数据（不分页）
        const response = await request.get(`/projects/${projectId.value}/assets`, {
          params: {
            page: 1,
            page_size: totalAssets.value, // 获取全部
            ...filters
          }
        })
        
        if (response.assets && response.assets.length > 0) {
          const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
          exportToExcel(response.assets, `资产列表_全部_${timestamp}.xlsx`)
          ElMessage.success(`成功导出 ${response.assets.length} 条资产`)
        } else {
          ElMessage.warning('没有可导出的数据')
        }
      } catch (error) {
        console.error('Export error:', error)
        ElMessage.error('导出失败')
      } finally {
        loadingMsg.close()
      }
    }
    
    const handleExportSelected = () => {
      if (selectedAssets.value.length === 0) {
        ElMessage.warning('请先选择要导出的资产')
        return
      }
      
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
      exportToExcel(selectedAssets.value, `资产列表_选中_${timestamp}.xlsx`)
      ElMessage.success(`成功导出 ${selectedAssets.value.length} 条资产`)
    }
    
    const goBack = () => { router.push('/dashboard') }
    const goToDomainMap = () => { router.push(`/project/${projectId.value}/domain-map`) }
    const goToCurlTasks = () => { router.push(`/project/${projectId.value}/curl-tasks`) }
    const goToVulnManagement = () => { router.push(`/project/${projectId.value}/vulnerabilities`) }
    
    onMounted(() => { loadAssets() })
    
    return {
      loading, addLoading, showAddDialog, showTagDialogVisible, showHttpProbeDialogVisible, showTestResultDialogVisible,
      showFilterPanel, assets, totalAssets, selectedAssets, selectedDomainAssets, paginatedAssets, pagination,
      assetText, batchTags, newTag, currentTestResult, testResultTab, testResultSaving, renderedMarkdown, currentUser,
      filters, hasActiveFilters, httpProbeMode, httpProbeLoading, clearFilters, loadAssets, handleAddAssets,
      showTagDialog, handleAddTag, removeTag, updateAsset, showTestResultDialog, handleSaveTestResult, handleDelete,
      handleSelectionChange, handleBatchDelete, handleBatchResolveDNS, getTypeName, getTypeColor, isDomainAsset,
      handleResolveDNS, formatTime, formatSize, showHttpProbeDialog, handleHttpProbe, handleSizeChange, handleCurrentChange,
      handleExportAll, handleExportSelected,
      showAssignTaskDialog, assignTaskForm, assignTaskLoading, invitees, inviteesLoading, handleAssignTask,
      goBack, goToDomainMap, goToCurlTasks, goToVulnManagement,
      // 必须返回图标
      ArrowLeft,
      Plus,
      Download
    }
  }
}
</script>

<style lang="scss" scoped>
/* 定义白色科技风变量 */
$bg-color: #f5f7fa;
$card-bg: #ffffff;
$primary-color: #2b5afb;
$text-main: #2c3e50;
$text-sub: #606266;
$border-color: #ebeef5;
$shadow-soft: 0 8px 24px rgba(149, 157, 165, 0.08);

.project-detail-container {
  width: 100%;
  height: 100vh; /* 核心：视口高度锁死 */
  display: flex;
  flex-direction: column;
  background: $bg-color;
  position: relative;
  overflow: hidden; /* 核心：禁止页面级滚动 */
  
  .light-bg-grid {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background-image: radial-gradient(#dce1e6 1.5px, transparent 1.5px);
    background-size: 30px 30px;
    opacity: 0.6;
    z-index: 0;
    pointer-events: none;
  }

  .detail-header {
    height: 64px;
    flex-shrink: 0;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid $border-color;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    z-index: 10;
    
    .header-left {
      display: flex; align-items: center; gap: 16px;
      
      .light-btn-back {
        background: #ffffff;
        border: 1px solid #dcdfe6;
        color: #303133;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 36px;
        height: 36px;
        font-size: 16px;

        &:hover {
          color: $primary-color;
          border-color: $primary-color;
          background: #ecf5ff;
          box-shadow: 0 4px 12px rgba(43, 90, 251, 0.2);
          transform: translateY(-1px);
        }

        &:active {
          transform: translateY(0);
          box-shadow: 0 2px 4px rgba(43, 90, 251, 0.1);
        }
      }

      .title-area {
        display: flex; flex-direction: column;
        h1 { font-size: 18px; color: $text-main; margin: 0; font-weight: 700; line-height: 1.2; }
        .subtitle { font-size: 10px; color: #909399; letter-spacing: 1px; transform: scale(0.95); transform-origin: left center; }
      }
    }
    
    .header-right .user-badge {
      display: flex; align-items: center; gap: 8px; padding: 4px 12px;
      background: #f5f7fa; border-radius: 20px; border: 1px solid $border-color;
      .user-avatar { background: $primary-color; color: #fff; }
      .user-info { font-size: 13px; color: $text-main; font-weight: 500; }
    }
  }
  
  .detail-content {
    flex: 1; /* 核心：自动占满剩余高度 */
    padding: 16px 24px;
    display: flex;
    flex-direction: column;
    overflow: hidden; /* 核心：防止内容撑破父容器 */
    z-index: 1;
    
    .content-wrapper {
      flex: 1; /* 核心：使用 flex: 1 代替 height: 100% */
      display: flex;
      flex-direction: column;
      min-height: 0; /* 关键：允许 Flex 子项高度小于内容高度 */
      gap: 16px;
    }

    .top-section {
      flex-shrink: 0; /* 顶部区域不压缩 */
    }

    .action-bar {
      display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;
      
      .left-actions {
        display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
        .tech-btn-group .el-button {
           border-radius: 0; border-color: #dcdfe6;
           &:first-child { border-top-left-radius: 4px; border-bottom-left-radius: 4px; }
           &:last-child { border-top-right-radius: 4px; border-bottom-right-radius: 4px; }
           &:hover, &:focus { color: $primary-color; border-color: lighten($primary-color, 20%); background-color: lighten($primary-color, 45%); z-index: 1; }
        }
        .tech-btn-primary { background: $primary-color; border-color: $primary-color; box-shadow: 0 4px 10px rgba(43, 90, 251, 0.2); &:hover { transform: translateY(-1px); } }
        .tech-btn-danger { background: #fff; border-color: #f56c6c; color: #f56c6c; &:hover { background: #fef0f0; } }
      }
      
      .stats .stat-pill {
        background: #fff; border: 1px solid $border-color; border-radius: 4px; padding: 4px 10px;
        display: flex; align-items: center; gap: 6px; font-size: 12px; color: $text-sub;
        .value { font-weight: 700; color: $text-main; }
        &.warning { background: #fdf6ec; border-color: #faecd8; color: #e6a23c; .value { color: #e6a23c; } }
        &.danger { background: #fef0f0; border-color: #fde2e2; color: #f56c6c; .value { color: #f56c6c; } }
      }
    }
    
    .filter-panel {
      background: $card-bg; border-radius: 8px; padding: 20px; margin-top: 16px;
      box-shadow: $shadow-soft; border: 1px solid $border-color;
      .tech-input, .tech-select { width: 100%; }
    }
    
    /* 表格容器 */
    .table-main-container {
      flex: 1; /* 占满剩余空间 */
      display: flex;
      flex-direction: column;
      min-height: 0; /* 必须：防止Flex溢出 */
      background: $card-bg;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid $border-color;
      box-shadow: $shadow-soft;

      .table-wrapper {
        flex: 1; 
        position: relative; /* 核心：给绝对定位的表格提供基准 */
        min-height: 0; 
      }

      .row-actions {
        display: flex; align-items: center; justify-content: center; gap: 8px;
        :deep(.el-button) {
          font-size: 12px; height: 24px; padding: 0 8px; border-radius: 4px; margin: 0; font-weight: 500;
          &.el-button--primary { color: $primary-color; &:hover { color: lighten($primary-color, 5%); background-color: rgba(43, 90, 251, 0.08); } }
          &.el-button--danger { color: #f56c6c; &:hover { color: #f78989; background-color: rgba(245, 108, 108, 0.08); } }
        }
      }
      
      .pagination-container {
        flex-shrink: 0; /* 核心：分页不被压缩 */
        padding: 12px 20px;
        border-top: 1px solid $border-color;
        background: #fafafa;
        display: flex;
        justify-content: center;
      }
      
      .asset-value-text { font-family: 'Consolas', monospace; font-size: 13px; color: #303133; background: #f4f4f5; padding: 2px 6px; border-radius: 4px; }
      .mono-text { font-family: 'Consolas', monospace; font-size: 13px; color: $text-sub; }
      .empty-text { color: #c0c4cc; }
      .title-text { color: $text-main; font-size: 13px; font-weight: 500; }
      .type-tag { font-weight: 500; }
      .tags-container { 
        display: flex; 
        flex-wrap: wrap; 
        gap: 4px; 
        align-items: center; 
        .custom-tag { border-radius: 4px; } 
        
        /* 新增按钮样式修复 */
        .add-tag-btn { 
          padding: 0;
          height: 20px; 
          width: 20px; 
          border: 1px dashed #c0c4cc; /* 虚线边框 */
          color: #909399;
          background: transparent;
          margin-left: 4px;
          
          &:hover {
             border-color: $primary-color;
             color: $primary-color;
             background-color: rgba(43, 90, 251, 0.1);
          }
        } 
      }
      .note-input :deep(.el-input__wrapper) { background: transparent; box-shadow: none; padding: 0; &:hover, &.is-focus { box-shadow: 0 1px 0 0 $border-color; } }
      .mini-select :deep(.el-input__wrapper) { box-shadow: none; background: transparent; padding: 0 8px; &:hover { background: #f5f7fa; } }
      .mini-select.high-risk :deep(.el-input__inner) { color: #f56c6c; font-weight: bold; }
      .time-text { font-size: 12px; color: #909399; }
    }
  }
}

/* Element Plus Deep Selectors */
:deep(.tech-table) {
  --el-table-header-bg-color: #f9fafc;
  --el-table-row-hover-bg-color: #f0f7ff;
  --el-table-border-color: #ebeef5;
  font-size: 13px;

  th.tech-table-header { color: $text-sub; font-weight: 600; height: 44px; border-bottom: 1px solid #ebeef5; }
  td.el-table__cell { padding: 8px 0; }
  .index-col .cell { color: #909399; font-size: 12px; }
}

:deep(.tech-dialog) {
  border-radius: 12px; overflow: hidden;
  .el-dialog__header { margin: 0; padding: 20px; border-bottom: 1px solid $border-color; background: #fff; .el-dialog__title { font-size: 16px; font-weight: 600; } }
  .el-dialog__body { padding: 24px; }
  .el-dialog__footer { padding: 16px 24px; border-top: 1px solid $border-color; background: #fbfbfc; }
}

.dialog-body-content {
  .tech-alert { margin-bottom: 16px; background-color: #f0f9eb; border: 1px solid #e1f3d8; &.el-alert--info { background-color: #f4f4f5; border-color: #e9e9eb; color: #909399; } .alert-content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 12px; .code-sample { font-family: 'Consolas', monospace; background: rgba(0,0,0,0.05); padding: 2px 4px; border-radius: 3px; display: inline-block; } } }
  .tech-textarea :deep(.el-textarea__inner) { font-family: 'Consolas', monospace; font-size: 13px; padding: 12px; background: #fff; &:focus { border-color: $primary-color; box-shadow: 0 0 0 2px rgba(43, 90, 251, 0.1); } }
}

.probe-config .tech-radio-group { display: flex; flex-direction: column; gap: 12px; .radio-card { border: 1px solid $border-color; border-radius: 8px; padding: 16px; cursor: pointer; &:hover { background: #f9fafc; } &.active { border-color: $primary-color; background: rgba(43, 90, 251, 0.02); box-shadow: 0 0 0 1px $primary-color inset; } .desc { margin: 4px 0 0 28px; font-size: 12px; color: #909399; } } }

.test-result-container {
  height: 600px; display: flex; flex-direction: column;
  .tech-tabs { height: 100%; display: flex; flex-direction: column; :deep(.el-tabs__header) { margin-bottom: 0; border-bottom: 1px solid $border-color; } :deep(.el-tabs__content) { flex: 1; padding: 0; overflow: hidden; } :deep(.el-tab-pane) { height: 100%; } }
  .code-font :deep(.el-textarea__inner) { font-family: 'Consolas', 'Menlo', monospace; height: 100%; border: none; resize: none; padding: 20px; background: #fafafa; &:focus { box-shadow: none; background: #fff; } }
  .markdown-preview {
    height: 100%; overflow-y: auto; padding: 30px 40px; background: #fff; color: #24292f; font-size: 14px; line-height: 1.6;
    :deep(h1) { border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; font-size: 2em; }
    :deep(pre) { background-color: #f6f8fa; border-radius: 6px; padding: 16px; }
  }
}
</style>