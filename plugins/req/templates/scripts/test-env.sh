#!/bin/bash

# 测试环境启动脚本模板
# 复制到项目 scripts/ 目录并根据需要修改

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
DOCKER_COMPOSE_FILE="docker-compose.test.yml"
BACKEND_PORT=8080
FRONTEND_PORT=3000
MYSQL_PORT=3307
REDIS_PORT=6380

# 日志函数
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 等待端口就绪
wait_for_port() {
    local host=$1
    local port=$2
    local timeout=${3:-30}
    local counter=0

    while ! nc -z "$host" "$port" 2>/dev/null; do
        counter=$((counter + 1))
        if [ $counter -ge $timeout ]; then
            log_error "等待 $host:$port 超时"
            return 1
        fi
        sleep 1
    done
    return 0
}

# 启动 Docker 容器
start_docker() {
    log_info "启动 Docker 容器..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

    log_info "等待 MySQL 就绪..."
    wait_for_port localhost $MYSQL_PORT 60
    log_info "MySQL 已就绪"

    log_info "等待 Redis 就绪..."
    wait_for_port localhost $REDIS_PORT 30
    log_info "Redis 已就绪"
}

# 启动后端服务
start_backend() {
    log_info "启动后端服务..."

    # 检查是否已运行
    if lsof -i:$BACKEND_PORT > /dev/null 2>&1; then
        log_warn "后端服务已在运行 (端口 $BACKEND_PORT)"
        return 0
    fi

    # 设置测试环境变量
    export APP_ENV=test
    export DB_HOST=localhost
    export DB_PORT=$MYSQL_PORT
    export DB_NAME=test_db
    export DB_USER=test_user
    export DB_PASSWORD=test123
    export REDIS_HOST=localhost
    export REDIS_PORT=$REDIS_PORT

    # 启动后端（后台运行）
    go run main.go > /tmp/backend-test.log 2>&1 &
    echo $! > /tmp/backend-test.pid

    log_info "等待后端服务就绪..."
    wait_for_port localhost $BACKEND_PORT 60
    log_info "后端服务已就绪"
}

# 启动前端服务（E2E 测试需要）
start_frontend() {
    log_info "启动前端服务..."

    # 检查是否已运行
    if lsof -i:$FRONTEND_PORT > /dev/null 2>&1; then
        log_warn "前端服务已在运行 (端口 $FRONTEND_PORT)"
        return 0
    fi

    # 进入前端目录并启动
    if [ -d "frontend" ]; then
        cd frontend
        npm run dev > /tmp/frontend-test.log 2>&1 &
        echo $! > /tmp/frontend-test.pid
        cd ..

        log_info "等待前端服务就绪..."
        wait_for_port localhost $FRONTEND_PORT 60
        log_info "前端服务已就绪"
    else
        log_warn "未找到 frontend 目录，跳过前端启动"
    fi
}

# 停止所有服务
stop_all() {
    log_info "停止测试环境..."

    # 停止后端
    if [ -f /tmp/backend-test.pid ]; then
        kill $(cat /tmp/backend-test.pid) 2>/dev/null || true
        rm /tmp/backend-test.pid
        log_info "后端服务已停止"
    fi

    # 停止前端
    if [ -f /tmp/frontend-test.pid ]; then
        kill $(cat /tmp/frontend-test.pid) 2>/dev/null || true
        rm /tmp/frontend-test.pid
        log_info "前端服务已停止"
    fi

    # 停止 Docker
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    log_info "Docker 容器已停止"
}

# 清理测试数据
clean_data() {
    log_info "清理测试数据..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down -v
    log_info "测试数据已清理"
}

# 显示状态
status() {
    echo ""
    echo "=== 测试环境状态 ==="
    echo ""

    # Docker 容器
    echo "Docker 容器："
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps 2>/dev/null || echo "  未启动"
    echo ""

    # 后端服务
    echo -n "后端服务 (端口 $BACKEND_PORT): "
    if lsof -i:$BACKEND_PORT > /dev/null 2>&1; then
        echo -e "${GREEN}运行中${NC}"
    else
        echo -e "${RED}未运行${NC}"
    fi

    # 前端服务
    echo -n "前端服务 (端口 $FRONTEND_PORT): "
    if lsof -i:$FRONTEND_PORT > /dev/null 2>&1; then
        echo -e "${GREEN}运行中${NC}"
    else
        echo -e "${RED}未运行${NC}"
    fi

    echo ""
}

# 使用说明
usage() {
    echo "测试环境管理脚本"
    echo ""
    echo "用法: $0 <command>"
    echo ""
    echo "命令:"
    echo "  start       启动完整测试环境（Docker + 后端 + 前端）"
    echo "  start-api   仅启动 API 测试环境（Docker + 后端）"
    echo "  stop        停止所有服务"
    echo "  clean       停止并清理测试数据"
    echo "  status      查看环境状态"
    echo "  docker      仅启动 Docker 容器"
    echo "  backend     仅启动后端服务"
    echo "  frontend    仅启动前端服务"
    echo ""
}

# 主逻辑
case "${1:-}" in
    start)
        start_docker
        start_backend
        start_frontend
        status
        ;;
    start-api)
        start_docker
        start_backend
        status
        ;;
    stop)
        stop_all
        ;;
    clean)
        stop_all
        clean_data
        ;;
    status)
        status
        ;;
    docker)
        start_docker
        ;;
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    *)
        usage
        exit 1
        ;;
esac
