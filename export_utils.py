import pandas as pd

def export_to_excel(data, filename):
    """
    将数据导出为 Excel 文件。
    data: list of dict 或 pandas.DataFrame
    filename: 导出的文件名
    """
    if isinstance(data, pd.DataFrame):
        df = data
    else:
        df = pd.DataFrame(data)
    df.to_excel(filename, index=False)