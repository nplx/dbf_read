import streamlit as st
import pandas as pd
import io
from pathlib import Path
import dbf
import base64
import os


# 标题
st.title('DBF文件转换 v1.0 | *.dbf → *.csv')


# 定义允许的文件类型
ALLOWED_EXTENSIONS = {"dbf"}


# 上传器
uploaded_file = st.file_uploader("选择要转换的文件", type=ALLOWED_EXTENSIONS)


# 保存上传文件
if uploaded_file is not None:
    data_load_state = st.text('Uploading data...')
    file_contents = uploaded_file.getvalue()
    # 将字节流转换为文件对象
    file_obj = io.BytesIO(file_contents)
    # print(uploaded_file.name)
    # 将文件保存到本地文件系统:
    with open(Path.joinpath(Path().resolve(), 'uploads', uploaded_file.name), 'wb+') as f:
        f.write(file_contents)
    # 获取文件路径
    file_path = Path(f.name).resolve()
    data_load_state.text("上传完成 ✔️")
    st.toast('已上传', icon='✅')


# 转换方法
def convert_data(data_file=None):
    # data_file是需要上传的dbf文件绝对路径名，是str
    if data_file:
        db = dbf.Table(filename=data_file)
        db.open(dbf.READ_ONLY)
        # print(type(db))
        # print(len(db))
        # 输出转换后的csv文件至converted文件夹
        file_name_stem = Path(data_file).stem
        file_name_suffix = Path(data_file).suffix
        dbf.export(db, file_name_stem+'.csv', format='csv', header=True, dialect=file_name_suffix, encoding='utf-8')
        db.close()
        csv_path = Path(file_name_stem + '.csv')
        if Path.exists(csv_path):
            Path(csv_path).replace('converted/'+csv_path.name)
            with open('converted/'+csv_path.name, 'r') as f:
                data = pd.read_csv(f, nrows=10000)
            st.write(data)
        else:
            st.toast('出错了', icon='❎')
            st.write("出错了 ❌")
            data = None
    else:
        raise '需要输入DBF文件'
    return csv_path


# 对dbf进行转换
try:
    with open(file_path, 'r') as f:
        data_process_state = st.text('Processing data...')
        # 调用转换，传入完整路径文件名
        csv_path = convert_data(f.name)
        data_process_state.text("转换完成 ✔️")
        st.toast('已转换', icon='✅')
except NameError:
    csv_path = None
    print('没有文件')
except dbf.exceptions.NotFoundError:
    st.toast('出错了', icon='❎')
    st.write("无法读取数据表 ❌")


# 下载文件
# print(csv_path)
if csv_path is not None:
    def get_binary_file_downloader_html(bin_file, file_label='File'):
        with open(bin_file, 'rb') as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">点击下载 {file_label}</a>'
        return href
    file_path = './converted/' + csv_path.name
    file_label = 'CSV文件'
    st.markdown(get_binary_file_downloader_html(file_path, file_label),
            unsafe_allow_html=True)
else:
    pass