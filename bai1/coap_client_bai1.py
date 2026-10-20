#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BÀI THỰC HÀNH 3 (CoAP) - BÀI 1 - CHƯƠNG TRÌNH 2: COAP CLIENT
Kết nối tới CoAP Server, thực hiện:
1. Gửi yêu cầu GET tới tài nguyên /iot/lab/message và hiển thị phản hồi.
2. Gửi yêu cầu POST chứa thông tin sinh viên tới /iot/lab/message và hiển thị phản hồi.
"""

import sys
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

DEFAULT_NAME = "Nguyen Phu Binh"
DEFAULT_ID = "B23DCCN083"


async def main():
    parser = argparse.ArgumentParser(
        description="BTH3 - Bai 1: CoAP Client (GET & POST toi /iot/lab/message)"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Địa chỉ CoAP Server (mặc định: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cổng CoAP Server (mặc định: 5683)")
    parser.add_argument("--name", default=DEFAULT_NAME, help=f"Họ tên sinh viên (mặc định: {DEFAULT_NAME})")
    parser.add_argument("--id", dest="student_id", default=DEFAULT_ID, help=f"Mã sinh viên (mặc định: {DEFAULT_ID})")
    parser.add_argument("--message", default=None, help="Thông điệp tùy biến (nếu không cung cấp sẽ tạo theo mẫu)")
    args = parser.parse_args()

    uri = f"coap://{args.host}:{args.port}/iot/lab/message"

    if args.message:
        post_message = args.message
    else:
        post_message = f"Xin chao tu CoAP Client - {args.student_id} - {args.name}"

    print("=" * 60)
    print("      BTH3 - BAI 1: COAP MESSAGE CLIENT")
    print(f"      Sinh vien: {args.name} | MSV: {args.student_id}")
    print("=" * 60)

    protocol = await aiocoap.Context.create_client_context()

    try:
        # ---------------------------------------------------------
        # BƯỚC 1: GỬI YÊU CẦU GET
        # ---------------------------------------------------------
        print("CoAP Client")
        print("Sending GET request...")
        print(f"URI: {uri}")

        get_request = aiocoap.Message(code=aiocoap.GET, uri=uri)
        try:
            get_response = await asyncio.wait_for(protocol.request(get_request).response, timeout=5.0)
            payload_str = get_response.payload.decode("utf-8", errors="replace")
            print("Response:")
            print(f"Code: {get_response.code}")
            print(f"Payload: {payload_str}")
        except asyncio.TimeoutError:
            print("[!] Timeout: Server không phản hồi yêu cầu GET trong vòng 5 giây.")
            return
        except Exception as e:
            print(f"[!] Lỗi khi gửi GET: {e}")
            return

        print("-" * 50)

        # ---------------------------------------------------------
        # BƯỚC 2: GỬI YÊU CẦU POST
        # ---------------------------------------------------------
        print("Sending POST request...")
        print(f"Payload: {post_message}")

        post_request = aiocoap.Message(
            code=aiocoap.POST,
            uri=uri,
            payload=post_message.encode("utf-8")
        )

        try:
            post_response = await asyncio.wait_for(protocol.request(post_request).response, timeout=5.0)
            ack_str = post_response.payload.decode("utf-8", errors="replace")
            print("Response:")
            print(f"Code: {post_response.code}")
            print(f"Payload: {ack_str}")
        except asyncio.TimeoutError:
            print("[!] Timeout: Server không phản hồi yêu cầu POST trong vòng 5 giây.")
        except Exception as e:
            print(f"[!] Lỗi khi gửi POST: {e}")

        print("=" * 60)
        print("[+] Hoàn tất kịch bản kiểm thử GET và POST.")

    finally:
        await protocol.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Client đã dừng.")
