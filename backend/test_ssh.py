import paramiko
import sys

host = "192.144.154.17"
user = "root"
password = "2313ynkhmymtm==="

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(host, port=22, username=user, password=password, timeout=15)
    print("SSH 连接成功!")
    stdin, stdout, stderr = client.exec_command("uname -a && docker --version && docker compose version")
    out = stdout.read().decode()
    err = stderr.read().decode()
    print(out)
    if err:
        print("STDERR:", err)
except Exception as e:
    print(f"连接失败: {e}")
    sys.exit(1)
finally:
    client.close()
