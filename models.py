from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from enum import Enum

db = SQLAlchemy()

# 添加产品表 Product
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    series = db.Column(db.String(50), nullable=False)
    spu = db.Column(db.String(50), nullable=False)
    sku = db.Column(db.String(50), nullable=False)
    file_control = db.Column(db.String(20), nullable=False)  # 已受控/未受控
    standardization = db.Column(db.String(20), nullable=False)  # 已落地/未落地

    def to_dict(self):
        return {
            'id': self.id,
            'series': self.series,
            'spu': self.spu,
            'sku': self.sku,
            'file_control': self.file_control,
            'standardization': self.standardization
        }

class ProcessStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"

class NodeType(Enum):
    START = "start"
    END = "end"
    CUTTING = "cutting"          # 切割
    EDGE_BANDING = "edge_banding"  # 封边
    DRILLING = "drilling"        # 打孔
    ASSEMBLY = "assembly"        # 组装
    PACKAGING = "packaging"      # 包装
    QUALITY_CHECK = "quality_check"  # 质检

# 工艺流程主表
class WorkflowTemplate(db.Model):
    __tablename__ = 'workflow_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    product_series = db.Column(db.String(50))  # 关联产品系列
    version = db.Column(db.String(20), default='1.0')
    status = db.Column(db.Enum(ProcessStatus), default=ProcessStatus.DRAFT)
    
    # 流程配置JSON
    workflow_config = db.Column(db.JSON)  # 存储节点和连接配置
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(50))
    
    # 关联关系
    nodes = db.relationship('WorkflowNode', backref='workflow', lazy=True, cascade='all, delete-orphan')
    cost_calculations = db.relationship('CostCalculation', backref='workflow', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'product_series': self.product_series,
            'version': self.version,
            'status': self.status.value,
            'workflow_config': self.workflow_config,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'nodes_count': len(self.nodes)
        }

# 工艺节点表
class WorkflowNode(db.Model):
    __tablename__ = 'workflow_nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow_templates.id'), nullable=False)
    
    node_id = db.Column(db.String(50), nullable=False)  # 前端生成的唯一ID
    node_type = db.Column(db.Enum(NodeType), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # 节点位置信息
    position_x = db.Column(db.Float, default=0)
    position_y = db.Column(db.Float, default=0)
    
    # 工艺参数JSON
    process_params = db.Column(db.JSON)  # 存储具体工艺参数
    
    # 成本相关
    estimated_time_minutes = db.Column(db.Float, default=0)  # 预估加工时间
    labor_cost_per_hour = db.Column(db.Float, default=0)     # 人工成本/小时
    machine_cost_per_hour = db.Column(db.Float, default=0)   # 设备成本/小时
    
    # 关联关系
    input_connections = db.relationship('NodeConnection', 
                                      foreign_keys='NodeConnection.target_node_id',
                                      backref='target_node', lazy=True)
    output_connections = db.relationship('NodeConnection',
                                       foreign_keys='NodeConnection.source_node_id', 
                                       backref='source_node', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'node_id': self.node_id,
            'workflow_id': self.workflow_id,
            'node_type': self.node_type.value,
            'name': self.name,
            'description': self.description,
            'position': {'x': self.position_x, 'y': self.position_y},
            'process_params': self.process_params,
            'estimated_time_minutes': self.estimated_time_minutes,
            'labor_cost_per_hour': self.labor_cost_per_hour,
            'machine_cost_per_hour': self.machine_cost_per_hour
        }

# 节点连接表
class NodeConnection(db.Model):
    __tablename__ = 'node_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow_templates.id'), nullable=False)
    
    source_node_id = db.Column(db.Integer, db.ForeignKey('workflow_nodes.id'), nullable=False)
    target_node_id = db.Column(db.Integer, db.ForeignKey('workflow_nodes.id'), nullable=False)
    
    connection_id = db.Column(db.String(50), nullable=False)  # 前端生成的连接ID
    
    # 连接条件和规则
    conditions = db.Column(db.JSON)  # 连接条件配置

    def to_dict(self):
        return {
            'id': self.id,
            'connection_id': self.connection_id,
            'workflow_id': self.workflow_id,
            'source_node_id': self.source_node_id,
            'target_node_id': self.target_node_id,
            'conditions': self.conditions
        }

# 材料定义表
class Material(db.Model):
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # 板材/五金/辅料
    
    # 规格信息
    thickness = db.Column(db.Float)  # 厚度(mm)
    width = db.Column(db.Float)      # 宽度(mm)  
    length = db.Column(db.Float)     # 长度(mm)
    
    # 成本信息
    unit_price = db.Column(db.Float, nullable=False)  # 单价
    unit = db.Column(db.String(20), default='张')      # 单位
    supplier = db.Column(db.String(100))
    
    # 损耗率
    waste_rate = db.Column(db.Float, default=0.05)  # 默认5%损耗
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'category': self.category,
            'thickness': self.thickness,
            'width': self.width,
            'length': self.length,
            'unit_price': self.unit_price,
            'unit': self.unit,
            'supplier': self.supplier,
            'waste_rate': self.waste_rate
        }

# 成本计算表
class CostCalculation(db.Model):
    __tablename__ = 'cost_calculations'
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow_templates.id'), nullable=False)
    product_sku = db.Column(db.String(50))  # 关联产品SKU
    
    # 计算基础信息
    quantity = db.Column(db.Integer, default=1)  # 生产数量
    calculation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 成本明细
    material_cost = db.Column(db.Float, default=0)      # 材料成本
    labor_cost = db.Column(db.Float, default=0)         # 人工成本
    machine_cost = db.Column(db.Float, default=0)       # 设备成本
    overhead_cost = db.Column(db.Float, default=0)      # 间接成本
    total_cost = db.Column(db.Float, default=0)         # 总成本
    
    # 详细成本分解JSON
    cost_breakdown = db.Column(db.JSON)  # 详细成本分解数据
    
    # 关联关系
    material_usages = db.relationship('MaterialUsage', backref='cost_calculation', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'product_sku': self.product_sku,
            'quantity': self.quantity,
            'calculation_date': self.calculation_date.isoformat(),
            'material_cost': self.material_cost,
            'labor_cost': self.labor_cost,
            'machine_cost': self.machine_cost,
            'overhead_cost': self.overhead_cost,
            'total_cost': self.total_cost,
            'unit_cost': self.total_cost / self.quantity if self.quantity > 0 else 0,
            'cost_breakdown': self.cost_breakdown
        }

# 材料用量表
class MaterialUsage(db.Model):
    __tablename__ = 'material_usages'
    
    id = db.Column(db.Integer, primary_key=True)
    cost_calculation_id = db.Column(db.Integer, db.ForeignKey('cost_calculations.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    
    # 用量信息
    planned_quantity = db.Column(db.Float, nullable=False)  # 计划用量
    actual_quantity = db.Column(db.Float)                   # 实际用量
    waste_quantity = db.Column(db.Float, default=0)        # 损耗量
    
    # 成本信息
    unit_cost = db.Column(db.Float, nullable=False)        # 单位成本
    total_cost = db.Column(db.Float, nullable=False)       # 总成本
    
    # 关联材料信息
    material = db.relationship('Material', backref='usages')

    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'material_name': self.material.name if self.material else None,
            'planned_quantity': self.planned_quantity,
            'actual_quantity': self.actual_quantity,
            'waste_quantity': self.waste_quantity,
            'unit_cost': self.unit_cost,
            'total_cost': self.total_cost
        }

# 工艺参数模板表
class ProcessTemplate(db.Model):
    __tablename__ = 'process_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    node_type = db.Column(db.Enum(NodeType), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # 默认参数配置
    default_params = db.Column(db.JSON)
    
    # 成本参数
    default_time_minutes = db.Column(db.Float, default=0)
    default_labor_cost_per_hour = db.Column(db.Float, default=0)
    default_machine_cost_per_hour = db.Column(db.Float, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'node_type': self.node_type.value,
            'name': self.name,
            'description': self.description,
            'default_params': self.default_params,
            'default_time_minutes': self.default_time_minutes,
            'default_labor_cost_per_hour': self.default_labor_cost_per_hour,
            'default_machine_cost_per_hour': self.default_machine_cost_per_hour
        }