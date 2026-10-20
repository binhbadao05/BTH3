#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BÀI THỰC HÀNH 3 (CoAP) - BÀI 3 - CHƯƠNG TRÌNH 2: LIGHT CONTROLLER CLIENT
Kết nối tới CoAP Server, cho phép người dùng điều khiển và truy vấn đèn:
- ON: Gửi PUT bật đèn.
- OFF: Gửi PUT tắt đèn.
- STATUS: Gửi GET truy vấn trạng thái hiện tại.
- EXIT: Thoát chương trình.
"""

import sys
import json
import argparse
import asyncio
import aiocoap

# Đảm bảo in tiếng Việt chuẩn trên Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


async def send_put_command(protocol, uri, device_id, command):
    """Gửi yêu cầu PUT để điều khiển thiết bị."""
    print("Sending PUT request...")
    payload_dict = {
        "device_id": device_id,
        "command": command
    }
    payload_bytes = json.dumps(payload_dict).encode("utf-8")

    request = aiocoap.Message(
        code=aiocoap.PUT,
        uri=uri,
        payload=payload_bytes,
        content_format=50  # application/json
    )

    try:
        response = await asyncio.wait_for(protocol.request(request).response, timeout=5.0)
        print(f"Response Code: {response.code}")
        if response.code == aiocoap.CHANGED:
            if command == "ON":
                print(f"Da bat den {device_id}")
            else:
                print(f"Da tat den {device_id}")
        else:
            raw_text = response.payload.decode("utf-8", errors="replace")
            print(f"Phan hoi: {raw_text}")
    except asyncio.TimeoutError:
        print("[!] Timeout: Server khong phan hoi yeu cau PUT.")
    except Exception as e:
        print(f"[!] Loi khi gui PUT: {e}")


async def send_get_status(protocol, uri):
    """Gửi yêu cầu GET để truy vấn trạng thái hiện tại."""
    print("Sending GET request...")
    request = aiocoap.Message(code=aiocoap.GET, uri=uri)

    try:
        response = await asyncio.wait_for(protocol.request(request).response, timeout=5.0)
        raw_text = response.payload.decode("utf-8", errors="replace")
        print("Response:")
        print(raw_text)
    except asyncio.TimeoutError:
        print("[!] Timeout: Server khong phan hoi yeu cau GET.")
    except Exception as e:
        print(f"[!] Loi khi gui GET: {e}")


async def main():
    parser = argparse.ArgumentParser(
        description="BTH3 - Bai 3: Light Controller Client"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Địa chỉ CoAP Server (mặc định: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cổng CoAP Server (mặc định: 5683)")
    parser.add_argument("--device", default="light01", help="Mã thiết bị đèn (mặc định: light01)")
    args = parser.parse_args()

    uri = f"coap://{args.host}:{args.port}/iot/lab/{args.device}/status"

    print("=" * 60)
    print("      BTH3 - BAI 3: LIGHT CONTROLLER CLIENT")
    print("      Sinh vien: Nguyen Phu Binh | MSV: B23DCCN083")
    print("=" * 60)
    print(f"[*] Muc tieu: {uri}")
    print("[*] Cac lenh ho tro: ON, OFF, STATUS, EXIT\n")

    protocol = await aiocoap.Context.create_client_context()

    try:
        while True:
            # Nhập lệnh không chặn event loop
            user_input = await asyncio.to_thread(input, "Nhap lenh (ON/OFF/STATUS/EXIT): ")
            cmd = user_input.strip().upper()

            if not cmd:
                continue

            if cmd == "EXIT":
                print("[*] Thoat chuong trinh Light Controller.")
                break
            elif cmd in ["ON", "OFF"]:
                await send_put_command(protocol, uri, args.device, cmd)
            elif cmd == "STATUS":
                await send_get_status(protocol, uri)
            else:
                print(f"[!] Lenh khong hop le: '{cmd}'. Chi ho tro ON, OFF, STATUS, EXIT.")
            print()

    except (asyncio.CancelledError, KeyboardInterrupt):
        print("\n[!] Dung Controller.")
    finally:
        await protocol.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
