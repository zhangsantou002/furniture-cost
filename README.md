# 板式家具加工工艺流程可视化编排与成本计算系统

一个专为板式家具制造企业设计的工艺流程可视化编排和成本计算管理系统。

## 🏗️ 系统架构

### 技术栈

**后端技术**
- **框架**: Flask 2.3.3
- **数据库**: SQLAlchemy ORM + SQLite
- **API**: RESTful API设计
- **数据可视化**: Plotly.js

**前端技术**
- **流程编排**: React Flow - 拖拽式工艺流程设计
- **图表展示**: Chart.js - 成本分析图表
- **UI框架**: Bootstrap 5 + Font Awesome图标
- **样式**: 现代化响应式CSS设计

## 📊 核心功能

### 1. 工艺流程可视化编排
- 🎨 **拖拽式设计器**: 直观的可视化工艺流程编排界面
- 🔧 **工艺节点管理**: 支持切割、封边、打孔、组装、质检、包装等工艺节点
- ⚙️ **参数配置**: 每个节点支持详细的工艺参数设置
- 📏 **时间与成本**: 预估加工时间和成本配置
- 🔗 **流程连接**: 灵活的节点连接和条件设置
- 📋 **模板管理**: 工艺流程模板保存和复用

### 2. 成本计算引擎
- 💰 **多维度成本计算**:
  - 材料成本（板材、五金、辅料）
  - 人工成本（按工时计算）
  - 设备成本（设备使用成本）
  - 间接成本（管理费用、能耗等）
- 📊 **实时成本分析**: 流程设计时实时预览成本
- 🗄️ **材料库管理**: 完整的材料信息和价格管理
- 📈 **损耗率计算**: 自动计算材料损耗成本

### 3. 数据分析与报表
- 📉 **成本趋势分析**: 多时间维度的成本趋势图表
- 🥧 **成本结构分析**: 成本组成饼图和占比分析
- 📊 **工艺节点对比**: 不同工艺节点的成本对比
- 📋 **详细报表**: 完整的成本计算记录和导出功能
- 🔍 **数据钻取**: 支持数据筛选和详细查看

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <project-url>
cd furniture-workflow-system
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **初始化数据库**
```bash
python init_workflow_data.py
```

4. **启动应用**
```bash
python app.py
```

5. **访问系统**
- 主页: http://localhost:5000
- 工艺流程设计器: http://localhost:5000/workflow-designer
- 成本分析报表: http://localhost:5000/cost-analysis

## 🗂️ 项目结构

```
furniture-workflow-system/
│
├── app.py                      # Flask主应用
├── models.py                   # 数据库模型定义
├── workflow_api.py             # 工艺流程API接口
├── config.py                   # 配置文件
├── init_workflow_data.py       # 数据初始化脚本
├── requirements.txt            # 项目依赖
├── README.md                   # 项目文档
│
├── templates/                  # HTML模板
│   ├── base.html              # 基础模板
│   ├── workflow_designer.html  # 工艺流程设计器
│   ├── cost_analysis.html      # 成本分析报表
│   └── ...                    # 其他页面模板
│
├── static/                     # 静态资源
│   ├── css/                   # 样式文件
│   ├── js/                    # JavaScript文件
│   └── images/                # 图片资源
│
└── instance/                   # 实例配置和数据库文件
    └── *.db                   # SQLite数据库文件
```

## 💾 数据库设计

### 核心数据表

#### 工艺流程管理
- `workflow_templates` - 工艺流程模板主表
- `workflow_nodes` - 工艺节点表
- `node_connections` - 节点连接关系表
- `process_templates` - 工艺参数模板表

#### 材料与成本
- `materials` - 材料定义表
- `cost_calculations` - 成本计算记录表
- `material_usages` - 材料用量记录表

#### 产品管理
- `products` - 产品信息表（继承原有系统）

## 🔧 API接口文档

### 工艺流程管理
- `GET /api/workflow/templates` - 获取工艺流程模板列表
- `POST /api/workflow/templates` - 创建新的工艺流程模板
- `GET /api/workflow/templates/{id}` - 获取工艺流程模板详情
- `PUT /api/workflow/templates/{id}` - 更新工艺流程模板

### 材料管理
- `GET /api/workflow/materials` - 获取材料列表
- `POST /api/workflow/materials` - 创建新材料
- `GET /api/workflow/node-types` - 获取工艺节点类型

### 成本计算
- `POST /api/workflow/cost-calculation` - 执行成本计算
- `GET /api/workflow/cost-calculations` - 获取成本计算历史
- `GET /api/workflow/cost-calculations/{id}` - 获取成本计算详情

### 统计分析
- `GET /api/workflow/statistics/cost-trend` - 获取成本趋势数据

## 🎯 使用场景

### 1. 工艺设计师
- 使用可视化设计器创建和编辑工艺流程
- 配置各工艺节点的参数和成本信息
- 预览和优化工艺流程的成本结构

### 2. 成本管理员
- 维护材料库和价格信息
- 分析产品成本构成和趋势
- 生成成本报表和分析报告

### 3. 生产管理员
- 查看标准化的工艺流程
- 跟踪生产成本和效率
- 进行工艺流程的持续改进

## 🔮 功能特色

### 工艺流程设计器亮点
- **直观的拖拽操作**: 从节点面板拖拽工艺节点到画布
- **实时属性编辑**: 选择节点即可在右侧面板编辑属性
- **智能连接**: 自动识别节点连接点，生成流程路径
- **成本实时预览**: 设计过程中实时显示成本估算
- **模板保存**: 一键保存工艺流程模板供后续使用

### 成本分析报表亮点
- **多维度图表**: 趋势图、饼图、柱状图等多种可视化
- **交互式筛选**: 支持时间范围、产品类型等多维筛选
- **数据钻取**: 点击图表可查看详细数据
- **响应式设计**: 完美适配不同屏幕尺寸
- **导出功能**: 支持Excel和PDF格式导出

## 📈 系统优势

1. **专业性**: 专门针对板式家具制造工艺设计
2. **易用性**: 直观的拖拽式界面，学习成本低
3. **灵活性**: 支持自定义工艺节点和参数配置
4. **准确性**: 精确的成本计算模型和损耗率处理
5. **可扩展性**: 模块化设计，便于功能扩展
6. **数据驱动**: 基于实际数据的成本分析和优化建议

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱: [your-email@example.com]
- 项目地址: [project-url]

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！