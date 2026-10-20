#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BÀI THỰC HÀNH 3 (CoAP) - BÀI 2 - CHƯƠNG TRÌNH 2: MONITORING COAP CLIENT
- Gửi yêu cầu GET định kỳ mỗi 3 giây đến tài nguyên:
  coap://localhost:5683/iot/lab/sensor01/data
- Nhận và phân tích JSON:
  + Nhiệt độ > 35°C -> CẢNH BÁO: Nhiệt độ cao
  + Độ ẩm < 40%    -> CẢNH BÁO: Độ ẩm thấp
- Hỗ trợ tính thời gian phản hồi trung bình và ghi file log (mở rộng).
"""

import sys
import json
import time
import argparse
import asyncio
from datetime import datetime
import aiocoap

# Đảm bảo in tiếng Việt chuẩn trên Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


async def main():
    parser = argparse.ArgumentParser(
        description="BTH3 - Bai 2: Monitoring CoAP Client (Giam sat sensor01)"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Địa chỉ CoAP Server (mặc định: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cổng CoAP Server (mặc định: 5683)")
    parser.add_argument("--device", default="sensor01", help="Mã cảm biến cần giám sát (mặc định: sensor01)")
    parser.add_argument("--interval", type=float, default=3.0, help="Chu kỳ gửi GET (giây, mặc định: 3.0)")
    parser.add_argument("--log-file", default=None, help="Đường dẫn file ghi log CSV (tùy chọn)")
    args = parser.parse_args()

    uri = f"coap://{args.host}:{args.port}/iot/lab/{args.device}/data"

    print("=" * 60)
    print("      BTH3 - BAI 2: MONITORING COAP CLIENT")
    print("      Sinh vien: Nguyen Phu Binh | MSV: B23DCCN083")
    print("=" * 60)
    print(f"[*] Mục tiêu: {uri}")
    print(f"[*] Chu kỳ truy vấn: {args.interval} giây/lần")
    print("[*] Đang bắt đầu giám sát... Nhấn Ctrl+C để dừng.\n")

    protocol = await aiocoap.Context.create_client_context()

    total_requests = 0
    total_latency_ms = 0.0

    # Nếu có ghi log CSV, tạo header
    if args.log_file:
        try:
            with open(args.log_file, "a", encoding="utf-8") as f:
                f.write("timestamp,device_id,temperature,humidity,status\n")
        except Exception as e:
            print(f"[!] Không thể mở file log: {e}")

    try:
        while True:
            total_requests += 1
            start_time = time.time()
            get_request = aiocoap.Message(code=aiocoap.GET, uri=uri)

            try:
                response = await asyncio.wait_for(protocol.request(get_request).response, timeout=4.0)
                latency_ms = (time.time() - start_time) * 1000
                total_latency_ms += latency_ms

                raw_payload = response.payload.decode("utf-8", errors="replace")
                data = json.loads(raw_payload)

                recv_time = datetime.now().strftime("%H:%M:%S")
                device_id = data.get("device_id", args.device)
                temperature = float(data.get("temperature", 0.0))
                humidity = float(data.get("humidity", 0.0))

                print(f"[{recv_time}] Received sensor data (RTT: {latency_ms:.1f}ms)")
                print(f"Device: {device_id}")
                print(f"Temperature: {temperature:.1f} C")
                print(f"Humidity: {humidity:.1f} %")

                has_warning = False
                status_list = []
                if temperature > 35.0:
                    print("CANH BAO: Nhiet do cao")
                    has_warning = True
                    status_list.append("CANH BAO: Nhiet do cao")
                if humidity < 40.0:
                    print("CANH BAO: Do am thap")
                    has_warning = True
                    status_list.append("CANH BAO: Do am thap")

                if not has_warning:
                    print("Trang thai: Binh thuong")
                    status_list.append("Binh thuong")

                print("-" * 30)

                # Ghi ra file CSV nếu được chỉ định
                if args.log_file:
                    with open(args.log_file, "a", encoding="utf-8") as f:
                        status_str = "; ".join(status_list)
                        f.write(f"{recv_time},{device_id},{temperature},{humidity},{status_str}\n")

            except asyncio.TimeoutError:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [!] CANH BAO: Timeout, Server không phản hồi yêu cầu GET!")
                print("-" * 30)
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [!] Lỗi khi lấy dữ liệu: {e}")
                print("-" * 30)

            await asyncio.sleep(args.interval)

    except (asyncio.CancelledError, KeyboardInterrupt):
        print("\n" + "=" * 60)
        print("[!] Đã dừng giám sát.")
        if total_requests > 0:
            avg_rtt = total_latency_ms / total_requests
            print(f"[*] Thống kê:")
            print(f"    - Tổng số lần gửi yêu cầu GET: {total_requests}")
            print(f"    - Thời gian phản hồi trung bình (RTT): {avg_rtt:.2f} ms")
        print("=" * 60)
    finally:
        await protocol.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
