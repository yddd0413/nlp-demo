# NLP Demo - 部署指南

## 方案一：Streamlit Cloud（推荐，免费）

### 步骤：

1. **创建GitHub仓库**
   - 登录 https://github.com
   - 创建新仓库，如 `nlp-demo`

2. **上传代码到GitHub**
   ```bash
   cd D:\opencodes\hw4
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的用户名/nlp-demo.git
   git push -u origin main
   ```

3. **部署到Streamlit Cloud**
   - 访问 https://share.streamlit.io
   - 用GitHub账号登录
   - 点击 "New app"
   - 选择你的仓库和 `nlp_app.py`
   - 点击 "Deploy"

4. **获得公开链接**
   - 部署完成后获得类似 `https://xxx-yyy.streamlit.app` 的链接
   - 任何人都可以访问！

---

## 方案二：Hugging Face Spaces（免费）

1. 访问 https://huggingface.co/new-space
2. 选择 SDK: Streamlit
3. 上传文件
4. 自动获得公开链接

---

## 方案三：本地暴露（临时测试）

使用 ngrok 让本地服务可外网访问：

```bash
# 安装ngrok
pip install pyngrok

# 运行应用
streamlit run nlp_app.py

# 另开终端，运行ngrok
ngrok http 8501
```

会获得一个临时外网链接（有效期有限）

---

## 注意事项

1. **模型下载**：首次部署会自动下载BERT模型（约440MB），需要等待几分钟
2. **内存要求**：建议选择至少8GB内存的部署环境
3. **免费限制**：Streamlit Cloud免费版有限制，足够演示使用
