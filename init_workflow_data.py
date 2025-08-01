#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板式家具工艺流程和成本计算系统 - 初始化数据脚本
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask
from models import (
    db, WorkflowTemplate, WorkflowNode, NodeConnection,
    Material, ProcessTemplate, NodeType, ProcessStatus
)
import json
from datetime import datetime

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workflow.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def init_materials():
    """初始化材料数据"""
    materials_data = [
        # 板材类
        {
            'code': 'E0-18MM-WH',
            'name': 'E0级白色三聚氰胺板',
            'category': '板材',
            'thickness': 18.0,
            'width': 1220.0,
            'length': 2440.0,
            'unit_price': 280.0,
            'unit': '张',
            'supplier': '大亚人造板',
            'waste_rate': 0.08
        },
        {
            'code': 'E0-18MM-BK',
            'name': 'E0级黑色三聚氰胺板',
            'category': '板材',
            'thickness': 18.0,
            'width': 1220.0,
            'length': 2440.0,
            'unit_price': 290.0,
            'unit': '张',
            'supplier': '大亚人造板',
            'waste_rate': 0.08
        },
        {
            'code': 'BACK-3MM',
            'name': '3mm密度板背板',
            'category': '板材',
            'thickness': 3.0,
            'width': 1220.0,
            'length': 2440.0,
            'unit_price': 45.0,
            'unit': '张',
            'supplier': '丰林集团',
            'waste_rate': 0.05
        },
        
        # 五金类
        {
            'code': 'HINGE-35',
            'name': '35杯铰链',
            'category': '五金',
            'unit_price': 12.5,
            'unit': '个',
            'supplier': '海蒂诗',
            'waste_rate': 0.02
        },
        {
            'code': 'SLIDE-350',
            'name': '350mm三节滑轨',
            'category': '五金',
            'unit_price': 25.0,
            'unit': '付',
            'supplier': '海蒂诗',
            'waste_rate': 0.02
        },
        {
            'code': 'HANDLE-128',
            'name': '128mm拉手',
            'category': '五金',
            'unit_price': 8.0,
            'unit': '个',
            'supplier': '雅洁五金',
            'waste_rate': 0.01
        },
        
        # 辅料类
        {
            'code': 'EDGE-1MM-WH',
            'name': '1mm白色PVC封边条',
            'category': '辅料',
            'thickness': 1.0,
            'width': 22.0,
            'unit_price': 3.5,
            'unit': '米',
            'supplier': '瑞好封边',
            'waste_rate': 0.10
        },
        {
            'code': 'EDGE-1MM-BK',
            'name': '1mm黑色PVC封边条',
            'category': '辅料',
            'thickness': 1.0,
            'width': 22.0,
            'unit_price': 3.8,
            'unit': '米',
            'supplier': '瑞好封边',
            'waste_rate': 0.10
        },
        {
            'code': 'GLUE-EVA',
            'name': 'EVA热熔胶',
            'category': '辅料',
            'unit_price': 18.0,
            'unit': '公斤',
            'supplier': '汉高胶粘剂',
            'waste_rate': 0.05
        },
        {
            'code': 'SCREW-4X16',
            'name': '4x16mm自攻螺丝',
            'category': '辅料',
            'unit_price': 0.08,
            'unit': '个',
            'supplier': '东明紧固件',
            'waste_rate': 0.03
        }
    ]
    
    for material_data in materials_data:
        if not Material.query.filter_by(code=material_data['code']).first():
            material = Material(**material_data)
            db.session.add(material)
    
    print(f"初始化了 {len(materials_data)} 个材料记录")

def init_process_templates():
    """初始化工艺参数模板"""
    templates_data = [
        {
            'node_type': NodeType.CUTTING,
            'name': '板材切割标准工艺',
            'description': '使用推台锯进行板材精确切割',
            'default_params': {
                'saw_type': '推台锯',
                'blade_size': '300mm',
                'feed_speed': '8m/min',
                'safety_margin': '2mm'
            },
            'default_time_minutes': 15.0,
            'default_labor_cost_per_hour': 45.0,
            'default_machine_cost_per_hour': 25.0
        },
        {
            'node_type': NodeType.EDGE_BANDING,
            'name': '自动封边工艺',
            'description': '使用自动封边机进行PVC封边',
            'default_params': {
                'machine_type': '自动封边机',
                'edge_material': 'PVC',
                'edge_thickness': '1mm',
                'temperature': '200°C'
            },
            'default_time_minutes': 8.0,
            'default_labor_cost_per_hour': 40.0,
            'default_machine_cost_per_hour': 30.0
        },
        {
            'node_type': NodeType.DRILLING,
            'name': '数控打孔工艺',
            'description': '使用数控钻床进行精确打孔',
            'default_params': {
                'drill_type': '数控钻床',
                'hole_diameter': '8mm',
                'drill_speed': '3000rpm',
                'feed_rate': '500mm/min'
            },
            'default_time_minutes': 12.0,
            'default_labor_cost_per_hour': 50.0,
            'default_machine_cost_per_hour': 35.0
        },
        {
            'node_type': NodeType.ASSEMBLY,
            'name': '标准组装工艺',
            'description': '按照图纸进行部件组装',
            'default_params': {
                'assembly_method': '手工+气动工具',
                'quality_check': '每步检查',
                'torque_setting': '8Nm'
            },
            'default_time_minutes': 45.0,
            'default_labor_cost_per_hour': 42.0,
            'default_machine_cost_per_hour': 8.0
        },
        {
            'node_type': NodeType.QUALITY_CHECK,
            'name': '质量检验工艺',
            'description': '全面质量检查和测试',
            'default_params': {
                'check_items': ['尺寸', '外观', '功能', '安全'],
                'check_standard': 'GB/T 3324-2017',
                'sampling_rate': '100%'
            },
            'default_time_minutes': 20.0,
            'default_labor_cost_per_hour': 38.0,
            'default_machine_cost_per_hour': 5.0
        },
        {
            'node_type': NodeType.PACKAGING,
            'name': '标准包装工艺',
            'description': '按照包装标准进行包装',
            'default_params': {
                'packaging_type': '纸箱+泡沫',
                'protection_level': 'A级',
                'labeling': '完整标签'
            },
            'default_time_minutes': 25.0,
            'default_labor_cost_per_hour': 35.0,
            'default_machine_cost_per_hour': 3.0
        }
    ]
    
    for template_data in templates_data:
        if not ProcessTemplate.query.filter_by(
            node_type=template_data['node_type'], 
            name=template_data['name']
        ).first():
            template = ProcessTemplate(**template_data)
            db.session.add(template)
    
    print(f"初始化了 {len(templates_data)} 个工艺参数模板")

def init_workflow_templates():
    """初始化工艺流程模板"""
    
    # 创建标准衣柜加工流程
    wardrobe_workflow = WorkflowTemplate(
        name='标准衣柜加工流程',
        description='适用于标准规格衣柜的完整加工流程',
        product_series='HSR170',
        version='1.0',
        status=ProcessStatus.ACTIVE,
        created_by='系统管理员',
        workflow_config={
            'viewport': {'x': 0, 'y': 0, 'zoom': 1},
            'grid_size': 20,
            'snap_to_grid': True
        }
    )
    db.session.add(wardrobe_workflow)
    db.session.flush()  # 获取ID
    
    # 创建流程节点
    nodes_data = [
        {
            'node_id': 'start_001',
            'node_type': NodeType.START,
            'name': '开始',
            'description': '衣柜加工流程开始',
            'position_x': 100.0,
            'position_y': 100.0,
            'process_params': {},
            'estimated_time_minutes': 0.0,
            'labor_cost_per_hour': 0.0,
            'machine_cost_per_hour': 0.0
        },
        {
            'node_id': 'cut_001',
            'node_type': NodeType.CUTTING,
            'name': '板材切割',
            'description': '将原材料板材按照图纸尺寸进行切割',
            'position_x': 300.0,
            'position_y': 100.0,
            'process_params': {
                'material_list': ['侧板', '顶底板', '背板', '搁板'],
                'cut_precision': '±0.5mm',
                'edge_quality': 'A级'
            },
            'estimated_time_minutes': 30.0,
            'labor_cost_per_hour': 45.0,
            'machine_cost_per_hour': 25.0
        },
        {
            'node_id': 'edge_001',
            'node_type': NodeType.EDGE_BANDING,
            'name': '封边处理',
            'description': '对切割好的板材进行封边处理',
            'position_x': 500.0,
            'position_y': 100.0,
            'process_params': {
                'edge_sides': ['前边', '两侧边'],
                'edge_material': 'PVC 1mm',
                'edge_color': '同色系'
            },
            'estimated_time_minutes': 20.0,
            'labor_cost_per_hour': 40.0,
            'machine_cost_per_hour': 30.0
        },
        {
            'node_id': 'drill_001',
            'node_type': NodeType.DRILLING,
            'name': '钻孔加工',
            'description': '按照装配要求进行钻孔',
            'position_x': 700.0,
            'position_y': 100.0,
            'process_params': {
                'hole_types': ['32系列孔', '铰链孔', '拉手孔'],
                'hole_accuracy': '±0.1mm',
                'hole_quality': '无崩边'
            },
            'estimated_time_minutes': 25.0,
            'labor_cost_per_hour': 50.0,
            'machine_cost_per_hour': 35.0
        },
        {
            'node_id': 'assy_001',
            'node_type': NodeType.ASSEMBLY,
            'name': '部件组装',
            'description': '按照装配图进行组装',
            'position_x': 500.0,
            'position_y': 300.0,
            'process_params': {
                'assembly_order': ['柜体', '门板', '五金'],
                'tools_required': ['气动螺丝刀', '安装夹具'],
                'quality_points': ['垂直度', '对角线', '开启顺畅']
            },
            'estimated_time_minutes': 60.0,
            'labor_cost_per_hour': 42.0,
            'machine_cost_per_hour': 8.0
        },
        {
            'node_id': 'qc_001',
            'node_type': NodeType.QUALITY_CHECK,
            'name': '质量检验',
            'description': '全面质量检查',
            'position_x': 300.0,
            'position_y': 300.0,
            'process_params': {
                'check_list': ['外观检查', '尺寸检查', '功能检查', '安全检查'],
                'check_standard': 'GB/T 3324-2017',
                'defect_handling': '不合格返工'
            },
            'estimated_time_minutes': 15.0,
            'labor_cost_per_hour': 38.0,
            'machine_cost_per_hour': 5.0
        },
        {
            'node_id': 'pack_001',
            'node_type': NodeType.PACKAGING,
            'name': '包装入库',
            'description': '产品包装和入库',
            'position_x': 100.0,
            'position_y': 300.0,
            'process_params': {
                'packaging_method': '拆装包装',
                'protection_materials': ['珍珠棉', '纸护角', '塑料薄膜'],
                'package_marking': ['产品信息', '装配说明', '注意事项']
            },
            'estimated_time_minutes': 30.0,
            'labor_cost_per_hour': 35.0,
            'machine_cost_per_hour': 3.0
        },
        {
            'node_id': 'end_001',
            'node_type': NodeType.END,
            'name': '结束',
            'description': '衣柜加工流程结束',
            'position_x': 100.0,
            'position_y': 500.0,
            'process_params': {},
            'estimated_time_minutes': 0.0,
            'labor_cost_per_hour': 0.0,
            'machine_cost_per_hour': 0.0
        }
    ]
    
    # 创建节点
    for node_data in nodes_data:
        node = WorkflowNode(
            workflow_id=wardrobe_workflow.id,
            **node_data
        )
        db.session.add(node)
    
    db.session.flush()  # 确保节点已保存并获得ID
    
    # 创建节点连接
    connections_data = [
        ('start_001', 'cut_001'),
        ('cut_001', 'edge_001'),
        ('edge_001', 'drill_001'),
        ('drill_001', 'assy_001'),
        ('assy_001', 'qc_001'),
        ('qc_001', 'pack_001'),
        ('pack_001', 'end_001')
    ]
    
    for source_node_id, target_node_id in connections_data:
        source_node = WorkflowNode.query.filter_by(
            workflow_id=wardrobe_workflow.id,
            node_id=source_node_id
        ).first()
        target_node = WorkflowNode.query.filter_by(
            workflow_id=wardrobe_workflow.id,
            node_id=target_node_id
        ).first()
        
        if source_node and target_node:
            connection = NodeConnection(
                workflow_id=wardrobe_workflow.id,
                source_node_id=source_node.id,
                target_node_id=target_node.id,
                connection_id=f"conn_{source_node_id}_{target_node_id}",
                conditions={}
            )
            db.session.add(connection)
    
    print(f"创建了工艺流程模板: {wardrobe_workflow.name}")
    print(f"包含 {len(nodes_data)} 个节点和 {len(connections_data)} 个连接")

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        print("开始初始化工艺流程和成本计算系统数据...")
        
        # 初始化基础数据
        init_materials()
        init_process_templates()
        init_workflow_templates()
        
        # 提交事务
        try:
            db.session.commit()
            print("[OK] 所有数据初始化完成！")
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] 数据初始化失败: {e}")
            return False
        
        # 显示统计信息
        print("\n[STAT] 数据统计:")
        print(f"材料数量: {Material.query.count()}")
        print(f"工艺模板数量: {ProcessTemplate.query.count()}")
        print(f"工艺流程数量: {WorkflowTemplate.query.count()}")
        print(f"工艺节点数量: {WorkflowNode.query.count()}")
        print(f"节点连接数量: {NodeConnection.query.count()}")
        
        return True

if __name__ == '__main__':
    main()