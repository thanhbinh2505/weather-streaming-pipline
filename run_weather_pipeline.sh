#!/bin/bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' 

echo -e "${GREEN}==============================================${NC}"
echo -e "${GREEN}   WEATHER DATA STREAMING PIPELINE STARTUP${NC}"
echo -e "${GREEN}==============================================${NC}"

echo -e "${YELLOW}[1/5] Cleaning up old streaming checkpoints...${NC}"
rm -rf ./consumer/checkpoints/*

echo -e "Checkpoints cleared."
echo -e "${YELLOW}[2/5] Stopping any running services...${NC}"

docker compose down --remove-orphans

echo -e "${YELLOW}[3/5] Starting Infrastructure Services...${NC}"
docker compose up -d zookeeper kafka prometheus grafana kafka-exporter
echo -e "Waiting for Kafka to be ready (15s)..."
sleep 15

echo -e "${YELLOW}[4/5] Starting Weather Producer...${NC}"
docker compose up -d --build producer

echo -e "${YELLOW}[5/5] Starting Spark Streaming Consumer...${NC}"
docker compose up -d --build spark-consumer

echo -e "${GREEN}==============================================${NC}"
echo -e "${GREEN}   PIPELINE IS NOW UP AND RUNNING!${NC}"
echo -e "${BLUE}   - Grafana: http://localhost:3000${NC}"
echo -e "${BLUE}   - Prometheus: http://localhost:9090${NC}"
echo -e "${BLUE}   - Kafka Exporter: http://localhost:9308${NC}"
echo -e "${GREEN}==============================================${NC}"

echo -e "${YELLOW}Bạn muốn theo dõi log của dịch vụ nào?${NC}"
echo -e "1) ${BLUE}Producer${NC} (Luồng thu thập API)"
echo -e "2) ${BLUE}Spark Consumer${NC} (Luồng xử lý dữ liệu)"
echo -e "3) ${BLUE}Both${NC} (Cả hai luồng)"
echo -e "4) ${BLUE}Exit${NC}"

read -p "Nhập lựa chọn [1-4]: " choice

case $choice in
1)
    echo -e "${GREEN}Đang mở log Producer...${NC}"
    docker compose logs -f producer
;;
2)
    echo -e "${GREEN}Đang mở log Spark Consumer...${NC}"
    docker compose logs -f spark-consumer
;;
3)
    echo -e "${GREEN}Đang mở log cả 2 dịch vụ...${NC}"
    docker compose logs -f producer spark-consumer
    ;;
4)
    echo -e "${GREEN}Hệ thống đang chạy ngầm.${NC}"
    exit 0
;;
*)
    echo -e "${RED}Lựa chọn không hợp lệ. Hệ thống vẫn đang chạy ngầm.${NC}"
;;
esac