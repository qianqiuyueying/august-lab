# Git 配置和推送指南

## ✅ 当前 Git 配置状态

- **用户名**：qianqiuyueying
- **邮箱**：3044481323@qq.com
- **分支**：main
- **状态**：文件已暂存，等待提交

## 📝 步骤 1：创建初始提交

```bash
git commit -m "Initial commit: August.Lab project"
```

## 🔗 步骤 2：添加远程仓库

### 方式 A：使用 GitHub（推荐）

1. **在 GitHub 上创建新仓库**
   - 访问 https://github.com/new
   - 仓库名称：`august-lab`（或你喜欢的名称）
   - 选择 Public 或 Private
   - **不要**初始化 README、.gitignore 或 license（因为我们已经有了）

2. **添加远程仓库并推送**
   ```bash
   # 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
   git remote add origin https://github.com/YOUR_USERNAME/august-lab.git
   
   # 或者使用 SSH（如果你配置了 SSH 密钥）
   git remote add origin git@github.com:YOUR_USERNAME/august-lab.git
   
   # 推送代码
   git push -u origin main
   ```

### 方式 B：使用 Gitee（码云）

1. **在 Gitee 上创建新仓库**
   - 访问 https://gitee.com/projects/new
   - 仓库名称：`august-lab`
   - 选择公开或私有

2. **添加远程仓库并推送**
   ```bash
   git remote add origin https://gitee.com/YOUR_USERNAME/august-lab.git
   git push -u origin main
   ```

### 方式 C：使用其他 Git 托管服务

```bash
# GitLab
git remote add origin https://gitlab.com/YOUR_USERNAME/august-lab.git

# 自建 Git 服务器
git remote add origin git@your-server.com:username/august-lab.git
```

## 🚀 步骤 3：推送代码

```bash
# 首次推送（设置上游分支）
git push -u origin main

# 之后的推送
git push
```

## 🔐 认证方式

### HTTPS 方式（需要输入用户名和密码/Token）

如果使用 HTTPS，GitHub 现在要求使用 Personal Access Token 而不是密码：

1. 生成 Token：
   - GitHub: https://github.com/settings/tokens
   - 选择 `repo` 权限
   - 复制生成的 token

2. 推送时使用 token 作为密码

### SSH 方式（推荐，无需每次输入密码）

1. **检查是否已有 SSH 密钥**
   ```bash
   ls -al ~/.ssh
   ```

2. **如果没有，生成新的 SSH 密钥**
   ```bash
   ssh-keygen -t ed25519 -C "3044481323@qq.com"
   # 按 Enter 使用默认路径
   # 可以设置密码或直接按 Enter
   ```

3. **添加 SSH 密钥到 ssh-agent**
   ```bash
   # Windows (Git Bash)
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   
   # Linux/Mac
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

4. **复制公钥并添加到 GitHub/Gitee**
   ```bash
   # Windows (Git Bash)
   cat ~/.ssh/id_ed25519.pub
   
   # 复制输出的内容，添加到：
   # GitHub: https://github.com/settings/keys
   # Gitee: https://gitee.com/profile/sshkeys
   ```

5. **测试连接**
   ```bash
   # GitHub
   ssh -T git@github.com
   
   # Gitee
   ssh -T git@gitee.com
   ```

## 📋 常用 Git 命令

```bash
# 查看状态
git status

# 查看提交历史
git log --oneline

# 查看远程仓库
git remote -v

# 拉取最新代码
git pull

# 添加文件
git add .

# 提交更改
git commit -m "描述你的更改"

# 推送更改
git push
```

## ⚠️ 注意事项

1. **不要提交敏感信息**：
   - `.env` 文件（已在 .gitignore 中）
   - 数据库文件（`*.db`）
   - 密钥和密码

2. **首次推送前检查**：
   ```bash
   git status
   git log  # 应该能看到你的提交
   ```

3. **如果推送失败**：
   - 检查网络连接
   - 检查远程仓库地址是否正确
   - 检查认证信息是否正确

## 🎯 快速命令总结

```bash
# 1. 创建提交
git commit -m "Initial commit: August.Lab project"

# 2. 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/august-lab.git

# 3. 推送代码
git push -u origin main
```

完成！🎉

