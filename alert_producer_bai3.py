#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BÀI THỰC HÀNH 3 - CHƯƠNG TRÌNH 1: ALERT PRODUCER
Gửi các cảnh báo IoT qua direct exchange 'iot_alert_exchange' với routing key (info, warning, critical).
"""

import sys
import time
import argparse
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
EXCHANGE_TYPE = "direct"

# Danh sách thông điệp mẫu cho từng mức cảnh báo
SAMPLE_ALERTS = [
    ("info", "He thong khoi dong thanh cong va hoat dong on dinh"),
    ("warning", "Nhiet do phong may vuot nguong warning"),
    ("critical", "Cam bien kho lanh mat ket noi critical")
]


def parse_arguments():
    """Hỗ trợ cấu hình qua dòng lệnh."""
    parser = argparse.ArgumentParser(
        description="BTH3 - Alert Producer: Phat canh bao qua Direct Exchange 'iot_alert_exchange'."
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
        "--severity", choices=["info", "warning", "critical"], default=None,
        help="Muc canh bao can gui (info, warning, critical)"
    )
    parser.add_argument(
        "--message", default=None, help="Noi dung canh bao can gui"
    )
    parser.add_argument(
        "--loop", action="store_true", help="Gui lien tuc cac canh bao mau theo chu ky"
    )
    parser.add_argument(
        "--interval", type=float, default=2.0, help="Khoang thoi gian nghi giua cac lan gui (giay)"
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


def publish_alert(channel, severity, message):
    """Phát một message tới direct exchange với routing key tương ứng."""
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=severity,
        body=message.encode("utf-8"),
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent
        )
    )
    print(f" [x] Đã phát [{severity.upper()}] (routing_key='{severity}'): \"{message}\"")


def main():
    args = parse_arguments()

    print("=" * 60)
    print("      BTH3 - ALERT PRODUCER (DIRECT EXCHANGE)")
    print("=" * 60)
    print(f"[*] Đang kết nối tới broker: {args.host}:{args.port}...")

    connection = get_connection(args)
    channel = connection.channel()

    # Khai báo direct exchange tên: iot_alert_exchange
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type=EXCHANGE_TYPE,
        durable=True
    )
    print(f"[+] Đã tạo / kiểm tra Direct Exchange: '{EXCHANGE_NAME}'\n")

    try:
        if args.severity and args.message:
            # Gửi 1 message chỉ định từ dòng lệnh
            publish_alert(channel, args.severity, args.message)

        elif args.loop:
            # Gửi liên tục các cảnh báo mẫu theo chu kỳ
            print("[*] Chế độ lặp tuần hoàn (Nhấn Ctrl+C để dừng)...")
            step = 0
            while True:
                severity, message = SAMPLE_ALERTS[step % len(SAMPLE_ALERTS)]
                publish_alert(channel, severity, message)
                step += 1
                time.sleep(args.interval)

        else:
            # Mặc định: Gửi cả 3 mức cảnh báo (info, warning, critical) để kiểm thử
            print("[*] Đang gửi bộ 3 cảnh báo mẫu (info, warning, critical) để kiểm thử:")
            for severity, message in SAMPLE_ALERTS:
                publish_alert(channel, severity, message)
                time.sleep(0.5)

            print("\n[+] Đã gửi xong bộ kiểm thử.")
            print("Gợi ý lệnh:")
            print("  - Gửi 1 mức cụ thể: python alert_producer_bai3.py --severity warning --message \"Nhiet do cao\"")
            print("  - Chạy liên tục:    python alert_producer_bai3.py --loop")

    except KeyboardInterrupt:
        print("\n[!] Đã dừng producer (Ctrl+C).")
    finally:
        connection.close()
        print("[*] Đã đóng kết nối RabbitMQ an toàn.\n")


if __name__ == "__main__":
    main()
