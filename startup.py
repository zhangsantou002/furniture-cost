#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板式家具工艺流程管理系统 - 启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: Python {sys.version}")
        return False
    print(f"✅ Python版本检查通过: {sys.version}")
    return True

def check_requirements():
    """检查依赖包是否安装"""
    try:
        import flask
        import sqlalchemy
        import plotly
        import pandas
        print("✅ 依赖包检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def install_requirements():
    """安装依赖包"""
    print("📦 正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖包安装失败")
        return False

def init_database():
    """初始化数据库"""
    print("🗄️ 正在初始化数据库...")
    
    # 检查是否已存在数据库
    if os.path.exists("workflow.db"):
        response = input("数据库已存在，是否重新初始化？(y/N): ")
        if response.lower() != 'y':
            print("✅ 使用现有数据库")
            return True
    
    try:
        # 运行数据库初始化脚本
        result = subprocess.run([sys.executable, "init_workflow_data.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 数据库初始化完成")
            return True
        else:
            print(f"❌ 数据库初始化失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 数据库初始化出错: {e}")
        return False

def start_application():
    """启动应用"""
    print("🚀 启动应用服务器...")
    print("=" * 50)
    print("📱 访问地址:")
    print("   主页: http://localhost:5000")
    print("   工艺流程设计器: http://localhost:5000/workflow-designer")
    print("   成本分析报表: http://localhost:5000/cost-analysis")
    print("=" * 50)
    print("按 Ctrl+C 停止服务器")
    print()
    
    try:
        # 启动Flask应用
        subprocess.call([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")

def main():
    """主函数"""
    print("🏠 板式家具工艺流程管理系统")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 检查并安装依赖
    if not check_requirements():
        print("🔧 尝试自动安装依赖包...")
        if not install_requirements():
            print("请手动运行: pip install -r requirements.txt")
            return
    
    # 初始化数据库
    if not init_database():
        print("请检查数据库初始化脚本")
        return
    
    # 启动应用
    start_application()

if __name__ == "__main__":
    main()