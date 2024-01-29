
# Docker Compose でコンテナをバックグラウンドで起動
docker-compose up -d

# コンテナが起動中かどうかをポーリングして待機
while (docker ps | Out-String -Stream | Select-String pachi-app-1) {
  $test = docker ps | Out-String -Stream | Select-String pachi-app-1
  Write-Output $test
  Start-Sleep -Seconds 3
}

# コンテナが停止したら Docker Compose でコンテナを停止
docker-compose down