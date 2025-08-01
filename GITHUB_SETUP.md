# 📚 GitHub 部署完整指南

## 🎯 目标
将板式家具工艺流程管理系统上传到GitHub，并提供完整的运行指导。

## 📋 准备工作

### 1. 确保已安装必要工具
- [Git](https://git-scm.com/downloads)
- [Python 3.8+](https://www.python.org/downloads/)
- GitHub账户

### 2. 检查文件结构
确保项目包含以下文件：
```
furniture-workflow-system/
├── app.py                      # 主应用文件
├── models.py                   # 数据库模型
├── workflow_api.py             # API接口
├── config.py                   # 配置文件
├── init_workflow_data.py       # 数据初始化
├── startup.py                  # 启动脚本
├── requirements.txt            # 依赖列表
├── README.md                   # 项目说明
├── deploy.md                   # 部署指南
├── .gitignore                  # Git忽略文件
├── templates/                  # HTML模板
│   ├── workflow_designer.html
│   ├── cost_analysis.html
│   └── ...
└── static/                     # 静态资源（如果有）
```

## 🚀 上传到 GitHub

### 步骤1：创建GitHub仓库

1. **登录GitHub**
   - 访问 [github.com](https://github.com)
   - 登录您的账户

2. **创建新仓库**
   - 点击右上角的 "+" 按钮
   - 选择 "New repository"
   - 仓库名称: `furniture-workflow-system`
   - 描述: `板式家具加工工艺流程可视化编排与成本计算系统`
   - 设置为 Public（公开）或 Private（私有）
   - ✅ 勾选 "Add a README file"
   - 点击 "Create repository"

### 步骤2：本地Git初始化

在项目根目录打开终端，执行：

```bash
# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交文件
git commit -m "初始提交：板式家具工艺流程管理系统"

# 添加远程仓库（替换为您的用户名）
git remote add origin https://github.com/您的用户名/furniture-workflow-system.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 步骤3：验证上传

1. 刷新GitHub仓库页面
2. 确认所有文件已上传
3. 检查README.md是否正确显示

## 📖 更新 README.md

确保README.md包含正确的GitHub链接：

```markdown
## 🚀 快速开始

1. **克隆项目**
```bash
git clone https://github.com/您的用户名/furniture-workflow-system.git
cd furniture-workflow-system
```

2. **运行启动脚本**
```bash
python startup.py
```
```

## 🏃‍♂️ 运行系统指南

### 方法一：一键启动（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/您的用户名/furniture-workflow-system.git
cd furniture-workflow-system

# 2. 运行启动脚本
python startup.py
```

启动脚本将自动完成：
- ✅ 检查Python版本
- ✅ 安装所需依赖
- ✅ 初始化数据库
- ✅ 启动Web服务器

### 方法二：手动运行

```bash
# 1. 克隆项目
git clone https://github.com/您的用户名/furniture-workflow-system.git
cd furniture-workflow-system

# 2. 创建虚拟环境（推荐）
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python init_workflow_data.py

# 5. 启动应用
python app.py
```

### 访问系统

启动成功后，打开浏览器访问：

- 🏠 **主页**: http://localhost:5000
- 🎨 **工艺流程设计器**: http://localhost:5000/workflow-designer  
- 📊 **成本分析报表**: http://localhost:5000/cost-analysis

## 🐛 常见问题解决

### 1. Python版本问题
```bash
# 检查Python版本
python --version

# 如果版本低于3.8，请升级Python
```

### 2. 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 3. 端口占用问题
```bash
# 查看端口占用
netstat -ano | findstr 5000

# 修改端口（在app.py最后一行）
app.run(debug=True, port=8000)
```

### 4. 权限问题（Linux/macOS）
```bash
# 给启动脚本执行权限
chmod +x startup.py

# 使用python3运行
python3 startup.py
```

## 📱 系统功能演示

### 工艺流程设计器
1. 从左侧工具栏拖拽工艺节点到画布
2. 连接节点形成工艺流程
3. 选择节点配置参数和成本
4. 实时预览总成本
5. 保存工艺流程模板

### 成本分析报表
1. 查看成本趋势图表
2. 分析成本结构占比
3. 对比不同工艺节点成本
4. 导出分析报告

## 📞 获取帮助

遇到问题时：

1. **查看文档**
   - [README.md](README.md) - 项目介绍
   - [deploy.md](deploy.md) - 部署指南

2. **检查日志**
   ```bash
   # 查看终端输出的错误信息
   python app.py
   ```

3. **提交Issue**
   - 访问 GitHub 仓库
   - 点击 "Issues" 标签
   - 点击 "New issue"
   - 详细描述问题

4. **联系开发者**
   - Email: [your-email@example.com]
   - GitHub: [@您的用户名]

## 🎉 成功运行检查清单

- [ ] 成功克隆项目到本地
- [ ] Python 3.8+ 已安装
- [ ] 依赖包安装成功
- [ ] 数据库初始化完成
- [ ] Web服务器启动成功
- [ ] 能够访问主页 (http://localhost:5000)
- [ ] 工艺流程设计器可以正常使用
- [ ] 成本分析报表显示正常

## 🔄 更新系统

获取最新版本：

```bash
# 进入项目目录
cd furniture-workflow-system

# 拉取最新代码
git pull origin main

# 更新依赖（如果有变化）
pip install -r requirements.txt

# 重新启动系统
python startup.py
```

---

🎊 **恭喜！您已经成功部署了板式家具工艺流程管理系统！**

现在可以开始创建您的第一个工艺流程了！ 🚀