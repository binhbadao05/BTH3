# Bài Thực Hành 3: Mô Phỏng Hệ Thống Điều Phối Cảnh Báo IoT Với Exchange trong AMQP

> **Sinh viên thực hiện**: Nguyễn Phú Bình | **MSV**: B23DCCN083 | **Lớp**: D23CNPM06

## 1. Mục Tiêu
- Làm quen và vận dụng mô hình phân phối message nâng cao bằng **Exchange** và **Routing Key** trong AMQP.
- Sử dụng **Direct Exchange** (`iot_alert_exchange`) để định tuyến thông điệp cảnh báo chính xác tới các queue tương ứng theo mức độ:
  - `info`: Thông tin chung (không định tuyến vào 2 queue cảnh báo).
  - `warning`: Cảnh báo mức vừa (định tuyến vào `warning_queue`).
  - `critical`: Cảnh báo nguy cấp (định tuyến vào `critical_queue`).
- Mở rộng: Tạo consumer nhận toàn bộ cảnh báo và ghi log ra file `alerts.log`.

---

## 2. Cấu Trúc Thư Mục
```text
BTH3/
├── alert_producer_bai3.py       # Phát các cảnh báo với mức info, warning, critical
├── warning_consumer_bai3.py     # Chỉ nhận và xử lý cảnh báo mức warning
├── critical_consumer_bai3.py    # Chỉ nhận và xử lý cảnh báo mức critical
├── all_alerts_consumer_bai3.py  # [Mở rộng] Nhận tất cả cảnh báo & ghi file log
└── README.md                    # Hướng dẫn chi tiết Bài 3
```

---

## 3. Kiến Trúc Định Tuyến AMQP

```
                                      +--------------------+
                              +-----> |   warning_queue    | ----> warning_consumer_bai3.py
                              |       +--------------------+
                              | (routing_key='warning')
+-----------------------+     |
|  alert_producer_bai3  |     |
|   (Phát message)      | --->| Direct Exchange: 'iot_alert_exchange'
+-----------------------+     |
                              | (routing_key='critical')
                              |       +--------------------+
                              +-----> |   critical_queue   | ----> critical_consumer_bai3.py
                              |       +--------------------+
                              |
                              | (routing_key='info')
                              +-----> (Bỏ qua / hoặc all_alerts_queue)
```

---

## 4. Hướng Dẫn Chạy Chương Trình

### Bước 1: Mở các Consumer lắng nghe
Để quan sát cơ chế định tuyến thông điệp, mở 2 terminal song song:

- **Terminal 1 - Warning Consumer**:
  ```bash
  python warning_consumer_bai3.py
  ```

- **Terminal 2 - Critical Consumer**:
  ```bash
  python critical_consumer_bai3.py
  ```

- *(Tùy chọn mở rộng)* **Terminal 3 - All Alerts Logger**:
  ```bash
  python all_alerts_consumer_bai3.py
  ```

---

### Bước 2: Chạy Alert Producer để phát cảnh báo
Mở một terminal mới và chạy:

#### Cách 1: Chạy kịch bản kiểm thử mặc định (Gửi lần lượt info, warning, critical)
```bash
python alert_producer_bai3.py
```

#### Cách 2: Gửi cảnh báo cụ thể theo mức:
```bash
# Gửi mức warning:
python alert_producer_bai3.py --severity warning --message "Nhiet do phong may chuot muc warning"

# Gửi mức critical:
python alert_producer_bai3.py --severity critical --message "Cam bien kho lanh mat ket noi critical"

# Gửi mức info:
python alert_producer_bai3.py --severity info --message "He thong vua duoc bao tri thanh cong"
```

#### Cách 3: Chạy mô phỏng phát cảnh báo tuần hoàn tự động:
```bash
python alert_producer_bai3.py --loop --interval 2.0
```

---

## 5. Kết Quả Đạt Được

### Tại màn hình Alert Producer:
```text
============================================================
      BTH3 - ALERT PRODUCER (DIRECT EXCHANGE)
============================================================
[*] Đang kết nối tới broker: localhost:5672...
[+] Đã tạo / kiểm tra Direct Exchange: 'iot_alert_exchange'

[*] Đang gửi bộ 3 cảnh báo mẫu (info, warning, critical) để kiểm thử:
 [x] Đã phát [INFO] (routing_key='info'): "He thong khoi dong thanh cong va hoat dong on dinh"
 [x] Đã phát [WARNING] (routing_key='warning'): "Nhiet do phong may vuot nguong warning"
 [x] Đã phát [CRITICAL] (routing_key='critical'): "Cam bien kho lanh mat ket noi critical"

[+] Đã gửi xong bộ kiểm thử.
```

### Tại màn hình Warning Consumer (chỉ nhận warning):
```text
============================================================
      BTH3 - WARNING CONSUMER
============================================================
[*] Đang kết nối tới broker: localhost:5672...
[+] Đã bind queue 'warning_queue' vào exchange 'iot_alert_exchange'
[+] Routing Key: 'warning'
[*] Đang lắng nghe các cảnh báo WARNING. Nhấn Ctrl+C để dừng.

[warning_queue] Da nhan: Nhiet do phong may vuot nguong warning
               (Thoi gian: 14:10:05 | Routing Key: warning)
```

### Tại màn hình Critical Consumer (chỉ nhận critical):
```text
============================================================
      BTH3 - CRITICAL CONSUMER
============================================================
[*] Đang kết nối tới broker: localhost:5672...
[+] Đã bind queue 'critical_queue' vào exchange 'iot_alert_exchange'
[+] Routing Key: 'critical'
[*] Đang lắng nghe các cảnh báo CRITICAL. Nhấn Ctrl+C để dừng.

[critical_queue] Da nhan: Cam bien kho lanh mat ket noi critical
                (Thoi gian: 14:10:06 | Routing Key: critical)
```

### Đánh giá định tuyến:
- Message `info`: Cả `warning_consumer` và `critical_consumer` đều **không** nhận (đúng chuẩn).
- Message `warning`: Chỉ `warning_queue` nhận.
- Message `critical`: Chỉ `critical_queue` nhận.
