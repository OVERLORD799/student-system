import axios from "axios";
import { ElMessageBox } from "element-plus";

const http = axios.create({
  baseURL: "/api",
  timeout: 120000,
});

export function setupHttpErrors() {
  http.interceptors.response.use(
    (r) => r,
    async (err) => {
      if (err.config?.skipGlobalError) {
        return Promise.reject(err);
      }
      const res = err.response;
      let msg = err.message || "请求失败";
      if (res?.data) {
        const d = res.data;
        if (typeof d === "string") msg = d;
        else if (d.detail) msg = typeof d.detail === "string" ? d.detail : JSON.stringify(d.detail);
        else msg = JSON.stringify(d);
      }
      await ElMessageBox.alert(msg, "错误", { type: "error", confirmButtonText: "确定" });
      return Promise.reject(err);
    }
  );
}

export default http;
