 # CI 自动部署规范
 
 ## 目标
 
 - 仅在 `main` 分支有 `push` 时自动部署到服务器
 - 跳过所有测试与代码检查环节，直接部署
 
 ## 部署触发
 
 - 事件：`push`
 - 分支：`main`
 
 ## 部署方式
 
 - 通过 SSH 连接服务器并执行部署脚本
 - 服务器地址：`192.144.154.17`
 - 用户名：`root`
 - 端口：`22`（若 SSH 改过端口，需在 `.github/workflows/ci.yml` 中同步修改）
 - 工作目录：`/www/wwwroot/August`
 - 部署脚本：`./scripts/deploy.sh`
- 部署脚本需在仓库中标记为可执行（git mode `+x`），避免执行时报 `Permission denied`
- 部署脚本生成的 `SECRET_KEY` 必须为单行字符串，避免写入 `.env` 时导致 `sed` 替换失败
- 前端构建依赖需锁定已验证兼容版本（例如 `typescript@5.3.3`），避免构建期版本漂移导致失败
- 若前端包含非 TypeScript 的 `.vue` 组件脚本，需在 `tsconfig.json` 启用 `allowJs`，避免 `vue-tsc` 构建失败
- Python 依赖安装需增加重试与超时（`pip install --retries 5 --timeout 120`），避免网络波动导致 “No matching distribution”
- 若服务器已占用 80/443（如宝塔面板），Nginx 容器需改用 8080/8443 端口映射
- 后端运行需确保 `app` 包可被找到（容器内设置 `PYTHONPATH=/app/backend`），否则会出现 `ModuleNotFoundError: No module named 'app'`
- 若后端以非 root 用户运行，宿主机 `backend/products`/`backend/uploads`/`logs` 需可写（部署前 `chown -R 1000:1000`），否则创建 `products/versions` 会失败
- SQLite 文件 `august_lab.db` 需存在且可写（部署前 `touch` 并 `chown 1000:1000`），否则会出现 “unable to open database file”

## 代码同步

- 代码来源：`git@github.com:qianqiuyueying/august-lab.git`
- 服务器需预置可访问该仓库的 SSH Key（例如 `/root/.ssh/id_rsa`）
- 服务器需已信任 `github.com`（例如将其写入 `~/.ssh/known_hosts`）
- 部署前需确保仓库目录归属为执行用户（`root:root`），避免 `dubious ownership` 导致 git 失败
- 若工作目录不存在：创建父目录并 `git clone` 到 `/www/wwwroot/August`
- 若工作目录已存在：在该目录内执行 `git pull` 更新
 
 ## 禁用的环节
 
 - 不执行任何测试（后端、前端、集成）
 - 不执行任何代码检查或格式化（`lint`/`black`/`flake8`/`isort`）
 - 不执行 CI 侧的 Docker 构建或镜像测试
 
## 失败处理

 - 部署脚本退出非 0 即视为失败
 - CI 保留脚本输出作为失败日志
 - 不做自动重试

## 常见错误排查

- **`dial tcp 192.144.154.17:52631: i/o timeout`**  
  表示 GitHub Actions 的 runner 无法连上服务器的 SSH 端口，连接在建立阶段就超时。请检查：  
  1. 服务器上 SSH 是否在目标端口监听（`ss -tlnp | grep sshd`）。  
  2. 云安全组/防火墙是否放行入站 SSH 端口（来源需允许 GitHub 出口 IP 或临时 0.0.0.0/0 测试）。  
  3. 若服务器在国内或网络受限，可考虑部署 [self-hosted runner](https://docs.github.com/en/actions/hosting-your-own-runners) 在同一内网执行部署。

- **`connect: connection refused`**  
  表示已能到达服务器，但目标端口没有服务监听。请确认：  
  1. CI 中 `port` 与服务器实际 SSH 监听端口一致（`ss -tlnp | grep sshd` 查看）。  
  2. 若 SSH 在 22，workflow 中应为 `port: 22`；若已改为 52631，需在服务器 `sshd_config` 中设置 `Port 52631` 并重启 `sshd`，且防火墙放行该端口。
 
 ## 机密信息
 
 - SSH 私钥仅通过 GitHub Secrets 注入
 - 不在仓库保存任何密钥
 