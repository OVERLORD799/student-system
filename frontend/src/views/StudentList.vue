<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-head">
        <span>学生成绩列表</span>
        <div>
          <el-button type="primary" @click="goCreate">新增学生</el-button>
          <el-button @click="$router.push('/io')">导入 / 导出</el-button>
        </div>
      </div>
    </template>
    <el-form :inline="true" :model="filters" class="filters">
      <el-form-item label="年级">
        <el-input v-model="filters.grade" clearable placeholder="如 2023级" />
      </el-form-item>
      <el-form-item label="班级">
        <el-input v-model="filters.class" clearable />
      </el-form-item>
      <el-form-item label="学号起">
        <el-input v-model="filters.student_id_min" clearable />
      </el-form-item>
      <el-form-item label="学号止">
        <el-input v-model="filters.student_id_max" clearable />
      </el-form-item>
      <el-form-item label="身心素养">
        <el-input v-model="filters.mind_min" placeholder="min" style="width: 90px" clearable />
        <span class="sep">-</span>
        <el-input v-model="filters.mind_max" placeholder="max" style="width: 90px" clearable />
      </el-form-item>
      <el-form-item label="文艺素养">
        <el-input v-model="filters.art_min" style="width: 90px" clearable />
        <span class="sep">-</span>
        <el-input v-model="filters.art_max" style="width: 90px" clearable />
      </el-form-item>
      <el-form-item label="劳动素养">
        <el-input v-model="filters.labor_min" style="width: 90px" clearable />
        <span class="sep">-</span>
        <el-input v-model="filters.labor_max" style="width: 90px" clearable />
      </el-form-item>
      <el-form-item label="创新素养">
        <el-input v-model="filters.innovation_min" style="width: 90px" clearable />
        <span class="sep">-</span>
        <el-input v-model="filters.innovation_max" style="width: 90px" clearable />
      </el-form-item>
      <el-form-item label="素质总分">
        <el-input v-model="filters.quality_min" style="width: 90px" clearable />
        <span class="sep">-</span>
        <el-input v-model="filters.quality_max" style="width: 90px" clearable />
      </el-form-item>
      <el-form-item label="综合分值">
        <el-input v-model="filters.comprehensive_min" style="width: 90px" clearable />
        <span class="sep">-</span>
        <el-input v-model="filters.comprehensive_max" style="width: 90px" clearable />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="load">搜索</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </el-form-item>
    </el-form>
    <el-table
      :data="rows"
      v-loading="loading"
      border
      stripe
      style="width: 100%"
      :default-sort="{ prop: 'student_id', order: 'ascending' }"
      @sort-change="onSort"
    >
      <el-table-column prop="student_id" label="学号" sortable="custom" min-width="110" fixed />
      <el-table-column prop="name" label="姓名" sortable="custom" min-width="90" />
      <el-table-column prop="department" label="院系" sortable="custom" min-width="120" show-overflow-tooltip />
      <el-table-column prop="grade" label="年级" sortable="custom" width="100" />
      <el-table-column prop="class_name" label="班级" sortable="custom" width="100" />
      <el-table-column prop="academic_score" label="学业水平成绩" sortable="custom" width="120" />
      <el-table-column prop="mind_total" label="身心素养总分" sortable="custom" width="120" />
      <el-table-column prop="art_total" label="文艺素养总分" sortable="custom" width="120" />
      <el-table-column prop="labor_total" label="劳动素养总分" sortable="custom" width="120" />
      <el-table-column prop="innovation_total" label="创新素养总分" sortable="custom" width="120" />
      <el-table-column prop="quality_total" label="素质总分" sortable="custom" width="100" />
      <el-table-column prop="comprehensive_score" label="综合分值" sortable="custom" width="100" />
      <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="$router.push(`/students/${row.student_id}`)">详情</el-button>
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px" destroy-on-close>
    <el-form :model="form" label-width="110px">
      <el-form-item label="学号" required>
        <el-input v-model="form.student_id" :disabled="!!editingId" />
      </el-form-item>
      <el-form-item label="姓名" required>
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="院系">
        <el-input v-model="form.department" />
      </el-form-item>
      <el-form-item label="年级">
        <el-input v-model="form.grade" />
      </el-form-item>
      <el-form-item label="班级">
        <el-input v-model="form.class_name" />
      </el-form-item>
      <el-form-item label="学业水平成绩">
        <el-input-number v-model="form.academic_score" :min="0" :step="0.5" :precision="2" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="3" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="saveStudent">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import { ElMessageBox } from "element-plus";
import http from "../api/http";

const rows = ref([]);
const loading = ref(false);
const sortParam = ref("student_id");
const dialogVisible = ref(false);
const dialogTitle = ref("");
const editingId = ref("");
const form = reactive({
  student_id: "",
  name: "",
  department: "",
  grade: "",
  class_name: "",
  academic_score: 0,
  remark: "",
});

const filters = reactive({
  grade: "",
  class: "",
  student_id_min: "",
  student_id_max: "",
  mind_min: "",
  mind_max: "",
  art_min: "",
  art_max: "",
  labor_min: "",
  labor_max: "",
  innovation_min: "",
  innovation_max: "",
  quality_min: "",
  quality_max: "",
  comprehensive_min: "",
  comprehensive_max: "",
});

function buildParams() {
  const p = { sort: sortParam.value };
  Object.keys(filters).forEach((k) => {
    const v = filters[k];
    if (v !== "" && v != null) p[k] = v;
  });
  return p;
}

async function load() {
  loading.value = true;
  try {
    const { data } = await http.get("/students/", { params: buildParams() });
    rows.value = data;
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  Object.keys(filters).forEach((k) => {
    filters[k] = "";
  });
  sortParam.value = "student_id";
  load();
}

function onSort({ prop, order }) {
  if (!prop || !order) {
    sortParam.value = "student_id";
  } else {
    sortParam.value = (order === "descending" ? "-" : "") + prop;
  }
  load();
}

function goCreate() {
  editingId.value = "";
  dialogTitle.value = "新增学生";
  Object.assign(form, {
    student_id: "",
    name: "",
    department: "",
    grade: "",
    class_name: "",
    academic_score: 0,
    remark: "",
  });
  dialogVisible.value = true;
}

function openEdit(row) {
  editingId.value = row.student_id;
  dialogTitle.value = "编辑学生";
  Object.assign(form, {
    student_id: row.student_id,
    name: row.name,
    department: row.department,
    grade: row.grade,
    class_name: row.class_name,
    academic_score: Number(row.academic_score),
    remark: row.remark,
  });
  dialogVisible.value = true;
}

async function saveStudent() {
  if (!form.student_id || !form.name) {
    await ElMessageBox.alert("请填写学号与姓名", "提示", { type: "warning" });
    return;
  }
  if (editingId.value) {
    await http.patch(`/students/${editingId.value}/`, form);
  } else {
    await http.post("/students/", form);
  }
  dialogVisible.value = false;
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除学生 ${row.student_id} ${row.name}？`, "确认", {
    type: "warning",
  });
  await http.delete(`/students/${row.student_id}/`);
  await load();
}

onMounted(load);
</script>

<style scoped>
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filters {
  margin-bottom: 12px;
}
.sep {
  margin: 0 6px;
  color: #9ca3af;
}
</style>
