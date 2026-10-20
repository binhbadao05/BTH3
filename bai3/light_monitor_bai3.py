#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BÀI THỰC HÀNH 3 (CoAP) - BÀI 3 - CHƯƠNG TRÌNH 3: LIGHT MONITORING CLIENT (OBSERVE)
Sử dụng cơ chế CoAP Observe để tự động nhận thông báo khi trạng thái đèn thay đổi.
YÊU CẦU QUAN TRỌNG:
- KHÔNG sử dụng vòng lặp GET định kỳ (polling).
- Đăng ký Observe và nhận sự kiện push tự động từ CoAP Server.
"""

import sys
import json
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


def parse_light_payload(payload_bytes, default_device="light01"):
    """Giải mã JSON payload nhận được từ Server."""
    try:
        text = payload_bytes.decode("utf-8")
        data = json.loads(text)
        dev = data.get("device_id", default_device)
        status = data.get("status", "UNKNOWN")
        return dev, status
    except Exception:
        return default_device, payload_bytes.decode("utf-8", errors="replace")


async def main():
    parser = argparse.ArgumentParser(
        description="BTH3 - Bai 3: Light Monitoring Client (CoAP Observe)"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Địa chỉ CoAP Server (mặc định: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cổng CoAP Server (mặc định: 5683)")
    parser.add_argument("--device", default="light01", help="Mã thiết bị đèn (mặc định: light01)")
    args = parser.parse_args()

    uri = f"coap://{args.host}:{args.port}/iot/lab/{args.device}/status"

    print("=" * 60)
    print("      BTH3 - BAI 3: LIGHT MONITORING CLIENT (OBSERVE)")
    print("      Sinh vien: Nguyen Phu Binh | MSV: B23DCCN083")
    print("=" * 60)
    print(f"[*] Muc tieu theo doi: {uri}")
    print("[*] Co che: CoAP Observe (Tu dong nhan notification, khong polling GET)")
    print("[*] Nhan Ctrl+C de dung theo doi.\n")

    protocol = await aiocoap.Context.create_client_context()

    print("Registering CoAP Observe...")
    # Tạo yêu cầu GET với option observe=0 để đăng ký theo dõi
    request = aiocoap.Message(code=aiocoap.GET, uri=uri, observe=0)
    pr = protocol.request(request)

    try:
        # Nhận phản hồi khởi đầu (Initial State)
        initial_response = await pr.response
        print("Observe registration successful")

        now_str = datetime.now().strftime("%H:%M:%S")
        dev, status = parse_light_payload(initial_response.payload, default_device=args.device)
        print(f"[{now_str}] Initial State")
        print(f"Device: {dev}")
        print(f"Status: {status}")

        # Lắng nghe các thông báo cập nhật tự động (State Updated) đẩy từ Server
        async for update in pr.observation:
            now_str = datetime.now().strftime("%H:%M:%S")
            dev, status = parse_light_payload(update.payload, default_device=args.device)
            print(f"[{now_str}] State Updated")
            print(f"Device: {dev}")
            print(f"Status: {status}")

    except (asyncio.CancelledError, KeyboardInterrupt):
        print("\n[!] Nguoi dung yeu cau dung theo doi.")
    except Exception as e:
        print(f"\n[!] Loi trong qua trinh Observe: {e}")
    finally:
        # Hủy đăng ký Observe an toàn
        if hasattr(pr, "observation") and pr.observation is not None:
            pr.observation.cancel()
        await protocol.shutdown()
        print("[+] Da dong ket noi Observe an toan.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
