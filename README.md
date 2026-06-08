# 小区智能门禁系统

Django + React 实现的小区智能门禁管理系统，覆盖门禁设备状态、访客通行记录、异常报警和开门日志查询。

## 功能模块

- 后端 `backend/access` 按模型、序列化器、视图、管理命令拆分，提供 REST API。
- 前端 `frontend/src/modules` 按业务页面拆分为运行总览、门禁设备、访客记录、异常报警、开门日志。
- 提供演示数据命令 `python manage.py seed_demo`。
- 提供 `docker-compose.yml` 一键启动前后端。

## 本地开发

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

前端：

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

访问地址：

- 前端：http://127.0.0.1:5173
- 后端 API：http://127.0.0.1:8000/api/
- 后台管理：http://127.0.0.1:8000/admin/

## Docker Compose 启动

```bash
docker compose up --build
```

启动后访问：

- 前端：http://127.0.0.1:19080
- 后端 API：http://127.0.0.1:18080/api/

## 主要 API

- `GET /api/stats/`：总览统计
- `GET /api/devices/`：门禁设备列表
- `GET /api/visitors/`：访客通行记录
- `GET /api/alarms/`：异常报警
- `GET /api/door-logs/`：开门日志，支持 `keyword`、`result`、`opener_type` 查询参数
