# 构建阶段
FROM node:16-alpine AS build-stage
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 配置 npm 淘宝镜像源（可选，加快国内下载速度）
RUN npm config set registry https://registry.npmmirror.com

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:stable-alpine AS production-stage

# 复制构建产物到 Nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制 Nginx 配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
