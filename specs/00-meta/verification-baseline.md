# 可运行性验证基线规范

## 1. 目标与范围
- 目标：建立“不使用现有测试文件”的运行时冒烟验证基线
- 范围：本地开发环境（Windows）下的环境检查、服务启动、前后端运行时冒烟检查

## 2. 需求与业务规则
### 2.1 需求
- 必须执行环境检查脚本并确认输出可读
- 必须启动后端与前端服务并确认可访问
- 必须执行运行时冒烟检查并记录结果（脚本化命令）
- 必须覆盖：健康检查、公共页面、管理员登录、产品嵌入、文件上传、基础API、使用统计

### 2.2 规则
- 不得运行 `tests/` 或任何现有测试文件
- 单个冒烟检查无响应超过 60 秒视为卡住
- 卡住检查必须单独复现；仍卡住则停止并记录证据
- 不得跳过失败与错误；必须记录失败项与关键错误信息
- 需要认证的接口必须通过管理员登录获取令牌
- 若找不到可用的已发布产品（用于嵌入与统计），必须记录为 FAIL 并停止后续相关检查

## 3. 数据模型
### 3.1 验证记录
- 字段：command, started_at, ended_at, status, summary, evidence_path
- status: PASS | FAIL | ERROR | HANG

## 4. 执行与证据
### 4.1 环境检查
- 命令：`python check_env.py`
- 若控制台乱码，使用：`$env:PYTHONIOENCODING="utf-8"; python check_env.py`

### 4.2 服务启动
- 后端：`cd backend; python -m uvicorn main:app --reload --port 8001`
- 前端：`cd frontend; npm install; npm run dev`（首次运行需安装依赖）
- 记录：服务启动日志片段、监听端口

### 4.3 运行时冒烟检查（PowerShell）
```powershell
$api = "http://localhost:8001"
$web = "http://localhost:3000"

# 1) 健康检查
Invoke-RestMethod "$api/health"

# 2) 公共页面（前台与后台登录页，使用 curl.exe 获取状态码）
curl.exe -s -o NUL -w "%{http_code}`n" "$web/"
curl.exe -s -o NUL -w "%{http_code}`n" "$web/portfolio"
curl.exe -s -o NUL -w "%{http_code}`n" "$web/blog"
curl.exe -s -o NUL -w "%{http_code}`n" "$web/about"
curl.exe -s -o NUL -w "%{http_code}`n" "$web/admin/login"

# 3) 管理员登录（默认凭据来自环境变量）
$loginBody = @{ username = "admin"; password = "admin123" } | ConvertTo-Json
$loginRes = Invoke-RestMethod -Method Post -Uri "$api/api/auth/login" -Body $loginBody -ContentType "application/json"
$token = $loginRes.access_token
Invoke-RestMethod -Headers @{ Authorization = "Bearer $token" } "$api/api/auth/verify"

# 4) 基础 API（产品列表与详情）
$products = Invoke-RestMethod "$api/api/products?published_only=true"
if (-not $products -or $products.Count -eq 0) { throw "No published products" }
$productId = $products[0].id
Invoke-RestMethod "$api/api/products/$productId"

# 5) 产品嵌入（优先使用 /launch 返回的 entry_url）
$launch = Invoke-RestMethod "$api/api/products/$productId/launch"
curl.exe -4 -s -o NUL -w "%{http_code}`n" "$api$($launch.entry_url)"
curl.exe -s -o NUL -w "%{http_code}`n" "$web/product/$productId"

# 6) 使用统计
Invoke-RestMethod "$api/api/products/$productId/stats"

# 7) 文件上传（需要认证，使用 1x1 PNG 临时文件）
$tmpFile = Join-Path $env:TEMP "august-smoke.png"
[IO.File]::WriteAllBytes($tmpFile, [Convert]::FromBase64String("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/xcAAwMCAO3GgQkAAAAASUVORK5CYII="))
curl.exe -4 -s -X POST "$api/api/upload/image" -H "Authorization: Bearer $token" -F "file=@$tmpFile"
```
- 记录：每一步的请求与响应摘要（状态码、关键字段）

### 4.4 证据摘要
- 环境检查：`$env:PYTHONIOENCODING="utf-8"; python check_env.py` 输出可读，无乱码
- 服务启动：后端 `http://127.0.0.1:8001`，前端 `http://localhost:3000`
- 健康检查：`GET /health` 返回 `status=healthy`
- 公共页面：`/`、`/portfolio`、`/blog`、`/about`、`/admin/login` 通过 `curl.exe` 返回 200
- 管理员登录：`POST /api/auth/login` 成功，`GET /api/auth/verify` 返回成功消息（控制台中文存在编码显示问题，不影响响应）
- 基础 API：`GET /api/products?published_only=true` 返回产品列表；`GET /api/products/1` 返回产品详情
- 产品嵌入：`GET /api/products/1/launch` 返回 `entry_url=/products/1/index.html`；使用 `curl.exe -4` 访问 `entry_url` 返回 200；`/product/1` 返回 200
- 使用统计：`GET /api/products/1/stats` 返回统计摘要与分页
- 文件上传：`POST /api/upload/image` 返回 `message=文件上传成功` 与图片 URL
- 执行异常：`Invoke-WebRequest` 访问前端页面出现无响应（>60s），已改用 `curl.exe`；`curl.exe` 访问 `entry_url` 在 IPv6 下出现空响应，已改用 `curl.exe -4`

## 5. 完成标准
- 环境检查完成且输出可读
- 后端与前端服务可访问
- 运行时冒烟检查全部完成并有明确结果（PASS/FAIL/ERROR/HANG）
- 形成可继续排查的最小证据记录

## 6. 执行清单（同步更新）
- [x] 环境检查可运行且无乱码
- [x] 后端服务可启动并可访问
- [x] 前端服务可启动并可访问
- [x] 运行时冒烟检查已执行并记录结果
- [x] 失败/错误清单已对齐到具体规范条款
