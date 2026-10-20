# BÁO CÁO BUỔI THỰC HÀNH 3: LẬP TRÌNH PYTHON VỚI GIAO THỨC CoAP

> **Học phần**: Internet of Things (IoT) / Lập trình Mạng IoT  
> **Sinh viên thực hiện**: Nguyễn Phú Bình  
> **Mã sinh viên**: B23DCCN083  
> **Lớp**: D23CNPM06  

---

## 1. Giới Thiệu & Mục Tiêu Buổi Thực Hành
Buổi thực hành giúp sinh viên nắm vững nguyên lý hoạt động của giao thức **CoAP (Constrained Application Protocol - RFC 7252)** và mô hình giao tiếp Client–Server trong các hệ thống IoT:
1. Hiểu cách xây dựng **CoAP Server** và **CoAP Client** bằng Python thông qua thư viện `aiocoap`.
2. Sử dụng thành thạo các phương thức chuẩn:
   - `GET`: Truy vấn tài nguyên.
   - `POST`: Gửi thông điệp, cập nhật dữ liệu.
   - `PUT`: Điều khiển, thay đổi trạng thái tài nguyên.
3. Tổ chức dữ liệu IoT theo chuẩn: **Thiết bị (Device) → Tài nguyên (Resource) → URI → Payload (JSON)**.
4. Hiểu và triển khai cơ chế **CoAP Observe (RFC 7641)** để thiết bị tự động gửi thông báo (push notification) tới Client khi trạng thái thay đổi, loại bỏ việc dùng vòng lặp polling GET định kỳ gây tốn tài nguyên mạng.

---

## 2. Cấu Trúc Mã Nguồn BTH3

Cấu trúc thư mục được tổ chức theo đúng yêu cầu nộp bài trong tài liệu thực hành:

```text
BTH3/
├── bai1/
│   ├── coap_server_bai1.py      # [Bài 1] CoAP Server cung cấp /iot/lab/message
│   └── coap_client_bai1.py      # [Bài 1] CoAP Client gửi GET và POST
│
├── bai2/
│   ├── sensor_server_bai2.py    # [Bài 2] Server cảm biến cập nhật JSON mỗi 3s
│   └── monitor_client_bai2.py   # [Bài 2] Client giám sát, cảnh báo nhiệt độ/độ ẩm
│
├── bai3/
│   ├── light_server_bai3.py     # [Bài 3] Server đèn thông minh hỗ trợ CoAP Observe
│   ├── light_controller_bai3.py # [Bài 3] Client nhập lệnh ON/OFF/STATUS từ bàn phím
│   └── light_monitor_bai3.py    # [Bài 3] Client đăng ký Observe nhận push notification
│
├── requirements.txt             # Khai báo thư viện aiocoap
├── .gitignore                   # Bỏ qua file cache Python, log tạm
└── README.md                    # Báo cáo chi tiết Buổi 3 CoAP
```

---

## 3. Môi Trường & Cài Đặt

- **Ngôn ngữ**: Python 3.10+ (Đã kiểm thử trên Python 3.13)
- **Thư viện CoAP**: `aiocoap>=0.4.17`
- **Giao thức truyền vận**: UDP, cổng mặc định **`5683`**
- **Địa chỉ thử nghiệm**: `localhost` (`127.0.0.1`)

### Cài đặt môi trường:
```bash
pip install -r requirements.txt
```
*(Hoặc: `pip install aiocoap`)*

> [!NOTE]
> Giao thức CoAP hoạt động trên tầng mạng UDP cổng 5683. Khi triển khai giữa hai máy tính khác nhau trong mạng LAN, cần bảo đảm tường lửa (Windows Defender Firewall) cho phép truyền gói tin UDP trên cổng 5683.

---

## 4. Hướng Dẫn Chạy & Kết Quả Từng Bài

### 🔹 BÀI 1: Ứng Dụng Gửi và Nhận Thông Điệp CoAP Cơ Bản
- **Tài nguyên**: `coap://localhost:5683/iot/lab/message`
- **Cơ chế**:
  - `GET`: Trả về thông điệp chào mừng: `"Xin chao tu CoAP Server"`.
  - `POST`: Nhận thông tin sinh viên, in ra console thời điểm nhận và phản hồi `2.04 Changed` với payload: `"Server da nhan thong diep"`.

#### Cách chạy:
```bash
# Terminal 1: Khởi động Server
python bai1/coap_server_bai1.py

# Terminal 2: Chạy Client thực hiện GET & POST
python bai1/coap_client_bai1.py
```

#### Log minh chứng kết quả chạy:

**Tại màn hình Server (`coap_server_bai1.py`):**
```text
============================================================
      BTH3 - BAI 1: COAP MESSAGE SERVER
      Sinh vien: Nguyen Phu Binh | MSV: B23DCCN083
============================================================
[*] CoAP Server started on 127.0.0.1:5683
[*] Tài nguyên khả dụng: coap://127.0.0.1:5683/iot/lab/message
[*] Đang sẵn sàng phục vụ yêu cầu GET và POST... (Nhấn Ctrl+C để dừng)

[*] GET request received: /iot/lab/message
    - Từ Client: 127.0.0.1:51234

==================================================
POST request received:
Payload: Xin chao tu CoAP Client - B23DCCN083 - Nguyen Phu Binh
Time: 10:15:20
==================================================
```

**Tại màn hình Client (`coap_client_bai1.py`):**
```text
============================================================
      BTH3 - BAI 1: COAP MESSAGE CLIENT
      Sinh vien: Nguyen Phu Binh | MSV: B23DCCN083
============================================================
CoAP Client
Sending GET request...
URI: coap://127.0.0.1:5683/iot/lab/message
Response:
Code: 2.05 Content
Payload: Xin chao tu CoAP Server
--------------------------------------------------
Sending POST request...
Payload: Xin chao tu CoAP Client - B23DCCN083 - Nguyen Phu Binh
Response:
Code: 2.04 Changed
Payload: Server da nhan thong diep
============================================================
[+] Hoàn tất kịch bản kiểm thử GET và POST.
```

---

### 🔹 BÀI 2: Mô Phỏng Cảm Biến Nhiệt Độ và Độ Ẩm Bằng CoAP
- **Tài nguyên**: `coap://localhost:5683/iot/lab/sensor01/data`
- **Content-Format**: `application/json` (Code: 50 theo RFC 7252)
- **Cơ chế**:
  - `sensor_server_bai2.py` tự động sinh ngẫu nhiên nhiệt độ và độ ẩm sau mỗi 3 giây.
  - `monitor_client_bai2.py` gửi GET định kỳ 3 giây, parse JSON và đánh giá ngưỡng cảnh báo:
    - Nếu `nhiệt độ > 35°C`: Hiển thị `CANH BAO: Nhiet do cao`
    - Nếu `độ ẩm < 40%`: Hiển thị `CANH BAO: Do am thap`
    - Nếu bình thường: Hiển thị `Trang thai: Binh thuong`

#### Cách chạy:
```bash
# Terminal 1: Khởi động Server cảm biến
python bai2/sensor_server_bai2.py

# Terminal 2: Chạy Client giám sát
python bai2/monitor_client_bai2.py
```

#### Log minh chứng kết quả chạy:

**Tại màn hình Client Giám Sát (`monitor_client_bai2.py`):**
```text
============================================================
      BTH3 - BAI 2: MONITORING COAP CLIENT
      Sinh vien: Nguyen Phu Binh | MSV: B23DCCN083
============================================================
[*] Mục tiêu: coap://127.0.0.1:5683/iot/lab/sensor01/data
[*] Chu kỳ truy vấn: 3.0 giây/lần
[*] Đang bắt đầu giám sát... Nhấn Ctrl+C để dừng.

[10:20:03] Received sensor data (RTT: 4.2ms)
Device: sensor01
Temperature: 36.1 C
Humidity: 38.7 %
CANH BAO: Nhiet do cao
CANH BAO: Do am thap
------------------------------
[10:20:06] Received sensor data (RTT: 3.8ms)
Device: sensor01
Temperature: 29.4 C
Humidity: 62.5 %
Trang thai: Binh thuong
------------------------------
```

---

### 🔹 BÀI 3: Hệ Thống Giám Sát và Điều Khiển Đèn Thông Minh Bằng CoAP Observe
- **Tài nguyên**: `coap://localhost:5683/iot/lab/light01/status`
- **Cơ chế hoạt động**:
  - Server kế thừa `ObservableResource`. Trạng thái ban đầu: `OFF`.
  - `light_controller_bai3.py`: Gửi yêu cầu `PUT` để điều khiển bật (`ON`), tắt (`OFF`), hoặc `GET` lấy trạng thái (`STATUS`).
  - `light_monitor_bai3.py`: Đăng ký **CoAP Observe** (`observe=0`). Khi trạng thái đèn thay đổi qua lệnh PUT từ controller, Server **tự động đẩy thông báo mới** đến tất cả Monitoring Client đang Observe (*hoàn toàn không dùng vòng lặp polling GET*).

#### Cách chạy (mở 3 terminal song song):
```bash
# Terminal 1: Khởi động Server Đèn
python bai3/light_server_bai3.py

# Terminal 2: Khởi động Client Giám Sát (Observe)
python bai3/light_monitor_bai3.py

# Terminal 3: Khởi động Controller Client (Điều khiển)
python bai3/light_controller_bai3.py
```

#### Log minh chứng kết quả chạy:

**Terminal 1 – Smart Light Server (`light_server_bai3.py`):**
```text
CoAP Smart Light Server started on 127.0.0.1:5683...
Resource: /iot/lab/light01/status
Initial State: OFF
[*] Sẵn sàng nhận lệnh điều khiển PUT và đăng ký Observe...

[10:30:00] New Observe registration received from 127.0.0.1:52100

==================================================
PUT request received:
Device: light01
Command: ON
Light state changed: OFF -> ON
Notify observers: ON
==================================================

==================================================
PUT request received:
Device: light01
Command: OFF
Light state changed: ON -> OFF
Notify observers: OFF
==================================================
```

**Terminal 2 – Monitoring Client Observe (`light_monitor_bai3.py`):**
```text
============================================================
      BTH3 - BAI 3: LIGHT MONITORING CLIENT (OBSERVE)
============================================================
[*] Muc tieu theo doi: coap://127.0.0.1:5683/iot/lab/light01/status
[*] Co che: CoAP Observe (Tu dong nhan notification, khong polling GET)
[*] Nhan Ctrl+C de dung theo doi.

Registering CoAP Observe...
Observe registration successful
[10:30:00] Initial State
Device: light01
Status: OFF
[10:30:15] State Updated
Device: light01
Status: ON
[10:30:25] State Updated
Device: light01
Status: OFF
```

**Terminal 3 – Controller Client (`light_controller_bai3.py`):**
```text
Nhap lenh (ON/OFF/STATUS/EXIT): ON
Sending PUT request...
Response Code: 2.04 Changed
Da bat den light01

Nhap lenh (ON/OFF/STATUS/EXIT): STATUS
Sending GET request...
Response:
{
  "device_id": "light01",
  "status": "ON"
}

Nhap lenh (ON/OFF/STATUS/EXIT): OFF
Sending PUT request...
Response Code: 2.04 Changed
Da tat den light01
```

---

## 5. Kết Luận & Đánh Giá
- **100% Hoàn thành**: Triển khai đầy đủ và chính xác tất cả các chức năng theo yêu cầu của tài liệu `Thực hành buổi 3 python coap.docx`.
- **Chuẩn giao thức**:
  - Định nghĩa tài nguyên theo cây URI chuẩn RESTful/CoAP.
  - Sử dụng đúng mã phản hồi: `2.05 Content`, `2.04 Changed`, `4.00 Bad Request`.
  - Thiết lập chuẩn Content-Format `application/json` (50).
- **Tính năng Observe nâng cao**: Triển khai chuẩn cơ chế Publish-Subscribe thông qua CoAP Observe RFC 7641, phản hồi thời gian thực với độ trễ thấp và tối ưu hóa băng thông mạng.
