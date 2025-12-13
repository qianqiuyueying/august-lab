# 修复 Git 推送问题

## 问题
`git: 'remote-https' is not a git command` 或 HTTPS 推送失败

## 解决方案

### 方案 1：临时禁用代理（推荐先试这个）

```bash
# 临时禁用代理推送
git -c http.proxy= -c https.proxy= push -u origin main
```

### 方案 2：使用 SSH 方式（最稳定）

1. **检查是否已有 SSH 密钥**
```bash
ls ~/.ssh
```

2. **如果没有，生成 SSH 密钥**
```bash
ssh-keygen -t ed25519 -C "3044481323@qq.com"
# 按 Enter 使用默认路径
# 可以设置密码或直接按 Enter
```

3. **复制公钥**
```bash
cat ~/.ssh/id_ed25519.pub
# 复制输出的内容
```

4. **添加到 GitHub**
   - 访问：https://github.com/settings/keys
   - 点击 "New SSH key"
   - 标题：随便填（如 "My PC"）
   - 密钥：粘贴刚才复制的公钥
   - 点击 "Add SSH key"

5. **测试连接**
```bash
ssh -T git@github.com
# 应该看到：Hi qianqiuyueying! You've successfully authenticated...
```

6. **修改远程仓库为 SSH 地址**
```bash
git remote set-url origin git@github.com:qianqiuyueying/august-lab.git
```

7. **推送**
```bash
git push -u origin main
```

### 方案 3：修复代理配置

如果代理端口 7890 不可用，可以临时禁用：

```bash
# 查看当前代理配置
git config --global --get http.proxy
git config --global --get https.proxy

# 临时禁用（仅本次推送）
git -c http.proxy= -c https.proxy= push -u origin main

# 或者永久禁用（如果不需要代理）
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 方案 4：使用 GitHub Desktop 或 GitHub CLI

如果命令行有问题，可以使用图形界面工具：
- GitHub Desktop: https://desktop.github.com/
- GitHub CLI: https://cli.github.com/

## 推荐方案

**最推荐使用 SSH 方式**，因为：
- 不需要每次输入密码
- 更安全
- 不受代理影响
- 一次配置，长期使用

