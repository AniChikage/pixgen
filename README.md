# pixgen后台文档

## 安装
1. 创建python环境，安装依赖
```
conda create --name="pixgen" python=3.10
conda activate pixgen
pip install -r requirements.txt
```

2. 将`.env.template`更名为`.env`，填上相应配置，然后执行
```
source .env
```

3. 启动
```
cd backend
python app.py
```

