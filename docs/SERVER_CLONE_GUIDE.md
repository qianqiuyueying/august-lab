# 服务器上克隆仓库指南

## 📋 情况说明

### 公开仓库（Public）
- ✅ **可以直接克隆**，无需任何密钥
- 使用 HTTPS 或 SSH 都可以
- 任何人都可以克隆

### 私有仓库（Private）
- ❌ **需要认证**才能克隆
- 必须配置 SSH 密钥或使用 Personal Access Token
- 只有授权用户可以访问

## 🚀 方法一：公开仓库（最简单）

如果你的仓库是 **Public**，在服务器上直接执行：

```bash
# 使用 HTTPS（推荐，最简单）
git clone https://github.com/qianqiuyueying/august-lab.git

# 或者使用 SSH（如果已配置 SSH 密钥）
git clone git@github.com:qianqiuyueying/august-lab.git
```

**无需任何额外配置！**

## 🔐 方法二：私有仓库 + SSH 密钥（推荐）

如果仓库是 **Private**，需要在服务器上配置 SSH 密钥：

### 步骤 1：在服务器上生成 SSH 密钥

```bash
# 登录到服务器
ssh user@your-server.com

# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your-email@example.com"
# 按 Enter 使用默认路径
# 可以设置密码或直接按 Enter

# 查看公钥
cat ~/.ssh/id_ed25519.pub
```

### 步骤 2：将公钥添加到 GitHub

1. 复制服务器上的公钥内容
2. 访问：https://github.com/settings/keys
3. 点击 "New SSH key"
4. 粘贴公钥并保存

### 步骤 3：测试连接

```bash
ssh -T git@github.com
# 应该看到：Hi qianqiuyueying! You've successfully authenticated...
```

### 步骤 4：克隆仓库

```bash
git clone git@github.com:qianqiuyueying/august-lab.git
```

## 🔑 方法三：私有仓库 + Personal Access Token

如果不想配置 SSH，可以使用 HTTPS + Token：

### 步骤 1：生成 Personal Access Token

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择 `repo` 权限
4. 复制生成的 token（只显示一次！）

### 步骤 2：克隆时使用 Token

```bash
# 克隆时会提示输入用户名和密码
git clone https://github.com/qianqiuyueying/august-lab.git

# 用户名：qianqiuyueying
# 密码：粘贴你的 Personal Access Token（不是 GitHub 密码！）
```

### 步骤 3：保存凭据（可选）

```bash
# 配置 Git 凭据存储
git config --global credential.helper store

# 之后输入一次用户名和 token，Git 会自动保存
```

## 📝 完整部署流程示例

假设你要在服务器上部署项目：

```bash
# 1. 登录服务器
ssh user@your-server.com

# 2. 克隆仓库（公开仓库，最简单）
cd /opt
git clone https://github.com/qianqiuyueying/august-lab.git
cd august-lab

# 3. 配置环境变量
cp env.example .env
nano .env  # 修改配置

# 4. 使用 Docker 部署
docker-compose up -d

# 或者传统方式部署
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🔄 更新代码

```bash
# 进入项目目录
cd /opt/august-lab

# 拉取最新代码
git pull

# 如果有新依赖，重新构建
docker-compose build
docker-compose up -d
```

## ⚠️ 注意事项

1. **公开 vs 私有**：
   - 公开仓库：任何人都可以克隆，但只有你有推送权限
   - 私有仓库：需要认证才能克隆

2. **SSH vs HTTPS**：
   - SSH：需要配置密钥，但更安全，一次配置长期使用
   - HTTPS：简单，但私有仓库需要每次输入 token

3. **服务器安全**：
   - 不要在服务器上提交敏感信息
   - 使用 `.env` 文件管理配置，不要提交到 Git
   - 定期更新系统和依赖

## 🎯 推荐方案

**对于部署场景，推荐：**

1. **公开仓库** → 直接 HTTPS 克隆（最简单）
2. **私有仓库** → 配置 SSH 密钥（更安全，一次配置）

## 📚 相关文档

- 部署指南：`docs/DEPLOYMENT_CN.md`
- Git 配置：`GIT_SETUP.md`

