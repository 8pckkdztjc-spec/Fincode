# frontend/Dockerfile
# ================================
# FinCode Frontend Dockerfile
# 用于开发环境的 Vite + React 前端
# ================================

FROM node:20-alpine

# 设置工作目录
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 暴露 Vite 开发服务器端口
EXPOSE 5173

# 开发模式启动命令
# --host 参数允许外部访问（Docker 容器外部）
CMD ["npm", "run", "dev", "--", "--host"]
