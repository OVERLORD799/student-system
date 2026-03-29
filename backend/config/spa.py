from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse


def _dist_index_path() -> Path:
    return Path(settings.BASE_DIR).parent / "frontend" / "dist" / "index.html"


def root_hint(request):
    """未构建前端时，避免访问 / 出现难以理解的 404。"""
    return HttpResponse(
        """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>学生综测成绩系统</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 48px auto; padding: 0 16px; line-height: 1.6; }
    code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; }
    a { color: #2563eb; }
  </style>
</head>
<body>
  <h1>学生综测成绩系统（后端已启动）</h1>
  <p>当前没有可用的前端静态文件（缺少 <code>frontend/dist</code>）。请任选一种方式使用界面：</p>
  <ul>
    <li><strong>开发调试</strong>：在 <code>frontend</code> 目录执行 <code>npm install</code> 与 <code>npm run dev</code>，
      浏览器打开终端里提示的地址（一般为 <code>http://localhost:5173</code>）。接口会通过代理访问本机 8000 端口。</li>
    <li><strong>只跑一个端口</strong>：在 <code>frontend</code> 执行 <code>npm run build</code> 生成 <code>dist</code> 后，
      再访问本页即可加载 Web 界面。</li>
  </ul>
  <p>说明：你看到的「URLconf / empty path」是 Django 在 <code>DEBUG=True</code> 下对根路径未匹配路由的调试页；
    与 <code>migrate</code> 无关；执行迁移后若未构建前端，直接打开 <code>http://127.0.0.1:8000/</code> 就会出现该情况。</p>
  <p>接口自检：<a href="/api/students/">/api/students/</a> · 管理后台：<a href="/admin/">/admin/</a></p>
</body>
</html>""",
        content_type="text/html; charset=utf-8",
    )


def spa_index(request):
    path = _dist_index_path()
    if not path.is_file():
        raise Http404("前端未构建：请在 frontend 目录执行 npm install 与 npm run build")
    return FileResponse(path.open("rb"), content_type="text/html; charset=utf-8")
