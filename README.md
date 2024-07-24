
# AI trading copilot 



### 业务意图和操作逻辑
- 读取 data/intention_scripts.xlsx文件

### 模型文件地址

- 大模型部分直接调用OpenAI接口
- 向量模型部分使用本地模型，如不存在将自动下载，配置见configs/project.yaml
  - Embedding模型
  - Rerank模型

### 启动方式
- Entrypoint为根目录的 python app.py
- docker: sh build_local_run.sh
- 后端访问的线上服务地址为 http://localhost:8867/api/v1/in_trading

### API接口

- 与后端交互接口 /api/v1/in_trading
- 接口文档： http://localhost:8867/docs

