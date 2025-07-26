#!/bin/bash

# Путь к вашему проекту, например текущая директория
PROJECT_DIR=$(pwd)

# Имя виртуального окружения
VENV_DIR="$PROJECT_DIR/.venv"

# Имя systemd-сервиса
SERVICE_NAME="anonymouschatbot"

echo "1. Активируем виртуальное окружение и устанавливаем зависимости..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Виртуальное окружение не найдено по пути $VENV_DIR, создаём..."
    python3 -m venv "$VENV_DIR"
fi

# Активируем и устанавливаем зависимости
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

echo "2. Создаем systemd сервис..."

SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Telegram Aiogram Bot Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/python $PROJECT_DIR/src/main.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "3. Перезагружаем systemd, активируем и запускаем сервис..."

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "Сервис $SERVICE_NAME запущен и включён на автозапуск."
echo "Для проверки статуса используйте: sudo systemctl status $SERVICE_NAME"
