#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BÀI THỰC HÀNH 3 (CoAP) - BÀI 2 - CHƯƠNG TRÌNH 1: SENSOR COAP SERVER
Mô phỏng cảm biến nhiệt độ & độ ẩm (sensor01).
Cung cấp tài nguyên: coap://localhost:5683/iot/lab/sensor01/data
- Tự động cập nhật dữ liệu cảm biến sau mỗi 3 giây.
- Hỗ trợ phương thức GET trả về dữ liệu JSON với Content-Format: application/json (50).
"""

import sys
import json
import random
import argparse
import asyncio
from datetime import datetime
import aiocoap
import aiocoap.resource as resource

# Đảm bảo in tiếng Việt chuẩn trên Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class SensorDataResource(resource.Resource):
    """
    Tài nguyên cảm biến tại đường dẫn: /iot/lab/sensor01/data
    Cập nhật dữ liệu đo định kỳ và phản hồi các yêu cầu GET.
    """
    def __init__(self, device_id="sensor01"):
        super().__init__()
        self.device_id = device_id
        self.temperature = 28.5
        self.humidity = 65.2
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_sensor_values(self):
        """Mô phỏng đo lường: sinh ngẫu nhiên nhiệt độ (22.0 - 39.0°C) và độ ẩm (32.0 - 78.0%)."""
        self.temperature = round(random.uniform(22.0, 39.0), 1)
        self.humidity = round(random.uniform(32.0, 78.0), 1)
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_data_dict(self):
        return {
            "device_id": self.device_id,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "timestamp": self.timestamp
        }

    async def render_get(self, request):
        """Xử lý yêu cầu GET: trả về dữ liệu JSON mới nhất."""
        data_dict = self.get_data_dict()
        payload_bytes = json.dumps(data_dict, indent=2).encode("utf-8")
        
        client_info = request.remote.hostinfo if request.remote else "unknown"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] GET /iot/lab/{self.device_id}/data tu {client_info} -> Temp: {self.temperature}C, Hum: {self.humidity}%")

        # 50 = application/json trong chuẩn CoAP Content-Format (RFC 7252)
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=payload_bytes,
            content_format=50
        )


async def sensor_update_task(sensor_resource, interval=3.0):
    """Tác vụ nền tự động cập nhật dữ liệu cảm biến sau mỗi `interval` giây."""
    try:
        while True:
            await asyncio.sleep(interval)
            sensor_resource.update_sensor_values()
            data = sensor_resource.get_data_dict()
            print(f"[Sensor Update] {data['device_id']}: {data['temperature']}°C | {data['humidity']}% (Time: {data['timestamp']})")
    except asyncio.CancelledError:
        pass


async def main():
    parser = argparse.ArgumentParser(
        description="BTH3 - Bai 2: Sensor CoAP Server (URI: /iot/lab/sensor01/data)"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Địa chỉ IP lắng nghe (mặc định: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cổng UDP lắng nghe (mặc định: 5683)")
    parser.add_argument("--device", default="sensor01", help="Mã thiết bị cảm biến (mặc định: sensor01)")
    parser.add_argument("--interval", type=float, default=3.0, help="Chu kỳ cập nhật dữ liệu (giây, mặc định: 3.0)")
    args = parser.parse_args()

    root = resource.Site()
    sensor_res = SensorDataResource(device_id=args.device)

    # Đường dẫn tài nguyên: /iot/lab/sensor01/data
    root.add_resource(["iot", "lab", args.device, "data"], sensor_res)

    server = await aiocoap.Context.create_server_context(root, bind=(args.host, args.port))

    print("=" * 60)
    print("      BTH3 - BAI 2: SENSOR COAP SERVER")
    print("      Sinh vien: Nguyen Phu Binh | MSV: B23DCCN083")
    print("=" * 60)
    print(f"[*] CoAP Sensor Server started on {args.host}:{args.port}")
    print(f"[*] Tài nguyên: coap://{args.host}:{args.port}/iot/lab/{args.device}/data")
    print(f"[*] Chu kỳ cập nhật cảm biến: {args.interval}s")
    print("[*] Đang chạy tác vụ đo lường và sẵn sàng phục vụ... (Ctrl+C để dừng)\n")

    # Khởi động tác vụ cập nhật nền
    update_task = asyncio.create_task(sensor_update_task(sensor_res, interval=args.interval))

    try:
        await asyncio.get_running_loop().create_future()
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("\n[!] Đang tắt Sensor Server...")
    finally:
        update_task.cancel()
        await server.shutdown()
        print("[+] Sensor Server đã dừng an toàn.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
