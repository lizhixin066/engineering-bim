# ============================================================
# Engineering BIM - Docker 容器
# ============================================================
# 构建: docker build -t engineering-bim .
# 运行: docker run -it --rm -v ./data:/app/data -v ./output:/app/output engineering-bim
# ============================================================

FROM python:3.11-slim

LABEL org.opencontainers.image.title="Engineering BIM"
LABEL org.opencontainers.image.description="大型工程综合技能：识图、算量、CAD转BIM"
LABEL org.opencontainers.image.license="MIT"
LABEL org.opencontainers.image.url="https://github.com/engineering-bim/engineering-bim"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据和输出目录
RUN mkdir -p /app/data /app/output

# 预装配技能文件
RUN python assemble.py

# 默认命令
CMD ["python", "assemble.py"]