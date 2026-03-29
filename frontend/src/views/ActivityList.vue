<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-head">
        <span>活动管理</span>
        <el-button type="primary" @click="openCreate">新增活动</el-button>
      </div>
    </template>
    <el-table :data="rows" v-loading="loading" border stripe>
      <el-table-column prop="activity_id" label="活动编号" width="140" />
      <el-table-column prop="name" label="活动名称" min-width="180" show-overflow-tooltip />
      <el-table-column prop="category" label="所属类别" width="120" />
      <el-table-column prop="score" label="标准分值" width="100" />
      <el-table-column label="是否进阶" width="100">
        <template #default="{ row }">{{ row.is_advanced ? "是" : "否" }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dlg" :title="dlgTitle" width="520px" destroy-on-close>
    <el-form :model="form" label-width="100px">
      <el-form-item label="活动编号" required>
        <el-input v-model="form.activity_id" :disabled="!!editingId" placeholder="如 A001" />
      </el-form-item>
      <el-form-item label="活动名称" required>
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="所属类别" required>
        <el-select v-model="form.category" style="width: 100%">
          <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
        </el-select>
      </el-form-item>
      <el-form-item label="标准分值" required>
        <el-input-number v-model="form.score" :min="0" :step="0.5" :precision="2" />
      </el-form-item>
      <el-form-item label="是否进阶">
        <el-switch v-model="form.is_advanced" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dlg = false">取消</el-button>
      <el-button type="primary" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import { ElMessageBox } from "element-plus";
import http from "../api/http";

const categories = ["身心素养", "文艺素养", "劳动素养", "创新素养"];
const rows = ref([]);
const loading = ref(false);
const dlg = ref(false);
const dlgTitle = ref("");
const editingId = ref("");
const form = reactive({
  activity_id: "",
  name: "",
  category: categories[0],
  score: 0,
  is_advanced: false,
});

async function load() {
  loading.value = true;
  try {
    const { data } = await http.get("/activities/");
    rows.value = data;
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  editingId.value = "";
  dlgTitle.value = "新增活动";
  Object.assign(form, {
    activity_id: "",
    name: "",
    category: categories[0],
    score: 0,
    is_advanced: false,
  });
  dlg.value = true;
}

function openEdit(row) {
  editingId.value = row.activity_id;
  dlgTitle.value = "编辑活动";
  Object.assign(form, {
    activity_id: row.activity_id,
    name: row.name,
    category: row.category,
    score: Number(row.score),
    is_advanced: !!row.is_advanced,
  });
  dlg.value = true;
}

async function save() {
  if (!form.activity_id || !form.name) {
    await ElMessageBox.alert("请填写活动编号与名称", "提示", { type: "warning" });
    return;
  }
  if (editingId.value) {
    await http.patch(`/activities/${editingId.value}/`, form);
  } else {
    await http.post("/activities/", form);
  }
  dlg.value = false;
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除活动「${row.name}」？`, "确认", { type: "warning" });
  try {
    await http.delete(`/activities/${row.activity_id}/`, { skipGlobalError: true });
    await load();
  } catch (e) {
    if (e.response?.status === 400) {
      await ElMessageBox.confirm(
        "该活动存在学生参与记录。是否级联删除所有相关参与记录后再删除活动？",
        "无法直接删除",
        { type: "warning" }
      );
      await http.delete(`/activities/${row.activity_id}/`, {
        params: { cascade: 1 },
      });
      await load();
    } else {
      throw e;
    }
  }
}

onMounted(load);
</script>

<style scoped>
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
