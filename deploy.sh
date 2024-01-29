#!/bin/bash

# Docker Compose でコンテナをバックグラウンドで起動
docker-compose up -d

# コンテナが終了するまで待機
while docker ps | grep "pachi-app-1"; do
  echo "pachi-app container is still running"
  sleep 5
done

# コンテナが停止したら Docker Compose でコンテナを停止
docker-compose down