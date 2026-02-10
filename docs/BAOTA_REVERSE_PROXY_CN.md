# 宝塔面板反向代理配置说明（August.Lab）

## 若出现 502：检查 `$connection_upgrade` 是否定义

宝塔生成的配置里常有：

```nginx
proxy_set_header Connection $connection_upgrade;
```

若 Nginx 未在 **http 块**中定义 `$connection_upgrade`，该变量为空，可能导致代理异常或 502。

**做法一（推荐）：在站点配置里不用该变量，改为透传客户端请求头**

在反向代理的 `location` 里，把：

- `proxy_set_header Connection $connection_upgrade;`  
改为：  
- `proxy_set_header Connection $http_connection;`  
- 并保留 `proxy_set_header Upgrade $http_upgrade;`

这样由客户端决定是否 WebSocket 升级，无需 map。

**做法二：在 Nginx 的 http 块中定义 map**

宝塔：**软件商店 → Nginx → 设置 → 配置修改**，在 `http {` 内部**最上面**增加：

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}
```

保存后重载 Nginx。

---

## 部署结构说明

- **backend 容器**：提供整站服务（前端 SPA + 接口），映射到主机端口 **8000**
- **nginx 容器**（可选）：项目自带，映射到主机 **8080**（HTTP）、**8443**（HTTPS）

若使用宝塔做反向代理，应**直接代理到 backend 的端口**，无需经过项目内的 nginx。

---

## 宝塔反向代理正确配置

### 1. 代理目标（重要）

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **代理地址** | `127.0.0.1` | 必须是本机，不能填容器名 |
| **端口** | `8000` | backend 在 docker-compose 中映射的端口 |
| **代理目录/路径** | **整站**（根路径 `/`） | 本项目的 backend 同时提供前端页面和 API，必须反代整站 |

**错误示例（会导致 502 或页面异常）：**

- 只代理 `/api/` → 访问首页会 404 或 502
- 端口填 `8080` → 那是项目内 nginx，若你打算用宝塔就不需要再经一层
- 代理地址填 `backend` 或容器名 → 宝塔的 Nginx 在主机上，解析不到 Docker 容器名

### 2. 在宝塔里操作步骤

1. **网站** → 你的域名 → **设置** → **反向代理** → **添加反向代理**
2. **代理名称**：随意，如 `August.Lab`
3. **目标 URL**：填 `http://127.0.0.1:8000`
4. **发送域名**：`$host`（默认即可）
5. **代理目录**：留空或选「根目录」表示代理整站
6. 提交后**重载 Nginx 配置**

### 3. 若宝塔生成的是「按目录代理」

请确保是**整站代理**，即：

- 不要只添加「代理目录」为 `/api`
- 应有一条规则：路径为 `/` 或整站，目标为 `http://127.0.0.1:8000`

否则访问 `https://你的域名/` 时没有反代到 8000，就会 404 或 502。

---

## 404 排查：/admin、/api/products 等返回 404

**现象**：访问 `http://你的域名/admin` 或 `http://你的域名/api/products` 返回 **404 Not Found**。

**原因说明：**

- 本项目的 **backend（端口 8000）** 同时提供：① 前端 SPA（含 `/admin` 等前端路由）；② 所有 API（如 `/api/products`）。
- 若宝塔里该站点**没有**把整站反向代理到 `http://127.0.0.1:8000`，而是：
  - 只把「网站根目录」指向某个静态目录（如 `frontend/dist`），或
  - 只配置了「代理目录」为 `/api` 且目标不对，
  则会出现：
  - **/admin 404**：Nginx 会去找服务器上的文件 `/admin` 或 `admin/index.html`，不存在就 404（前端路由应由后端返回 `index.html`）。
  - **/api/products 404**：请求没被转到后端，或只转了一部分路径，Nginx 没有对应 location 就 404。

**正确做法：整站反代到 backend**

1. 宝塔 → **网站** → 你的域名（如 wangzihao.space）→ **设置** → **反向代理**。
2. 确保有一条**整站**反向代理：
   - **代理目录**：根目录 `/`（或「整站」），**不要**只填 `/api`。
   - **目标 URL**：`http://127.0.0.1:8000`（若 502 再按本文「502 排查」改为 `http://172.17.0.1:8000`）。
3. 若之前有「仅代理 /api」的规则，可删除或改为整站代理，避免根路径和前端路由未走 backend。
4. 保存后**重载 Nginx**。

**自检（在服务器上执行）：**

```bash
# 后端是否正常
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health   # 应为 200
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/products   # 应为 200
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/admin   # 应为 200（后端会返回 index.html）
```

若本机 curl 已返回 200，但浏览器访问域名仍 404，说明 Nginx 未把该路径反代到 8000，请按上面步骤检查并改为**整站代理**。

---

## 502 排查步骤

### 步骤 1：确认 backend 在主机本机可访问

在**服务器上**执行（SSH 或宝塔终端）：

```bash
# 健康检查
curl -v http://127.0.0.1:8000/health

# 首页
curl -I http://127.0.0.1:8000/
```

- 若这里就无响应或连接被拒绝，说明 502 是「宝塔 Nginx 连不上 backend」，继续下面步骤。
- 若这里返回 200，说明 backend 正常，问题多半在宝塔的代理配置或代理路径。

### 情况：服务器 IP:8000 能访问，但域名反代后 502（必读）

**现象**：在浏览器或服务器上访问 `http://服务器IP:8000` 正常，但通过域名（经宝塔 Nginx 反代）访问就是 502。

**常见原因：宝塔的 Nginx 跑在 Docker 里**。此时：

- 你 SSH 到的是**宿主机**，`127.0.0.1:8000` 是宿主机上的端口，所以 `curl http://127.0.0.1:8000` 正常。
- 宝塔的 Nginx 进程在**容器内**，配置里的 `127.0.0.1` 对 Nginx 来说是**容器自己的本机**，容器里没有进程监听 8000，所以反代会 502。

**解决办法：让反代指向「宿主机」的地址，而不是 127.0.0.1。**

在反向代理里把目标从 `http://127.0.0.1:8000` 改成下面之一（按顺序试）：

| 目标地址 | 说明 |
|----------|------|
| `http://172.17.0.1:8000` | Linux 下 Docker 默认桥接网卡，多数情况有效 |
| `http://host.docker.internal:8000` | 若宝塔 Nginx 容器支持该主机名（部分环境需在 docker run 时加 `--add-host=host.docker.internal:host-gateway`） |
| `http://宿主机内网IP:8000` | 如 `192.168.x.x` 或 `10.x.x.x`，从容器能访问到的那个 IP |

**操作步骤：**

1. 宝塔 → **网站** → 你的域名 → **设置** → **反向代理** → 编辑当前反代。
2. 把 **目标 URL** 从 `http://127.0.0.1:8000` 改为 `http://172.17.0.1:8000`。
3. 保存并**重载 Nginx**，再用域名访问测试。

若 172.17.0.1 不行，在服务器上查一下「宿主机在 Docker 网桥上的 IP」：

```bash
# 宿主机在默认桥上的 IP（Linux）
ip addr show docker0 | grep inet
# 常见为 172.17.0.1
```

或看网关：

```bash
docker run --rm alpine ip route | grep default
# default via 172.17.0.1 表示容器内访问宿主机用 172.17.0.1
```

把得到的 IP 填到反代目标里（例如 `http://172.17.0.1:8000`）即可。

### 步骤 2：确认 8000 端口和容器在运行

```bash
cd /opt/august-lab   # 或你部署的项目目录
docker-compose ps
# 应看到 august-lab-backend 为 Up

# 查看端口
ss -tlnp | grep 8000
# 或
netstat -tlnp | grep 8000
```

应看到 `0.0.0.0:8000` 或 `*:8000` 在监听。

### 步骤 3：查看 backend 日志

```bash
docker-compose logs --tail=100 backend
```

看是否有启动失败、反复重启或报错。

### 步骤 4：检查宝塔 Nginx 错误日志

宝塔：**网站** → 你的站点 → **日志** → **错误日志**。  
查看 502 对应时间的错误，常见有：

- `connect() failed (111: Connection refused)` → 后端未监听或端口错
- `upstream timed out` → 后端响应过慢或未启动

### 步骤 5：核对宝塔生成的 Nginx 配置

宝塔：**网站** → 你的站点 → **设置** → **配置文件**。  
应能看到类似（具体以宝塔为准）：

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

重点确认：

- `proxy_pass` 为 `http://127.0.0.1:8000;`（末尾有无 `/` 会影响路径，整站代理一般不要多余 `/`）
- 没有只代理 `location /api/` 而导致根路径未代理

---

## 可选：不用宝塔反代，用项目内 Nginx

若你希望由项目内的 nginx 容器对外提供 80/443，可以：

1. 把 nginx 容器的端口改为 `80:80`、`443:443`（需先确保主机 80/443 没被宝塔占用，或停用宝塔对该域名的站点）。
2. 在宿主机不再用宝塔反代，直接通过域名访问服务器 80/443，由 Docker 的 nginx 反代到 backend。

此时访问的是「项目 nginx → backend」，不再经过宝塔 Nginx。

---

## 环境变量提醒

部署到域名后，请把 `.env` 里的 `ALLOWED_ORIGINS` 改成你的实际域名，例如：

```bash
ALLOWED_ORIGINS=https://你的域名.com,https://www.你的域名.com
```

否则跨域或 Cookie 可能异常（一般不会直接导致 502，但登录/接口可能异常）。

---

## 小结

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| 502 | 代理目标不是 127.0.0.1:8000 | 改为 `http://127.0.0.1:8000`，整站代理 |
| 502 | backend 未启动或崩溃 | `docker-compose ps`、`docker-compose logs backend` |
| 502 | 只代理了 /api/，根路径未代理 | 改为代理根路径 `/` 到 8000 |
| 本机 curl 127.0.0.1:8000 正常但域名 502 | 宝塔配置或 Nginx 未重载 | 检查站点配置、重载 Nginx、看错误日志 |

按上述检查后，若仍有 502，可把「本机 curl 结果」和「宝塔该站点错误日志片段」贴出便于进一步排查。
