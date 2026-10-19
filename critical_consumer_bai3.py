#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BÀI THỰC HÀNH 3 - CHƯƠNG TRÌNH 3: CRITICAL CONSUMER
Lắng nghe 'critical_queue' được bind vào 'iot_alert_exchange' với routing_key='critical'.
"""

import sys
import argparse
from datetime import datetime
import pika

# Đảm bảo in tiếng Việt chuẩn trên Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==============================================================================
# CẤU HÌNH MẶC ĐỊNH
# ==============================================================================
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 5672
DEFAULT_USER = "guest"
DEFAULT_PASS = "guest"
EXCHANGE_NAME = "iot_alert_exchange"
QUEUE_NAME = "critical_queue"
ROUTING_KEY = "critical"


def parse_arguments():
    """Hỗ trợ cấu hình qua dòng lệnh."""
    parser = argparse.ArgumentParser(
        description="BTH3 - Critical Consumer: Nhan canh bao muc CRITICAL tu RabbitMQ."
    )
    parser.add_argument(
        "--host", default=DEFAULT_HOST, help="Dia chi RabbitMQ broker (mac dinh: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help="Cong RabbitMQ broker (mac dinh: 5672)"
    )
    parser.add_argument(
        "--user", default=DEFAULT_USER, help="Username RabbitMQ (mac dinh: guest)"
    )
    parser.add_argument(
        "--password", default=DEFAULT_PASS, help="Password RabbitMQ (mac dinh: guest)"
    )
    parser.add_argument(
        "--url", default=None, help="AMQP URL (vi du: amqp://user:pass@host:5672/)"
    )
    return parser.parse_args()


def get_connection(args):
    """Tạo kết nối tới RabbitMQ broker."""
    try:
        if args.url:
            parameters = pika.URLParameters(args.url)
        else:
            credentials = pika.PlainCredentials(args.user, args.password)
            parameters = pika.ConnectionParameters(
                host=args.host,
                port=args.port,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=2
            )
        return pika.BlockingConnection(parameters)
    except pika.exceptions.AMQPConnectionError as err:
        print(f"\n[!] LỖI KẾT NỐI BROKER: {err}")
        print(f"Không thể kết nối tới '{args.host}:{args.port}'. Vui lòng kiểm tra RabbitMQ Server.\n")
        sys.exit(1)


def callback(ch, method, properties, body):
    """Xử lý khi nhận được message cảnh báo CRITICAL."""
    message = body.decode("utf-8")
    now_str = datetime.now().strftime("%H:%M:%S")

    # In ra đúng theo mẫu định dạng của đề bài
    print(f"[{QUEUE_NAME}] Da nhan: {message}")
    print(f"                (Thoi gian: {now_str} | Routing Key: {method.routing_key})")

    # Xác nhận đã nhận tin nhắn
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    args = parse_arguments()

    print("=" * 60)
    print("      BTH3 - CRITICAL CONSUMER")
    print("=" * 60)
    print(f"[*] Đang kết nối tới broker: {args.host}:{args.port}...")

    connection = get_connection(args)
    channel = connection.channel()

    # 1. Đảm bảo Direct Exchange tồn tại
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="direct",
        durable=True
    )

    # 2. Khai báo queue 'critical_queue'
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # 3. Bind queue với exchange thông qua routing_key='critical'
    channel.queue_bind(
        exchange=EXCHANGE_NAME,
        queue=QUEUE_NAME,
        routing_key=ROUTING_KEY
    )

    print(f"[+] Đã bind queue '{QUEUE_NAME}' vào exchange '{EXCHANGE_NAME}'")
    print(f"[+] Routing Key: '{ROUTING_KEY}'")
    print(f"[*] Đang lắng nghe các cảnh báo CRITICAL. Nhấn Ctrl+C để dừng.\n")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=False
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n[!] Đang dừng consumer (Ctrl+C)...")
        channel.stop_consuming()
    finally:
        connection.close()
        print("[*] Đã đóng kết nối RabbitMQ an toàn.\n")


if __name__ == "__main__":
    main()
