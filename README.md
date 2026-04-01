# NLP Demo - 词义消歧与语义角色标注

## 环境要求
- Python 3.8+
- pip

## 运行方式

### 方式一：一键运行（推荐）
双击 `run.bat` 文件，它会自动：
1. 安装所有依赖
2. 下载必要的模型
3. 启动Web应用

### 方式二：手动安装
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 下载spaCy模型
python -m spacy download en_core_web_sm

# 3. 运行应用
streamlit run nlp_app.py
```

## 功能说明

### 标签页1：词义消歧 (WSD)
- 输入含多义词的句子
- 指定目标多义词
- 使用Lesk算法预测词义
- 使用BERT提取上下文词向量
- 对比两个句子中目标词的语义相似度

### 标签页2：语义角色标注 (SRL)
- 输入句子进行依存句法分析
- 提取谓词、施事者、受事者、地点、时间等语义角色
- 可视化依存句法树

## 首次运行
首次运行时需要下载BERT模型（约440MB），请耐心等待。
