# 🚀 August.Lab 快速部署指南

## 最简单的部署方式（推荐）

### 使用 Docker 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/your-username/august-lab.git
cd august-lab

# 2. 配置环境变量
cp env.example .env
# 编辑 .env 文件，修改 SECRET_KEY 和管理员密码

# 3. 运行部署脚本
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# 或者手动部署
docker-compose up -d
```

**就这么简单！** 服务将在以下地址运行：
- 前端：http://localhost
- API：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

## 详细部署文档

- **中文部署指南**：查看 [docs/DEPLOYMENT_CN.md](docs/DEPLOYMENT_CN.md)
- **英文部署指南**：查看 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **部署检查清单**：查看 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

## 部署前必读

### ⚠️ 必须修改的配置

1. **SECRET_KEY**：使用 `openssl rand -base64 64` 生成
2. **管理员密码**：修改默认密码 `admin123`
3. **域名配置**：如果使用自定义域名，修改 `.env` 中的域名相关配置

### 📋 系统要求

- **Docker 方式**：Docker + Docker Compose，2GB+ 内存
- **传统方式**：Ubuntu 20.04+ / Debian 11+，Python 3.8+，Node.js 18+，4GB+ 内存

---

## 常见问题

### Q: 如何配置 HTTPS？

A: 参考 [docs/DEPLOYMENT_CN.md](docs/DEPLOYMENT_CN.md) 中的 SSL 配置部分，使用 Let's Encrypt 免费证书。

### Q: 如何更新部署？

A: 
```bash
git pull
docker-compose build
docker-compose up -d
```

### Q: 如何查看日志？

A:
```bash
# Docker 方式
docker-compose logs -f

# 传统方式
sudo journalctl -u august-lab -f
```

---

## 获取帮助

如有问题，请查看详细文档或提交 Issue。

