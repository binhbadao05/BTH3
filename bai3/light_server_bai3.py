#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BÀI THỰC HÀNH 3 (CoAP) - BÀI 3 - CHƯƠNG TRÌNH 1: SMART LIGHT COAP SERVER
Mô phỏng thiết bị đèn thông minh (light01) hỗ trợ CoAP Observe.
Tài nguyên: coap://localhost:5683/iot/lab/light01/status
Chức năng:
- GET: Trả về trạng thái hiện tại (ON/OFF).
- PUT: Nhận lệnh điều khiển (ON/OFF), cập nhật trạng thái và trả về 2.04 Changed.
- Observe: Kế thừa ObservableResource, tự động notify tất cả client khi trạng thái thay đổi.
"""

import sys
import json
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


class SmartLightResource(resource.ObservableResource):
    """
    Tài nguyên Đèn thông minh (light01) hỗ trợ Observe tại /iot/lab/light01/status.
    """
    def __init__(self, device_id="light01"):
        super().__init__()
        self.device_id = device_id
        self.state = "OFF"  # Trạng thái ban đầu: OFF

    def _build_payload(self):
        data = {
            "device_id": self.device_id,
            "status": self.state
        }
        return json.dumps(data, indent=2).encode("utf-8")

    async def render_get(self, request):
        """Xử lý yêu cầu GET hoặc khởi tạo đăng ký Observe."""
        client_info = request.remote.hostinfo if request.remote else "unknown"
        observe_option = request.opt.observe
        if observe_option is not None:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] New Observe registration received from {client_info}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] GET request received from {client_info}")

        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=self._build_payload(),
            content_format=50  # application/json
        )

    async def render_put(self, request):
        """Xử lý yêu cầu PUT để bật/tắt đèn và kích hoạt Observe notification nếu trạng thái đổi."""
        client_info = request.remote.hostinfo if request.remote else "unknown"
        raw_payload = request.payload.decode("utf-8", errors="replace").strip()

        print("\n" + "=" * 50)
        print("PUT request received:")
        command = None

        # Hỗ trợ nhận cả dạng JSON hoặc text chuỗi
        try:
            req_data = json.loads(raw_payload)
            command = req_data.get("command", "").upper()
            target_device = req_data.get("device_id", self.device_id)
            print(f"Device: {target_device}")
            print(f"Command: {command}")
        except json.JSONDecodeError:
            command = raw_payload.upper()
            print(f"Device: {self.device_id}")
            print(f"Command (raw text): {command}")

        # Kiểm tra lệnh hợp lệ (chỉ ON hoặc OFF)
        if command not in ["ON", "OFF"]:
            print(f"[!] Lệnh không hợp lệ: '{command}'. Chỉ chấp nhận 'ON' hoặc 'OFF'.")
            print("=" * 50)
            err_msg = json.dumps({"error": f"Lenh khong hop le: {command}. Chi chap nhan ON hoac OFF."})
            return aiocoap.Message(
                code=aiocoap.BAD_REQUEST,
                payload=err_msg.encode("utf-8"),
                content_format=50
            )

        # Xử lý thay đổi trạng thái
        if command != self.state:
            old_state = self.state
            self.state = command
            print(f"Light state changed: {old_state} -> {self.state}")
            print(f"Notify observers: {self.state}")
            print("=" * 50)
            # Tự động gửi thông báo đến toàn bộ các client đang Observe
            self.updated_state()
        else:
            print(f"Trang thai giu nguyen: {self.state} (khong kich hoat notify)")
            print("=" * 50)

        ack_payload = json.dumps({
            "device_id": self.device_id,
            "status": self.state,
            "message": f"Den {self.device_id} hien dang {self.state}"
        }).encode("utf-8")

        return aiocoap.Message(
            code=aiocoap.CHANGED,
            payload=ack_payload,
            content_format=50
        )


async def main():
    parser = argparse.ArgumentParser(
        description="BTH3 - Bai 3: Smart Light CoAP Server (Observe)"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Địa chỉ IP lắng nghe (mặc định: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cổng UDP lắng nghe (mặc định: 5683)")
    parser.add_argument("--device", default="light01", help="Mã thiết bị đèn (mặc định: light01)")
    args = parser.parse_args()

    root = resource.Site()
    light_res = SmartLightResource(device_id=args.device)

    # Đường dẫn tài nguyên: /iot/lab/light01/status
    root.add_resource(["iot", "lab", args.device, "status"], light_res)

    server = await aiocoap.Context.create_server_context(root, bind=(args.host, args.port))

    print("=" * 60)
    print("      BTH3 - BAI 3: SMART LIGHT COAP SERVER (OBSERVE)")
    print("      Sinh vien: Nguyen Phu Binh | MSV: B23DCCN083")
    print("=" * 60)
    print(f"CoAP Smart Light Server started on {args.host}:{args.port}...")
    print(f"Resource: /iot/lab/{args.device}/status")
    print(f"Initial State: {light_res.state}")
    print("[*] Sẵn sàng nhận lệnh điều khiển PUT và đăng ký Observe... (Ctrl+C để dừng)\n")

    try:
        await asyncio.get_running_loop().create_future()
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("\n[!] Đang tắt Smart Light Server...")
    finally:
        await server.shutdown()
        print("[+] Smart Light Server đã dừng an toàn.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
