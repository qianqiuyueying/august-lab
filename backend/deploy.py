import paramiko
import os
import time as t

host = "192.144.154.17"
user = "root"
password = "2313ynkhmymtm==="
deploy_dir = "/opt/blog"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=22, username=user, password=password, timeout=30)


def run_cmd(cmd, timeout=120):
    print(f"  $ {cmd[:120]}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    channel = stdout.channel
    channel.setblocking(False)
    start = t.time()
    while not channel.exit_status_ready():
        if channel.recv_ready():
            data = channel.recv(4096).decode()
            if data:
                print(data, end="")
        if t.time() - start > timeout:
            print(f"\n  TIMEOUT after {timeout}s")
            return 1
        t.sleep(1)
    exit_code = channel.recv_exit_status()
    while channel.recv_ready():
        print(channel.recv(4096).decode(), end="")
    err = stderr.read().decode()
    if err:
        print(f"  ERR: {err}")
    return exit_code


sftp = client.open_sftp()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 上传文件到服务器
print("1. 上传部署文件...")
sftp.put(os.path.join(BASE_DIR, "Dockerfile"), f"{deploy_dir}/Dockerfile")
sftp.put(os.path.join(BASE_DIR, "docker-compose.yml"), f"{deploy_dir}/docker-compose.yml")
sftp.put(os.path.join(BASE_DIR, "nginx.conf"), f"{deploy_dir}/nginx.conf")
sftp.close()

# 配置 BT-Panel Nginx 反向代理
print("2. 配置 BT-Panel Nginx...")
blog_nginx_conf = """upstream blog {
    server 127.0.0.1:8080;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://blog;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
# 写入配置文件
stdin, stdout, stderr = client.exec_command(f"cat > {deploy_dir}/host-nginx.conf << 'NGINX_EOF'\n{blog_nginx_conf}\nNGINX_EOF")
stdout.read()

# 复制到 BT-Panel vhost 目录并测试
run_cmd(f"cp {deploy_dir}/host-nginx.conf /www/server/panel/vhost/nginx/blog.conf")
run_cmd("nginx -t")
run_cmd("nginx -s reload")

# 停止旧容器
print("3. 停止旧容器...")
run_cmd(f"cd {deploy_dir} && docker compose down || true")

# 清理旧镜像
print("4. 清理旧镜像...")
run_cmd("docker rmi $(docker images -q blog-backend 2>/dev/null) 2>/dev/null || true")

# 重新构建
print("5. 构建并启动...")
run_cmd(f"cd {deploy_dir} && docker compose up -d --build", timeout=300)

# 检查状态
print("6. 容器状态...")
run_cmd(f"cd {deploy_dir} && docker compose ps")

# 验证
print("7. 验证服务...")
t.sleep(5)
run_cmd("curl -sf http://localhost/api/health && echo ' Backend OK' || echo ' Backend NOT READY'")
run_cmd("curl -sf -o /dev/null -w 'HTTP %{http_code}' http://localhost/ && echo ' Frontend' || echo ' Frontend NOT READY'")

client.close()
print("\n部署完成！")
