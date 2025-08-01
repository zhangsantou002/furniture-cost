from flask import Flask, render_template, request, jsonify, redirect, url_for
# 删除 from flask_sqlalchemy import SQLAlchemy，改为导入 models 里的 db
from models import db as workflow_db, Product
import plotly.graph_objs as go
import plotly.utils
import json
from collections import Counter

# 导入工艺流程相关模块
try:
    from workflow_api import workflow_bp
    WORKFLOW_ENABLED = True
except ImportError:
    WORKFLOW_ENABLED = False
    print("⚠️ 工艺流程模块未找到，将以基础模式运行")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product_status.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 用 workflow_db.init_app(app) 替代 db = SQLAlchemy(app)
workflow_db.init_app(app)

# 注册工艺流程API蓝图
if WORKFLOW_ENABLED:
    app.register_blueprint(workflow_bp)

# 创建数据库表
with app.app_context():
    workflow_db.create_all()
    # 初始化工艺流程数据库（不要再调用 workflow_db.init_app(app)）
    # 其它初始化代码...

    # 初始化示例数据
    if Product.query.count() == 0:
        sample_data = [
            ('Zina', 'HSR170', 'HSR170W01', '未受控', '已落地'),
            ('Zina', 'HSR170', 'HSR170B01', '已受控', '未落地'),
        ]

        for data in sample_data:
            product = Product(
                series=data[0],
                spu=data[1],
                sku=data[2],
                file_control=data[3],
                standardization=data[4]
            )
            workflow_db.session.add(product)
        workflow_db.session.commit()


def generate_charts():
    """生成多维度图表"""
    products = Product.query.all()
    product_data = [p.to_dict() for p in products]

    charts = {}

    # 1. 系列分布饼图
    series_counts = Counter(p['series'] for p in product_data)
    charts['series_pie'] = json.dumps({
        'data': [{
            'values': list(series_counts.values()),
            'labels': list(series_counts.keys()),
            'type': 'pie',
            'name': '系列分布'
        }],
        'layout': {
            'title': '产品系列分布',
            'height': 400
        }
    }, cls=plotly.utils.PlotlyJSONEncoder)

    # 2. 文件受控状态柱状图
    file_control_counts = Counter(p['file_control'] for p in product_data)
    charts['file_control_bar'] = json.dumps({
        'data': [{
            'x': list(file_control_counts.keys()),
            'y': list(file_control_counts.values()),
            'type': 'bar',
            'marker': {'color': ['#ff6b6b', '#4ecdc4']}
        }],
        'layout': {
            'title': '文件受控状态分布',
            'xaxis': {'title': '受控状态'},
            'yaxis': {'title': '产品数量'},
            'height': 400
        }
    }, cls=plotly.utils.PlotlyJSONEncoder)

    # 3. 标准化落地状态柱状图
    std_counts = Counter(p['standardization'] for p in product_data)
    charts['standardization_bar'] = json.dumps({
        'data': [{
            'x': list(std_counts.keys()),
            'y': list(std_counts.values()),
            'type': 'bar',
            'marker': {'color': ['#45b7d1', '#f9ca24']}
        }],
        'layout': {
            'title': '标准化落地状态分布',
            'xaxis': {'title': '落地状态'},
            'yaxis': {'title': '产品数量'},
            'height': 400
        }
    }, cls=plotly.utils.PlotlyJSONEncoder)

    return charts


# 路由
@app.route('/')
def dashboard():
    """主看板页面"""
    charts = generate_charts()
    products = Product.query.all()

    # 统计数据
    total_products = len(products)
    controlled_products = len([p for p in products if p.file_control == '已受控'])
    standardized_products = len([p for p in products if p.standardization == '已落地'])
    
    # 获取工艺流程模板数量
    try:
        from models import WorkflowTemplate
        workflow_templates = WorkflowTemplate.query.count()
    except:
        workflow_templates = 0

    return render_template('dashboard.html', 
                         charts=charts, 
                         total_products=total_products,
                         controlled_products=controlled_products,
                         standardized_products=standardized_products,
                         workflow_templates=workflow_templates)


@app.route('/products')
def products():
    """产品列表页面"""
    products = Product.query.all()
    return render_template('products.html', products=products)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    """添加产品"""
    if request.method == 'POST':
        product = Product(
            series=request.form['series'],
            spu=request.form['spu'],
            sku=request.form['sku'],
            file_control=request.form['file_control'],
            standardization=request.form['standardization']
        )
        workflow_db.session.add(product)
        workflow_db.session.commit()
        return redirect(url_for('products'))

    return render_template('add_product.html')


@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    """编辑产品"""
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.series = request.form['series']
        product.spu = request.form['spu']
        product.sku = request.form['sku']
        product.file_control = request.form['file_control']
        product.standardization = request.form['standardization']
        workflow_db.session.commit()
        return redirect(url_for('products'))

    return render_template('edit_product.html', product=product)


@app.route('/delete_product/<int:id>')
def delete_product(id):
    """删除产品"""
    product = Product.query.get_or_404(id)
    workflow_db.session.delete(product)
    workflow_db.session.commit()
    return redirect(url_for('products'))


@app.route('/api/products')
def api_products():
    """API接口获取产品数据"""
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])


from flask import send_file
from export_utils import export_to_excel
from datetime import datetime


@app.route('/export')
def export_products():
    """导出产品数据"""
    products = Product.query.all()
    excel_file = export_to_excel(products)

    filename = f"产品数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return send_file(
        excel_file,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/api/stats')
def api_stats():
    """获取统计数据API"""
    products = Product.query.all()

    stats = {
        'total': len(products),
        'by_series': {},
        'by_file_control': {},
        'by_standardization': {},
        'combinations': {}
    }

    for product in products:
        # 按系列统计
        stats['by_series'][product.series] = stats['by_series'].get(product.series, 0) + 1

        # 按文件受控状态统计
        stats['by_file_control'][product.file_control] = stats['by_file_control'].get(product.file_control, 0) + 1

        # 按标准化状态统计
        stats['by_standardization'][product.standardization] = stats['by_standardization'].get(product.standardization,
                                                                                               0) + 1

        # 按状态组合统计
        combo = f"{product.file_control}-{product.standardization}"
        stats['combinations'][combo] = stats['combinations'].get(combo, 0) + 1

    return jsonify(stats)


@app.route('/batch_update', methods=['POST'])
def batch_update():
    """批量更新产品状态"""
    data = request.get_json()
    product_ids = data.get('product_ids', [])
    updates = data.get('updates', {})

    try:
        for product_id in product_ids:
            product = Product.query.get(product_id)
            if product:
                if 'file_control' in updates:
                    product.file_control = updates['file_control']
                if 'standardization' in updates:
                    product.standardization = updates['standardization']

        workflow_db.session.commit()
        return jsonify({'success': True, 'message': f'成功更新 {len(product_ids)} 个产品'})
    except Exception as e:
        workflow_db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/workflow-designer')
def workflow_designer():
    """工艺流程设计器页面"""
    return render_template('workflow_designer.html')

@app.route('/cost-analysis')
def cost_analysis():
    """成本分析报表页面"""
    return render_template('cost_analysis.html')


if __name__ == '__main__':
    app.run(debug=True)

# 在app.py中添加以下导入和路由 (继续)


