#!/bin/bash

# 板式家具工艺流程管理系统启动脚本

echo "🚀 启动板式家具工艺流程管理系统..."

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
echo "🔍 检查依赖包..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📥 安装依赖包..."
    pip install Flask Flask-SQLAlchemy plotly openpyxl blinker sqlalchemy
fi

# 初始化数据库
echo "🗄️ 初始化数据库..."
python3 init_workflow_data.py

# 启动应用
echo "🌐 启动Web应用..."
echo "📍 访问地址: http://localhost:5000"
echo "🛑 按 Ctrl+C 停止应用"
echo ""

python3 app.py