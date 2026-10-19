#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BÀI THỰC HÀNH 3 - CHƯƠNG TRÌNH MỞ RỘNG: ALL ALERTS CONSUMER & LOGGER
Lắng nghe tất cả các mức cảnh báo (info, warning, critical) và ghi log ra file.
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
QUEUE_NAME = "all_alerts_queue"
ROUTING_KEYS = ["info", "warning", "critical"]
LOG_FILE = "alerts.log"


def parse_arguments():
    """Hỗ trợ cấu hình qua dòng lệnh."""
    parser = argparse.ArgumentParser(
        description="BTH3 - Mo rong: Nhan tat ca canh bao va ghi log ra file."
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
    parser.add_argument(
        "--logfile", default=LOG_FILE, help="Duong dan file ghi log (mac dinh: alerts.log)"
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
        sys.exit(1)


def make_callback(logfile):
    """Tạo callback có kèm file log."""
    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{method.routing_key.upper()}] {message}"

        # In ra màn hình console
        print(f"[{QUEUE_NAME}] Da nhan [{method.routing_key}]: {message}")

        # Ghi log ra file alerts.log
        try:
            with open(logfile, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except IOError as e:
            print(f"[!] Lỗi ghi file log: {e}")

        ch.basic_ack(delivery_tag=method.delivery_tag)
    return callback


def main():
    args = parse_arguments()

    print("=" * 60)
    print("      BTH3 - ALL ALERTS CONSUMER & LOGGER (MỞ RỘNG)")
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

    # 2. Khai báo queue 'all_alerts_queue'
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # 3. Bind queue với cả 3 routing keys: info, warning, critical
    for r_key in ROUTING_KEYS:
        channel.queue_bind(
            exchange=EXCHANGE_NAME,
            queue=QUEUE_NAME,
            routing_key=r_key
        )
        print(f"[+] Đã bind routing_key: '{r_key}'")

    print(f"[+] File log: {args.logfile}")
    print(f"[*] Đang lắng nghe tất cả các cảnh báo. Nhấn Ctrl+C để dừng.\n")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=make_callback(args.logfile),
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
