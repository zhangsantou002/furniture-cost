# 部署指南

## 📋 系统要求

### 基础环境
- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **内存**: 最少 2GB RAM
- **磁盘空间**: 最少 500MB 可用空间

### 推荐环境
- **Python**: 3.9 或 3.10
- **内存**: 4GB+ RAM
- **磁盘空间**: 2GB+ 可用空间

## 🚀 快速部署

### 方法一：使用启动脚本（推荐）

1. **下载项目**
```bash
git clone https://github.com/你的用户名/furniture-workflow-system.git
cd furniture-workflow-system
```

2. **运行启动脚本**
```bash
# Windows
python startup.py

# macOS/Linux
python3 startup.py
```

启动脚本会自动：
- 检查Python版本
- 安装依赖包
- 初始化数据库
- 启动应用服务器

### 方法二：手动部署

1. **克隆项目**
```bash
git clone https://github.com/你的用户名/furniture-workflow-system.git
cd furniture-workflow-system
```

2. **创建虚拟环境（推荐）**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **初始化数据库**
```bash
python init_workflow_data.py
```

5. **启动应用**
```bash
python app.py
```

## 🌐 访问系统

启动成功后，在浏览器中访问：

- **主页**: http://localhost:5000
- **工艺流程设计器**: http://localhost:5000/workflow-designer
- **成本分析报表**: http://localhost:5000/cost-analysis

## 🔧 生产环境部署

### 使用 Gunicorn（Linux/macOS）

1. **安装 Gunicorn**
```bash
pip install gunicorn
```

2. **创建 WSGI 文件**
创建 `wsgi.py`:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

3. **启动 Gunicorn**
```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

### 使用 Nginx 反向代理

1. **安装 Nginx**
```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

2. **配置 Nginx**
创建配置文件 `/etc/nginx/sites-available/furniture-workflow`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/project/static;
        expires 30d;
    }
}
```

3. **启用配置**
```bash
sudo ln -s /etc/nginx/sites-available/furniture-workflow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 使用 Docker

1. **创建 Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python init_workflow_data.py

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

2. **构建镜像**
```bash
docker build -t furniture-workflow .
```

3. **运行容器**
```bash
docker run -p 5000:5000 furniture-workflow
```

### 使用 Docker Compose

创建 `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
    environment:
      - FLASK_ENV=production
```

运行：
```bash
docker-compose up -d
```

## 🔐 安全配置

### 1. 修改密钥
编辑 `config.py`，修改：
```python
SECRET_KEY = 'your-super-secret-key-here'
```

### 2. 数据库安全
生产环境建议使用 PostgreSQL 或 MySQL：
```python
# config.py
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/furniture_workflow'
```

### 3. HTTPS 配置
使用 Let's Encrypt 获取 SSL 证书：
```bash
sudo certbot --nginx -d your-domain.com
```

## 📊 监控和日志

### 1. 应用日志
配置日志级别和输出文件：
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 系统监控
推荐使用：
- **Prometheus + Grafana**: 系统监控
- **ELK Stack**: 日志分析
- **New Relic/DataDog**: APM监控

## 🔄 备份和恢复

### 数据库备份
```bash
# SQLite 备份
cp workflow.db workflow_backup_$(date +%Y%m%d).db

# PostgreSQL 备份
pg_dump furniture_workflow > backup_$(date +%Y%m%d).sql
```

### 数据恢复
```bash
# SQLite 恢复
cp workflow_backup_20240101.db workflow.db

# PostgreSQL 恢复
psql furniture_workflow < backup_20240101.sql
```

## 🚨 故障排除

### 常见问题

1. **端口被占用**
```bash
# 查找占用端口的进程
netstat -tulpn | grep :5000
# 或者使用其他端口
python app.py --port 8000
```

2. **依赖安装失败**
```bash
# 升级 pip
pip install --upgrade pip
# 使用国内源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

3. **数据库连接错误**
```bash
# 检查数据库文件权限
ls -la *.db
# 重新初始化数据库
rm workflow.db
python init_workflow_data.py
```

4. **内存不足**
```bash
# 增加系统交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 日志查看
```bash
# 查看应用日志
tail -f app.log

# 查看系统日志
journalctl -u your-service-name -f
```

## 📈 性能优化

### 1. 数据库优化
- 创建适当的索引
- 定期清理过期数据
- 使用连接池

### 2. 缓存配置
安装 Redis 并配置缓存：
```python
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
```

### 3. 静态文件优化
- 使用 CDN 加速
- 开启 Gzip 压缩
- 设置合适的缓存头

## 📞 技术支持

遇到问题时：
1. 查看日志文件
2. 检查系统资源使用情况
3. 参考故障排除指南
4. 提交 GitHub Issue

---

🎉 部署完成后，您就可以开始使用板式家具工艺流程管理系统了！