<template>
  <el-row :gutter="16">
    <el-col :span="12">
      <el-card shadow="never">
        <template #header>导入 Excel</template>
        <p class="tip">
          列需包含：学号、姓名、院系、年级、班级、学业水平成绩、四类素养活动列、备注。活动单元格格式示例：<code
            >志愿者活动（2.5）</code
          >
          多条换行分隔。
        </p>
        <el-upload
          :auto-upload="false"
          :show-file-list="true"
          accept=".xlsx"
          :limit="1"
          :on-change="onFile"
        >
          <el-button type="primary">选择 .xlsx 文件</el-button>
        </el-upload>
        <div class="mt">
          <el-button type="success" :disabled="!fileRaw" :loading="previewing" @click="preview">
            解析并预览冲突
          </el-button>
        </div>
        <el-alert v-if="parseErrors.length" type="error" :closable="false" class="mt" title="解析错误">
          <ul>
            <li v-for="(e, i) in parseErrors" :key="i">{{ e }}</li>
          </ul>
        </el-alert>
        <div v-if="token" class="mt">
          <h4>导入预览（共 {{ rowCount }} 行）</h4>
          <template v-if="conflictRows.length">
            <p class="tip">
              以下学号已存在：选择「覆盖」将替换其基本信息与全部活动记录；「跳过」则保留系统原数据。
            </p>
            <el-table :data="conflictRows" border size="small" max-height="360">
              <el-table-column prop="student_id" label="学号" width="120" />
              <el-table-column label="策略" width="220">
                <template #default="{ row }">
                  <el-radio-group v-model="resolutions[row.student_id]">
                    <el-radio label="overwrite">覆盖</el-radio>
                    <el-radio label="skip">跳过</el-radio>
                  </el-radio-group>
                </template>
              </el-table-column>
              <el-table-column label="已有姓名">
                <template #default="{ row }">{{ row.existing?.name || "—" }}</template>
              </el-table-column>
              <el-table-column label="导入姓名">
                <template #default="{ row }">{{ row.incoming?.name }}</template>
              </el-table-column>
            </el-table>
          </template>
          <p v-else class="tip">无学号冲突，可直接确认导入。</p>
          <div class="mt">
            <el-button type="primary" :loading="confirming" @click="confirmImport">确认导入</el-button>
          </div>
        </div>
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card shadow="never">
        <template #header>导出 Excel</template>
        <p class="tip">导出将使用下列筛选条件（与列表页参数一致）。留空表示不限制。</p>
        <el-form :model="filters" label-width="100px">
          <el-form-item label="年级">
            <el-input v-model="filters.grade" clearable />
          </el-form-item>
          <el-form-item label="班级">
            <el-input v-model="filters.class" clearable />
          </el-form-item>
          <el-form-item label="学号起止">
            <el-input v-model="filters.student_id_min" placeholder="起" style="width: 45%; margin-right: 8px" clearable />
            <el-input v-model="filters.student_id_max" placeholder="止" style="width: 45%" clearable />
          </el-form-item>
          <el-form-item label="素质总分">
            <el-input v-model="filters.quality_min" placeholder="min" style="width: 45%; margin-right: 8px" clearable />
            <el-input v-model="filters.quality_max" placeholder="max" style="width: 45%" clearable />
          </el-form-item>
          <el-form-item label="综合分值">
            <el-input
              v-model="filters.comprehensive_min"
              placeholder="min"
              style="width: 45%; margin-right: 8px"
              clearable
            />
            <el-input v-model="filters.comprehensive_max" placeholder="max" style="width: 45%" clearable />
          </el-form-item>
          <el-form-item label="排序">
            <el-input v-model="filters.sort" placeholder="如 -comprehensive_score" clearable />
          </el-form-item>
        </el-form>
        <el-button type="primary" :loading="exporting" @click="doExport">导出 .xlsx</el-button>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { computed, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import http from "../api/http";

const fileRaw = ref(null);
const previewing = ref(false);
const confirming = ref(false);
const exporting = ref(false);
const token = ref("");
const conflicts = ref([]);
const rowCount = ref(0);
const parseErrors = ref([]);
const resolutions = reactive({});

const filters = reactive({
  grade: "",
  class: "",
  student_id_min: "",
  student_id_max: "",
  quality_min: "",
  quality_max: "",
  comprehensive_min: "",
  comprehensive_max: "",
  sort: "student_id",
});

const conflictRows = computed(() => conflicts.value.filter((c) => c.is_conflict));

function onFile(uploadFile) {
  fileRaw.value = uploadFile.raw;
  token.value = "";
  conflicts.value = [];
  parseErrors.value = [];
  Object.keys(resolutions).forEach((k) => delete resolutions[k]);
}

async function preview() {
  if (!fileRaw.value) return;
  previewing.value = true;
  parseErrors.value = [];
  token.value = "";
  conflicts.value = [];
  Object.keys(resolutions).forEach((k) => delete resolutions[k]);
  const fd = new FormData();
  fd.append("file", fileRaw.value);
  try {
    const { data } = await http.post("/import/preview/", fd, {
      headers: { "Content-Type": "multipart/form-data" },
      skipGlobalError: true,
    });
    token.value = data.token;
    conflicts.value = data.conflicts || [];
    rowCount.value = data.row_count || 0;
    conflicts.value.forEach((c) => {
      if (c.is_conflict) {
        resolutions[c.student_id] = "overwrite";
      }
    });
    ElMessage.success("解析成功，请确认冲突策略后导入");
  } catch (e) {
    const d = e.response?.data;
    if (d?.row_errors?.length) {
      parseErrors.value = d.row_errors;
    }
    const msg = d?.detail || e.message || "预览失败";
    ElMessage.error(typeof msg === "string" ? msg : JSON.stringify(msg));
  } finally {
    previewing.value = false;
  }
}

async function confirmImport() {
  if (!token.value) return;
  confirming.value = true;
  try {
    const { data } = await http.post("/import/confirm/", {
      token: token.value,
      resolutions,
    });
    ElMessage.success(`导入完成：成功 ${data.imported}，跳过 ${data.skipped}`);
    token.value = "";
    conflicts.value = [];
    fileRaw.value = null;
  } finally {
    confirming.value = false;
  }
}

function buildExportParams() {
  const p = {};
  Object.keys(filters).forEach((k) => {
    const v = filters[k];
    if (v !== "" && v != null) p[k] = v;
  });
  return p;
}

async function doExport() {
  exporting.value = true;
  try {
    const res = await http.get("/export/", {
      params: buildExportParams(),
      responseType: "blob",
      skipGlobalError: true,
    });
    const cd = res.headers["content-disposition"] || "";
    let name = null;
    const star = cd.match(/filename\*=UTF-8''([^;]+)/i);
    if (star) {
      try {
        name = decodeURIComponent(star[1].trim());
      } catch {
        name = star[1];
      }
    }
    if (!name) {
      const m = cd.match(/filename="?([^";]+)"?/);
      name = m ? m[1] : `学生综测导出_${Date.now()}.xlsx`;
    }
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = name;
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success("已开始下载");
  } catch (e) {
    if (e.response?.data instanceof Blob) {
      const text = await e.response.data.text();
      try {
        const j = JSON.parse(text);
        ElMessage.error(j.detail || text);
      } catch {
        ElMessage.error(text || "导出失败");
      }
    } else {
      throw e;
    }
  } finally {
    exporting.value = false;
  }
}
</script>

<style scoped>
.tip {
  color: #6b7280;
  font-size: 13px;
  line-height: 1.5;
  margin: 0 0 12px;
}
.mt {
  margin-top: 12px;
}
code {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
}
</style>
