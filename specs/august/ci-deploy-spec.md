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
 - 端口：`52631`
 - 工作目录：`/www/wwwroot/August`
 - 部署脚本：`./scripts/deploy.sh`
- 部署脚本需在仓库中标记为可执行（git mode `+x`），避免执行时报 `Permission denied`

## 代码同步

- 代码来源：`git@github.com:qianqiuyueying/august-lab.git`
- 服务器需预置可访问该仓库的 SSH Key（例如 `/root/.ssh/id_rsa`）
- 服务器需已信任 `github.com`（例如将其写入 `~/.ssh/known_hosts`）
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
 
 ## 机密信息
 
 - SSH 私钥仅通过 GitHub Secrets 注入
 - 不在仓库保存任何密钥
 