#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BÀI THỰC HÀNH 3 (CoAP) - BÀI 1 - CHƯƠNG TRÌNH 1: COAP SERVER
Cung cấp tài nguyên: coap://localhost:5683/iot/lab/message
Hỗ trợ phương thức:
- GET: Trả về thông điệp chào mừng từ Server.
- POST: Nhận thông điệp từ Client (Họ tên SV, MSV, lời chào), in thời điểm nhận và phản hồi xác nhận.
"""

import sys
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


class MessageResource(resource.Resource):
    """
    Tài nguyên CoAP tại đường dẫn: /iot/lab/message
    Hỗ trợ xử lý yêu cầu GET và POST.
    """
    def __init__(self):
        super().__init__()
        self.welcome_message = "Xin chao tu CoAP Server"
        self.last_received_message = None

    async def render_get(self, request):
        """Xử lý yêu cầu GET: trả về thông điệp chào mừng."""
        client_address = request.remote.hostinfo if request.remote else "unknown"
        print(f"\n[*] GET request received: /iot/lab/message")
        print(f"    - Từ Client: {client_address}")
        
        response_payload = self.welcome_message.encode("utf-8")
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=response_payload
        )

    async def render_post(self, request):
        """Xử lý yêu cầu POST: nhận thông điệp từ client và xác nhận."""
        payload_text = request.payload.decode("utf-8")
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_received_message = payload_text

        print("\n" + "=" * 50)
        print("POST request received:")
        print(f"Payload: {payload_text}")
        print(f"Time: {current_time}")
        print("=" * 50)

        ack_payload = "Server da nhan thong diep".encode("utf-8")
        return aiocoap.Message(
            code=aiocoap.CHANGED,
            payload=ack_payload
        )


async def main():
    parser = argparse.ArgumentParser(
        description="BTH3 - Bai 1: CoAP Server (URI: /iot/lab/message)"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Địa chỉ IP lắng nghe (mặc định: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cổng UDP lắng nghe (mặc định: 5683)")
    args = parser.parse_args()

    root = resource.Site()
    # Đường dẫn tài nguyên: /iot/lab/message
    root.add_resource(["iot", "lab", "message"], MessageResource())

    server = await aiocoap.Context.create_server_context(root, bind=(args.host, args.port))

    print("=" * 60)
    print("      BTH3 - BAI 1: COAP MESSAGE SERVER")
    print("      Sinh vien: Nguyen Phu Binh | MSV: B23DCCN083")
    print("=" * 60)
    print(f"[*] CoAP Server started on {args.host}:{args.port}")
    print(f"[*] Tài nguyên khả dụng: coap://{args.host}:{args.port}/iot/lab/message")
    print("[*] Đang sẵn sàng phục vụ yêu cầu GET và POST... (Nhấn Ctrl+C để dừng)\n")

    try:
        # Giữ server chạy vô hạn
        await asyncio.get_running_loop().create_future()
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("\n[!] Đang tắt CoAP Server...")
    finally:
        await server.shutdown()
        print("[+] CoAP Server đã dừng an toàn.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
