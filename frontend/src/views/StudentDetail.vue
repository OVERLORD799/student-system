<template>
  <el-page-header @back="$router.push('/students')" class="mb">
    <template #content>
      <span class="title">学生详情</span>
    </template>
  </el-page-header>

  <el-card v-loading="loading" shadow="never" class="mb">
    <template #header>基本信息</template>
    <el-form :model="stu" label-width="120px" class="base-form">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="学号">
            <el-input v-model="stu.student_id" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="姓名">
            <el-input v-model="stu.name" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="院系">
            <el-input v-model="stu.department" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="年级">
            <el-input v-model="stu.grade" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="班级">
            <el-input v-model="stu.class_name" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="学业水平成绩">
            <el-input-number v-model="stu.academic_score" :min="0" :step="0.5" :precision="2" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="素质总分">
            <el-input :model-value="String(stu.quality_total)" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="综合分值">
            <el-input :model-value="String(stu.comprehensive_score)" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="备注">
            <el-input v-model="stu.remark" type="textarea" :rows="3" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-button type="primary" @click="saveBase">保存基本信息</el-button>
    </el-form>
  </el-card>

  <el-card shadow="never">
    <template #header>活动参与记录</template>
    <el-tabs v-model="activeCat">
      <el-tab-pane v-for="c in categories" :key="c" :label="c" :name="c">
        <div class="tab-actions">
          <el-button type="primary" size="small" @click="openAdd(c)">添加记录</el-button>
        </div>
        <el-table :data="filtered(c)" border stripe>
          <el-table-column label="活动名称" min-width="160">
            <template #default="{ row }">{{ row.activity.name }}</template>
          </el-table-column>
          <el-table-column label="标准分值" width="100">
            <template #default="{ row }">{{ row.activity.score }}</template>
          </el-table-column>
          <el-table-column label="实际得分" width="120">
            <template #default="{ row }">{{ row.actual_score ?? row.activity.score }}</template>
          </el-table-column>
          <el-table-column label="是否进阶" width="100">
            <template #default="{ row }">{{ row.activity.is_advanced ? "是" : "否" }}</template>
          </el-table-column>
          <el-table-column label="参与时间" width="130">
            <template #default="{ row }">{{ row.participate_date || "—" }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openEditRow(row)">编辑</el-button>
              <el-button link type="danger" @click="removeRow(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </el-card>

  <el-dialog v-model="dlg" :title="dlgTitle" width="480px" destroy-on-close>
    <el-form :model="pa" label-width="100px">
      <el-form-item label="活动" required>
        <el-select v-model="pa.activity_id" filterable placeholder="选择活动" style="width: 100%">
          <el-option
            v-for="a in activityOptions"
            :key="a.activity_id"
            :label="`${a.name}（${a.score}）`"
            :value="a.activity_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="实际得分">
        <el-input-number v-model="pa.actual_score" :min="0" :step="0.5" :precision="2" />
        <div class="hint">留空则使用活动标准分值</div>
      </el-form-item>
      <el-form-item label="参与时间">
        <el-date-picker v-model="pa.participate_date" type="date" value-format="YYYY-MM-DD" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dlg = false">取消</el-button>
      <el-button type="primary" @click="saveParticipation">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { ElMessageBox } from "element-plus";
import http from "../api/http";

const categories = ["身心素养", "文艺素养", "劳动素养", "创新素养"];
const route = useRoute();
const loading = ref(false);
const stu = reactive({
  student_id: "",
  name: "",
  department: "",
  grade: "",
  class_name: "",
  academic_score: 0,
  quality_total: 0,
  comprehensive_score: 0,
  remark: "",
  participations: [],
});
const activeCat = ref(categories[0]);
const dlg = ref(false);
const dlgTitle = ref("");
const editingPartId = ref(null);
const dlgCategory = ref("");
const pa = reactive({
  activity_id: "",
  actual_score: null,
  participate_date: "",
});
const allActivities = ref([]);

const activityOptions = computed(() =>
  allActivities.value.filter((a) => a.category === dlgCategory.value)
);

function filtered(cat) {
  return (stu.participations || []).filter((p) => p.activity.category === cat);
}

async function load() {
  loading.value = true;
  try {
    const id = route.params.id;
    const { data } = await http.get(`/students/${id}/`);
    Object.assign(stu, data);
    stu.academic_score = Number(data.academic_score);
    const { data: acts } = await http.get("/activities/");
    allActivities.value = acts;
  } finally {
    loading.value = false;
  }
}

watch(
  () => route.params.id,
  () => load(),
  { immediate: true }
);

async function saveBase() {
  await http.patch(`/students/${stu.student_id}/`, {
    name: stu.name,
    department: stu.department,
    grade: stu.grade,
    class_name: stu.class_name,
    academic_score: stu.academic_score,
    remark: stu.remark,
  });
  await load();
}

function openAdd(cat) {
  dlgCategory.value = cat;
  editingPartId.value = null;
  dlgTitle.value = `添加参与记录 · ${cat}`;
  pa.activity_id = "";
  pa.actual_score = null;
  pa.participate_date = "";
  dlg.value = true;
}

function openEditRow(row) {
  dlgCategory.value = row.activity.category;
  editingPartId.value = row.id;
  dlgTitle.value = "编辑参与记录";
  pa.activity_id = row.activity.activity_id;
  pa.actual_score = row.actual_score != null ? Number(row.actual_score) : null;
  pa.participate_date = row.participate_date || "";
  dlg.value = true;
}

async function saveParticipation() {
  if (!pa.activity_id) {
    await ElMessageBox.alert("请选择活动", "提示", { type: "warning" });
    return;
  }
  const payload = {
    student_id: stu.student_id,
    activity_id: pa.activity_id,
    participate_date: pa.participate_date || null,
  };
  if (pa.actual_score != null && pa.actual_score !== "") {
    payload.actual_score = pa.actual_score;
  } else {
    payload.actual_score = null;
  }
  if (editingPartId.value) {
    await http.patch(`/participations/${editingPartId.value}/`, payload);
  } else {
    await http.post("/participations/", payload);
  }
  dlg.value = false;
  await load();
}

async function removeRow(row) {
  await ElMessageBox.confirm("确定删除该条参与记录？", "确认", { type: "warning" });
  await http.delete(`/participations/${row.id}/`);
  await load();
}
</script>

<style scoped>
.mb {
  margin-bottom: 16px;
}
.title {
  font-weight: 600;
}
.base-form {
  max-width: 1100px;
}
.tab-actions {
  margin-bottom: 10px;
}
.hint {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}
</style>
