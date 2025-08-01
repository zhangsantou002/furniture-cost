from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from models import (
    db, WorkflowTemplate, WorkflowNode, NodeConnection, 
    Material, CostCalculation, MaterialUsage, ProcessTemplate,
    NodeType, ProcessStatus
)
import json
from datetime import datetime
from sqlalchemy import func

# 创建蓝图
workflow_bp = Blueprint('workflow', __name__, url_prefix='/api/workflow')

# ============= 工艺流程模板管理 =============

@workflow_bp.route('/templates', methods=['GET'])
def get_workflow_templates():
    """获取工艺流程模板列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        product_series = request.args.get('product_series')
        
        query = WorkflowTemplate.query
        
        if status:
            query = query.filter(WorkflowTemplate.status == ProcessStatus(status))
        if product_series:
            query = query.filter(WorkflowTemplate.product_series == product_series)
            
        templates = query.order_by(WorkflowTemplate.updated_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'templates': [template.to_dict() for template in templates.items],
            'total': templates.total,
            'pages': templates.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/templates', methods=['POST'])
def create_workflow_template():
    """创建工艺流程模板"""
    try:
        data = request.get_json()
        
        template = WorkflowTemplate(
            name=data['name'],
            description=data.get('description'),
            product_series=data.get('product_series'),
            version=data.get('version', '1.0'),
            created_by=data.get('created_by', 'system'),
            workflow_config=data.get('workflow_config', {})
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'message': '工艺流程模板创建成功',
            'template': template.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/templates/<int:template_id>', methods=['GET'])
def get_workflow_template(template_id):
    """获取工艺流程模板详情"""
    try:
        template = WorkflowTemplate.query.get_or_404(template_id)
        
        # 获取关联的节点和连接
        nodes = [node.to_dict() for node in template.nodes]
        connections = []
        
        for node in template.nodes:
            for conn in node.output_connections:
                connections.append(conn.to_dict())
        
        result = template.to_dict()
        result['nodes'] = nodes
        result['connections'] = connections
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/templates/<int:template_id>', methods=['PUT'])
def update_workflow_template(template_id):
    """更新工艺流程模板"""
    try:
        template = WorkflowTemplate.query.get_or_404(template_id)
        data = request.get_json()
        
        # 更新基本信息
        if 'name' in data:
            template.name = data['name']
        if 'description' in data:
            template.description = data['description']
        if 'product_series' in data:
            template.product_series = data['product_series']
        if 'status' in data:
            template.status = ProcessStatus(data['status'])
        if 'workflow_config' in data:
            template.workflow_config = data['workflow_config']
            
        template.updated_at = datetime.utcnow()
        
        # 更新节点信息
        if 'nodes' in data:
            # 删除原有节点
            WorkflowNode.query.filter_by(workflow_id=template_id).delete()
            NodeConnection.query.filter_by(workflow_id=template_id).delete()
            
            # 创建新节点
            for node_data in data['nodes']:
                node = WorkflowNode(
                    workflow_id=template_id,
                    node_id=node_data['node_id'],
                    node_type=NodeType(node_data['node_type']),
                    name=node_data['name'],
                    description=node_data.get('description'),
                    position_x=node_data['position']['x'],
                    position_y=node_data['position']['y'],
                    process_params=node_data.get('process_params', {}),
                    estimated_time_minutes=node_data.get('estimated_time_minutes', 0),
                    labor_cost_per_hour=node_data.get('labor_cost_per_hour', 0),
                    machine_cost_per_hour=node_data.get('machine_cost_per_hour', 0)
                )
                db.session.add(node)
        
        # 更新连接信息
        if 'connections' in data:
            for conn_data in data['connections']:
                # 查找源节点和目标节点的数据库ID
                source_node = WorkflowNode.query.filter_by(
                    workflow_id=template_id, 
                    node_id=conn_data['source_node_id']
                ).first()
                target_node = WorkflowNode.query.filter_by(
                    workflow_id=template_id,
                    node_id=conn_data['target_node_id']
                ).first()
                
                if source_node and target_node:
                    connection = NodeConnection(
                        workflow_id=template_id,
                        source_node_id=source_node.id,
                        target_node_id=target_node.id,
                        connection_id=conn_data['connection_id'],
                        conditions=conn_data.get('conditions', {})
                    )
                    db.session.add(connection)
        
        db.session.commit()
        
        return jsonify({
            'message': '工艺流程模板更新成功',
            'template': template.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============= 工艺节点管理 =============

@workflow_bp.route('/node-types', methods=['GET'])
def get_node_types():
    """获取所有工艺节点类型"""
    node_types = []
    for node_type in NodeType:
        node_types.append({
            'value': node_type.value,
            'name': node_type.name,
            'label': get_node_type_label(node_type)
        })
    
    return jsonify({'node_types': node_types})

def get_node_type_label(node_type):
    """获取节点类型的中文标签"""
    labels = {
        NodeType.START: '开始',
        NodeType.END: '结束',
        NodeType.CUTTING: '切割',
        NodeType.EDGE_BANDING: '封边',
        NodeType.DRILLING: '打孔',
        NodeType.ASSEMBLY: '组装',
        NodeType.PACKAGING: '包装',
        NodeType.QUALITY_CHECK: '质检'
    }
    return labels.get(node_type, node_type.value)

@workflow_bp.route('/process-templates', methods=['GET'])
def get_process_templates():
    """获取工艺参数模板"""
    try:
        node_type = request.args.get('node_type')
        
        query = ProcessTemplate.query
        if node_type:
            query = query.filter(ProcessTemplate.node_type == NodeType(node_type))
            
        templates = query.all()
        
        return jsonify({
            'templates': [template.to_dict() for template in templates]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= 材料管理 =============

@workflow_bp.route('/materials', methods=['GET'])
def get_materials():
    """获取材料列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = Material.query
        
        if category:
            query = query.filter(Material.category == category)
        if search:
            query = query.filter(
                db.or_(
                    Material.name.contains(search),
                    Material.code.contains(search)
                )
            )
            
        materials = query.order_by(Material.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'materials': [material.to_dict() for material in materials.items],
            'total': materials.total,
            'pages': materials.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/materials', methods=['POST'])
def create_material():
    """创建材料"""
    try:
        data = request.get_json()
        
        material = Material(
            code=data['code'],
            name=data['name'],
            category=data.get('category'),
            thickness=data.get('thickness'),
            width=data.get('width'),
            length=data.get('length'),
            unit_price=data['unit_price'],
            unit=data.get('unit', '张'),
            supplier=data.get('supplier'),
            waste_rate=data.get('waste_rate', 0.05)
        )
        
        db.session.add(material)
        db.session.commit()
        
        return jsonify({
            'message': '材料创建成功',
            'material': material.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============= 成本计算 =============

@workflow_bp.route('/cost-calculation', methods=['POST'])
def calculate_cost():
    """计算工艺流程成本"""
    try:
        data = request.get_json()
        workflow_id = data['workflow_id']
        quantity = data.get('quantity', 1)
        product_sku = data.get('product_sku')
        
        # 获取工艺流程模板
        template = WorkflowTemplate.query.get_or_404(workflow_id)
        
        # 计算各项成本
        material_cost = 0
        labor_cost = 0
        machine_cost = 0
        overhead_cost = 0
        
        cost_breakdown = {
            'nodes': [],
            'materials': [],
            'summary': {}
        }
        
        # 计算每个节点的成本
        for node in template.nodes:
            node_labor_cost = (node.estimated_time_minutes / 60) * node.labor_cost_per_hour * quantity
            node_machine_cost = (node.estimated_time_minutes / 60) * node.machine_cost_per_hour * quantity
            
            labor_cost += node_labor_cost
            machine_cost += node_machine_cost
            
            cost_breakdown['nodes'].append({
                'node_id': node.node_id,
                'name': node.name,
                'time_minutes': node.estimated_time_minutes,
                'labor_cost': node_labor_cost,
                'machine_cost': node_machine_cost,
                'total_cost': node_labor_cost + node_machine_cost
            })
        
        # 计算材料成本（从请求数据中获取）
        if 'materials' in data:
            for material_data in data['materials']:
                material = Material.query.get(material_data['material_id'])
                if material:
                    planned_qty = material_data['quantity']
                    waste_qty = planned_qty * material.waste_rate
                    total_qty = planned_qty + waste_qty
                    cost = total_qty * material.unit_price
                    
                    material_cost += cost
                    
                    cost_breakdown['materials'].append({
                        'material_id': material.id,
                        'name': material.name,
                        'planned_quantity': planned_qty,
                        'waste_quantity': waste_qty,
                        'total_quantity': total_qty,
                        'unit_price': material.unit_price,
                        'total_cost': cost
                    })
        
        # 计算间接成本（按总成本的一定比例）
        overhead_rate = data.get('overhead_rate', 0.15)  # 默认15%
        overhead_cost = (material_cost + labor_cost + machine_cost) * overhead_rate
        
        total_cost = material_cost + labor_cost + machine_cost + overhead_cost
        
        cost_breakdown['summary'] = {
            'material_cost': material_cost,
            'labor_cost': labor_cost,
            'machine_cost': machine_cost,
            'overhead_cost': overhead_cost,
            'total_cost': total_cost,
            'unit_cost': total_cost / quantity if quantity > 0 else 0,
            'quantity': quantity
        }
        
        # 保存成本计算结果
        cost_calculation = CostCalculation(
            workflow_id=workflow_id,
            product_sku=product_sku,
            quantity=quantity,
            material_cost=material_cost,
            labor_cost=labor_cost,
            machine_cost=machine_cost,
            overhead_cost=overhead_cost,
            total_cost=total_cost,
            cost_breakdown=cost_breakdown
        )
        
        db.session.add(cost_calculation)
        
        # 保存材料用量记录
        if 'materials' in data:
            for material_data in data['materials']:
                material = Material.query.get(material_data['material_id'])
                if material:
                    planned_qty = material_data['quantity']
                    waste_qty = planned_qty * material.waste_rate
                    total_qty = planned_qty + waste_qty
                    cost = total_qty * material.unit_price
                    
                    usage = MaterialUsage(
                        cost_calculation=cost_calculation,
                        material_id=material.id,
                        planned_quantity=planned_qty,
                        waste_quantity=waste_qty,
                        unit_cost=material.unit_price,
                        total_cost=cost
                    )
                    db.session.add(usage)
        
        db.session.commit()
        
        return jsonify({
            'message': '成本计算完成',
            'calculation_id': cost_calculation.id,
            'cost_breakdown': cost_breakdown
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/cost-calculations', methods=['GET'])
def get_cost_calculations():
    """获取成本计算历史"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        workflow_id = request.args.get('workflow_id', type=int)
        product_sku = request.args.get('product_sku')
        
        query = CostCalculation.query
        
        if workflow_id:
            query = query.filter(CostCalculation.workflow_id == workflow_id)
        if product_sku:
            query = query.filter(CostCalculation.product_sku == product_sku)
            
        calculations = query.order_by(CostCalculation.calculation_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'calculations': [calc.to_dict() for calc in calculations.items],
            'total': calculations.total,
            'pages': calculations.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/cost-calculations/<int:calc_id>', methods=['GET'])
def get_cost_calculation_detail(calc_id):
    """获取成本计算详情"""
    try:
        calculation = CostCalculation.query.get_or_404(calc_id)
        
        result = calculation.to_dict()
        result['material_usages'] = [usage.to_dict() for usage in calculation.material_usages]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= 统计分析 =============

@workflow_bp.route('/statistics/cost-trend', methods=['GET'])
def get_cost_trend():
    """获取成本趋势分析"""
    try:
        days = request.args.get('days', 30, type=int)
        product_sku = request.args.get('product_sku')
        
        # 计算日期范围
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = CostCalculation.query.filter(
            CostCalculation.calculation_date >= start_date,
            CostCalculation.calculation_date <= end_date
        )
        
        if product_sku:
            query = query.filter(CostCalculation.product_sku == product_sku)
        
        calculations = query.order_by(CostCalculation.calculation_date).all()
        
        # 按日期分组统计
        trend_data = {}
        for calc in calculations:
            date_key = calc.calculation_date.strftime('%Y-%m-%d')
            if date_key not in trend_data:
                trend_data[date_key] = {
                    'date': date_key,
                    'total_cost': 0,
                    'material_cost': 0,
                    'labor_cost': 0,
                    'machine_cost': 0,
                    'overhead_cost': 0,
                    'count': 0
                }
            
            trend_data[date_key]['total_cost'] += calc.total_cost
            trend_data[date_key]['material_cost'] += calc.material_cost
            trend_data[date_key]['labor_cost'] += calc.labor_cost
            trend_data[date_key]['machine_cost'] += calc.machine_cost
            trend_data[date_key]['overhead_cost'] += calc.overhead_cost
            trend_data[date_key]['count'] += 1
        
        return jsonify({
            'trend_data': list(trend_data.values())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 错误处理
@workflow_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': '资源未找到'}), 404

@workflow_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': '请求参数错误'}), 400