import { createRouter, createWebHistory } from "vue-router";
import StudentList from "../views/StudentList.vue";
import StudentDetail from "../views/StudentDetail.vue";
import ActivityList from "../views/ActivityList.vue";
import ImportExport from "../views/ImportExport.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/students" },
    { path: "/students", name: "students", component: StudentList },
    { path: "/students/:id", name: "student-detail", component: StudentDetail },
    { path: "/activities", name: "activities", component: ActivityList },
    { path: "/io", name: "io", component: ImportExport },
  ],
});

export default router;
