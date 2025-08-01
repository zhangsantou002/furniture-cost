import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFileDialog, QTableWidget, QTableWidgetItem,
                             QComboBox, QTextEdit, QFormLayout,
                             QGroupBox, QInputDialog, QCheckBox, QLabel, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
import pandas as pd


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle('PyQt5 App Demo')  # Set window title

        mainLayout = QHBoxLayout()

        # Excel loading area
        excelLayout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.updateComponentSelection)
        excelLayout.addWidget(self.table)

        self.btnLoad = QPushButton('Load Excel')
        self.btnLoad.clicked.connect(self.loadExcel)
        self.btnLoad.setIcon(QIcon('load_icon.png'))  # Set button icon
        excelLayout.addWidget(self.btnLoad)

        # Add a matplotlib figure to the layout
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        excelLayout.addWidget(self.canvas)

        mainLayout.addLayout(excelLayout)

        self.cityInput = QComboBox()
        self.cityInput.addItems(
            ['东莞', '惠州', '杭州', '苏州', '宁波', '无锡', '南京', '青岛', '保定', '佛山', '沈阳', '长春', '柳州',
             '合肥'])  # 添加你需要的城市
        excelLayout.addWidget(self.cityInput)

        # Functionality buttons area
        buttonLayout = QVBoxLayout()
        self.processGroup = QGroupBox('Process Path')
        processLayout = QFormLayout()

        self.componentTypeInput = QComboBox()
        self.componentTypeInput.addItems(['板式', '五金'])
        self.componentTypeInput.currentIndexChanged.connect(self.updateProcessPathOptions)
        processLayout.addRow('Component Type:', self.componentTypeInput)

        self.componentInput = QComboBox()
        self.componentInput.currentIndexChanged.connect(self.updateProcessList)
        processLayout.addRow('Component:', self.componentInput)

        self.processPathLayout = QGridLayout()
        processLayout.addRow(self.processPathLayout)

        self.btnAddProcess = QPushButton('Add Process Path')
        self.btnAddProcess.clicked.connect(self.addProcessPath)
        self.btnAddProcess.setIcon(QIcon('add_icon.png'))  # Set button icon
        processLayout.addRow(self.btnAddProcess)

        self.processGroup.setLayout(processLayout)
        buttonLayout.addWidget(self.processGroup)

        self.btnSave = QPushButton('Save Excel')
        self.btnSave.clicked.connect(self.saveExcel)
        self.btnSave.setIcon(QIcon('save_icon.png'))  # Set button icon
        buttonLayout.addWidget(self.btnSave)

        self.processList = QListWidget()
        buttonLayout.addWidget(self.processList)

        self.btnDeleteProcess = QPushButton('Delete Selected Process Path')
        self.btnDeleteProcess.clicked.connect(self.deleteProcessPath)
        self.btnDeleteProcess.setIcon(QIcon('delete_icon.png'))  # Set button icon
        buttonLayout.addWidget(self.btnDeleteProcess)

        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

        self.processData = {}
        self.processFormulas = {
            '电子锯开料': '(a+b)*2*5.76/1000*c/15*d',
            'CNC开料': 'parameters/50+15*d',
            '排钻': 'parameters*20*d',
            '数控排钻': 'parameters*3+15*d',
            '锣槽': 'parameters/180+12*d',
            '铣型': 'parameters*d',
            '机器封边': '(a+b)*2/1000*28.8*d',
            '人工封边': 'parameters/1000*40*d',
            '空心板': '864*d if (a+b) > 1600 else 720*d if (a+b) > 1100 else 576*d if (a+b) > 700 else 432*d',
            '假厚板': '345*d if (a+b) > 1600 else 288*d if (a+b) > 1100 else 230*d if (a+b) > 700 else 172*d',
            '栅格门': '445*d if (a+b) > 1600 else 388*d if (a+b) > 1100 else 330*d if (a+b) > 700 else 272*d',
            '装饰件': 'parameters*d',
            '芯板门': '167.8*d if (a+b) > 1600 else 152.8*d if (a+b) > 1100 else 137.8*d if (a+b) > 700 else 122.8*d',
            '其他拼装': 'parameters*d',
            '导轨': 'parameters*d',
            '脚钉': 'parameters*10*d',
            '002公扣': 'parameters*15*d',
            '002母扣': 'parameters*10*d',
            '螺丝': 'parameters*8*d',
            '其他预装': 'parameters*d',
            'logo': '12*d',
            '字母标': '6*d',
            '清洁': 'a*b/1000*20*d',
            '修边': '(a+b)*2/1000*28.8*d',
            '修色': '(a+b)*2/1000*28.8*d',
            # ... 添加其他工艺路径的公式 ...
        }
        self.workPrices = {
            '东莞': 0.006694444,
            '惠州': 0.00625,
            '杭州': 0.008138889,
            '苏州': 0.008083333,
            '宁波': 0.008027778,
            '无锡': 0.008,
            '南京': 0.007916667,
            '青岛': 0.007277778,
            '保定': 0.006861111,
            '佛山': 0.006777778,
            '沈阳': 0.006722222,
            '长春': 0.006694444,
            '柳州': 0.006416667,
            '合肥': 0.006138889,
        }

    def loadExcel(self):
        try:
            fileName, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'Excel files (*.xlsx)')
            if fileName:
                self.df = pd.read_excel(fileName)
                self.df['City'] = self.cityInput.currentText()  # 使用用户选择的城市
                self.table.setRowCount(self.df.shape[0])
                self.table.setColumnCount(self.df.shape[1])
                self.table.setHorizontalHeaderLabels(self.df.columns)
                for i in range(self.df.shape[0]):
                    for j in range(self.df.shape[1]):
                        self.table.setItem(i, j, QTableWidgetItem(str(self.df.iat[i, j])))
                self.componentInput.addItems(self.df['Component'].unique())
                self.updateProcessPathOptions()
                self.updateBarChart()
        except Exception as e:
            print('Error:', e)

    def updateProcessPathOptions(self):
        # Clear the layout first
        for i in reversed(range(self.processPathLayout.count())):
            self.processPathLayout.itemAt(i).widget().setParent(None)

        if self.componentTypeInput.currentText() == '板式':
            processPaths = {
                '开料': ['CNC开料', '电子锯开料'],
                '封边': ['机器封边', '人工封边'],
                '打孔': ['排钻', '数控排钻'],
                '锣铣': ['锣槽', '铣型'],
                '拼装': ['空心板', '假厚板', '栅格门', '芯板门', '其他拼装'],
                '预装': ['螺丝', '导轨', '装饰件', '脚钉', '002公扣', '002母扣', '其他预装'],
                '贴标': ['logo', '字母标'],
                '辅助工艺': ['清洁', '修边', '修色'],  # 添加其他工艺路径...
            }
        else:
            processPaths = {
                '开料': ['激光开料', '切管机开料', '冲压开料'],
                '缩管': ['激光开料', '切管机开料', '冲压开料'],
                '弯管': ['u型弯管', '导角弯管', '滚圆圈管'],  # 添加其他工艺路径...
            }

        row = 0
        for processPath, subPaths in processPaths.items():
            group = QGroupBox(processPath)
            group.setStyleSheet("""
                QGroupBox {
                    font-size: 18px;
                    font-weight: bold;
                    margin-top: 30px;
                    border: 1px solid gray;
                    border-radius: 9px;
                    background-color: rgb(220, 220, 220);
                }

                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                }
            """)
            layout = QGridLayout()
            layout.setSpacing(10)  # Set spacing between widgets
            for i, subPath in enumerate(subPaths):
                checkbox = QCheckBox(subPath)
                checkbox.setStyleSheet("QCheckBox { color: black; font-size: 12px; }")  # Set QCheckBox style
                layout.addWidget(checkbox, i // 4, i % 4)  # 4 columns
            group.setLayout(layout)
            self.processPathLayout.addWidget(group, row, 0)
            row += 1

    def addProcessPath(self):
        try:
            if not hasattr(self, 'df'):
                print("No Excel file loaded")
                return

            if 'Component' not in self.df.columns:
                print("No 'Component' column in the Excel file")
                return

            selectedItems = self.table.selectedItems()
            if not selectedItems:
                print("No row selected")
                return

            selectedRow = selectedItems[0].row()
            component = self.df.iat[selectedRow, self.df.columns.get_loc('Component')]
            if component not in self.processData:
                self.processData[component] = []

            # Define the list of process paths that require parameters
            processPathsRequireParameters = [
                'CNC开料',
                '排钻',
                '数控排钻',
                '锣槽',
                '铣型',
                '人工封边',
                '其他拼装',
                '导轨',
                '脚钉',
                '002公扣',
                '002母扣',
                '螺丝',
                '其他预装'
            ]

            for i in range(self.processPathLayout.count()):
                group = self.processPathLayout.itemAt(i).widget()
                layout = group.layout()
                for j in range(layout.count()):
                    widget = layout.itemAt(j).widget()
                    if isinstance(widget, QCheckBox) and widget.isChecked():
                        processPath = widget.text()
                        processParameters = None
                        # Check if the current process path requires parameters
                        if processPath in processPathsRequireParameters:
                            processParameters, ok = QInputDialog.getText(self, 'Input Dialog',
                                                                         f'Enter parameters for {processPath}:')  # 弹出输入框
                            if not ok:  # 如果用户点击了取消按钮
                                continue
                        else:
                            processParameters = 0  # Set default parameters to 0 for process paths that do not require parameters

                        # 计算工时
                        formula = self.processFormulas[processPath]
                        a = self.df.iat[selectedRow, self.df.columns.get_loc('a')]
                        b = self.df.iat[selectedRow, self.df.columns.get_loc('b')]
                        c = self.df.iat[selectedRow, self.df.columns.get_loc('c')]
                        d = self.df.iat[selectedRow, self.df.columns.get_loc('d')]
                        parameters = float(processParameters)
                        time = eval(formula.format(a=a, b=b, c=c, d=d, parameters=parameters))

                        # 计算成本
                        city = self.df.iat[selectedRow, self.df.columns.get_loc('City')]
                        if city in self.workPrices:
                            cost = time * self.workPrices[city]
                        else:
                            print(f"Warning: No work price for city '{city}', using default price 0.007")
                            cost = time * 0.007  # 使用默认工价

                        self.processData[component].append([processPath, processParameters, time, cost])
            self.updateProcessList()
            self.updateBarChart()
        except Exception as e:
            print('Error:', e)

    def saveExcel(self):
        fileName, _ = QFileDialog.getSaveFileName(self, 'Save file', '', 'Excel files (*.xlsx)')
        if fileName:
            for component, data in self.processData.items():
                for i, (processPath, processParameters, time, cost) in enumerate(data):
                    self.df.loc[self.df['Component'] == component, f'Process Path {i + 1}'] = processPath
                    self.df.loc[self.df['Component'] == component, f'Process Parameters {i + 1}'] = processParameters
                    self.df.loc[self.df['Component'] == component, f'Process Time {i + 1}'] = time
                    self.df.loc[self.df['Component'] == component, f'Process Cost {i + 1}'] = cost
            self.df.to_excel(fileName, index=False)

    def deleteProcessPath(self):
        currentItem = self.processList.currentItem()
        if currentItem:
            parts = currentItem.text().split(': ', 1)
            if len(parts) < 2:
                print(f"Unexpected item text format: '{itemText}'")
                return

            component = parts[0]
            processPath, processParameters, time, cost = parts[1].rsplit(' - ', 3)  # Change here
            if component in self.processData:
                for i, data in enumerate(self.processData[component]):
                    if data[0] == processPath and str(data[1]) == processParameters:  # Compare as strings
                        del self.processData[component][i]
                        break
                self.updateProcessList()  # 更新列表控件
                if not self.processData[component]:  # 如果组件没有工艺路径，从字典中删除该组件
                    del self.processData[component]

                # Update self.df
                for i in range(1, len(self.df.columns)):
                    if self.df.columns[i].startswith('Process Path') or self.df.columns[i].startswith(
                            'Process Parameters') or self.df.columns[i].startswith('Process Time') or self.df.columns[
                        i].startswith('Process Cost'):
                        self.df.loc[self.df['Component'] == component, self.df.columns[i]] = None
            else:
                print(f"No such process path '{processPath}' for component '{component}'")
        else:
            print("No process path selected")
        self.updateBarChart()

    def updateComponentSelection(self):  # 新增：更新部件选择
        selectedItems = self.table.selectedItems()
        if selectedItems:
            selectedRow = selectedItems[0].row()
            if 'Component' in self.df.columns and selectedRow < len(self.df):
                component = self.df.iat[selectedRow, self.df.columns.get_loc('Component')]
                index = self.componentInput.findText(component)
                if index >= 0:
                    self.componentInput.setCurrentIndex(index)
            else:
                print(f"Error: Invalid row {selectedRow} or 'Component' column not in DataFrame")

    def updateProcessList(self):
        self.processList.clear()
        component = self.componentInput.currentText()
        if component in self.processData:
            for processPath, processParameters, time, cost in self.processData[component]:
                self.processList.addItem(
                    f"{component}: {processPath} - Parameters: {processParameters} - Time: {time} - Cost: {cost}")

    def updateBarChart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        component = self.componentInput.currentText()
        if component in self.processData:
            processPaths = [data[0] for data in self.processData[component]]
            costs = [data[3] for data in self.processData[component]]
            bars = ax.bar(processPaths, costs, color='blue')

            # Add data labels to the bars
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), va='bottom', ha='center')

            ax.set_title('Process Cost for Each Process Path')
            ax.set_xlabel('Process Path')
            ax.set_ylabel('Cost')

            # Add cumulative cost curve
            cumulative_costs = np.cumsum(costs)
            line, = ax.plot([bar.get_x() + bar.get_width() / 2 for bar in bars], cumulative_costs, color='red',
                            marker='o')

            # Add data labels to the line
            for i, txt in enumerate(cumulative_costs):
                ax.text(line.get_xdata()[i], line.get_ydata()[i], round(txt, 2), va='bottom', ha='center')

        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    demo = AppDemo()
    demo.show()

    sys.exit(app.exec_())