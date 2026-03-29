<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="brand">学生综测成绩系统</div>
      <el-menu
        mode="horizontal"
        :default-active="active"
        router
        class="nav"
        background-color="#1f2937"
        text-color="#e5e7eb"
        active-text-color="#93c5fd"
      >
        <el-menu-item index="/students">学生管理</el-menu-item>
        <el-menu-item index="/activities">活动管理</el-menu-item>
        <el-menu-item index="/io">导入/导出</el-menu-item>
      </el-menu>
    </el-header>
    <el-main class="main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const active = computed(() => {
  if (route.path.startsWith("/students")) return "/students";
  if (route.path.startsWith("/activities")) return "/activities";
  if (route.path.startsWith("/io")) return "/io";
  return route.path;
});
</script>

<style>
html,
body,
#app {
  height: 100%;
  margin: 0;
}
.layout {
  min-height: 100vh;
}
.header {
  display: flex;
  align-items: center;
  gap: 24px;
  background: #1f2937;
  padding: 0 20px;
}
.brand {
  color: #f9fafb;
  font-weight: 600;
  font-size: 18px;
  white-space: nowrap;
}
.nav {
  flex: 1;
  border-bottom: none !important;
}
.main {
  background: #f3f4f6;
  min-height: calc(100vh - 60px);
}
</style>
