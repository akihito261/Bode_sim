
```markdown
# Advanced Bode Plot Simulator & Op-Amp Design Tool

Đây là phần mềm mô phỏng đồ thị Bode chuyên sâu được viết bằng Python. Công cụ này hỗ trợ kỹ sư và sinh viên điện tử trong việc phân tích đáp ứng tần số, đánh giá độ ổn định (Stability Analysis) và thiết kế bù tần số (Frequency Compensation) cho mạch khuếch đại thuật toán (Op-Amp).

## 🌟 Tính Năng Nổi Bật

1.  **Vẽ Đồ Thị Bode (Gain & Phase):**
    * Tự động tính toán và vẽ biên độ (dB) và pha (độ).
    * Trục tần số hiển thị từ **0.01 Hz** để quan sát rõ đáp ứng DC.
    * Hỗ trợ thêm **Pole (Điểm cực)** và **RHP Zero (Điểm không bán phẳng phải)**.

2.  **Công Cụ Bù Miller (Miller Compensation):**
    * Tính năng chuyên biệt để mô phỏng hiệu ứng tách cực (Pole Splitting).
    * Tự động tính toán tụ bù $C_c$ dựa trên hệ số khuếch đại tầng 2 ($A_{v2}$).
    * Hiển thị trực quan $C_{in}$ và $C_{out}$ do hiệu ứng Miller sinh ra.
    * **Tương tác hai chiều:** Kéo Pole trên đồ thị để tìm $C_c$ hoặc nhập $C_c$ để thấy Poles di chuyển.

3.  **Phân Tích Độ Ổn Định:**
    * Tự động tính **Phase Margin (PM)**.
    * Xác định **Gain Crossover Frequency** ($f_{0dB}$) và **Bandwidth** ($f_{-3dB}$).
    * Hiển thị đường gióng tại điểm cắt biên để dễ dàng tra cứu.

4.  **Tương Tác & So Sánh:**
    * **Kéo thả (Drag & Drop):** Thay đổi tần số cắt bằng cách kéo trực tiếp các đường Pole trên đồ thị.
    * **Click-to-Inspect:** Nhấn vào bất kỳ điểm nào trên đường cong để xem tọa độ chính xác (Hz, dB, Deg).
    * **Chế độ so sánh:** Hỗ trợ 2 hệ thống (Av1 và Av2) để so sánh trước và sau khi bù.

---

## ⚙️ Yêu Cầu Cài Đặt

### 1. Phiên bản Python
Phần mềm yêu cầu **Python 3.7** trở lên (Khuyến nghị Python 3.9+).

### 2. Cài đặt thư viện
Bạn cần cài đặt các thư viện `numpy`, `matplotlib`, và `scipy`. Mở Terminal (hoặc CMD/PowerShell) và chạy lệnh sau:

```bash
pip install numpy matplotlib scipy

```

**Lưu ý cho người dùng Linux (Ubuntu/Debian):**
Nếu gặp lỗi liên quan đến thư viện giao diện `tkinter`, hãy chạy lệnh sau:

```bash
sudo apt-get install python3-tk

```

*(Trên Windows và macOS, tkinter thường đã được cài sẵn cùng Python).*

---

## 🚀 Hướng Dẫn Sử Dụng

### Bước 1: Chạy chương trình

Mở terminal tại thư mục chứa file code và chạy:

```bash
python <ten_file_cua_ban>.py

```

### Bước 2: Thiết lập thông số cơ bản

1. **Gain DC:** Nhập hệ số khuếch đại vòng hở tại DC (ví dụ: `10000000` cho 140dB) ở góc trên bên trái. Nhấn Enter.
2. **Thêm Pole/Zero:**
* Nhấn **"+ Thêm Pole"** để thêm các điểm cực của mạch (ví dụ: cực tại ngõ ra tầng 1 và tầng 2).
* Nhập giá trị điện trở () và tụ điện () thực tế của mạch.
* Nhấn **"+ Thêm Zero (RHP)"** nếu mạch có điểm không nằm bên phải mặt phẳng phức (thường gặp khi dùng tụ bù Miller mà không có trở Nulling).



### Bước 3: Sử dụng Chế độ Bù Miller (Op-Amp Design)

Đây là tính năng quan trọng nhất để thiết kế ổn định mạch:

1. Đảm bảo bạn đã có ít nhất **2 Poles (P1, P2)** trong danh sách.
2. Đánh dấu vào ô **"Bật tính Cc (Miller)"**.
3. Nhập **Gain Tầng 2 (Av2)** (ví dụ: 50 hoặc 100).
4. **Điều chỉnh:**
* **Cách 1:** Nhập giá trị tụ bù vào ô **Cc** (ví dụ `10e-12` cho 10pF).
* **Cách 2 (Trực quan):** Dùng chuột **kéo đường P2** (hoặc P1) trên đồ thị. Chương trình sẽ tự động tính ngược ra  cần thiết và cập nhật vị trí của Pole còn lại theo hiệu ứng Miller.


5. Quan sát **Phase Margin (PM)** ở bảng thông tin góc dưới bên trái. Mục tiêu thường là .

### Bước 4: So sánh (Tùy chọn)

1. Nhấn nút **"+ Kích hoạt Av2"**.
2. Thiết lập thông số cho hệ thống 2 (ví dụ: mạch khi chưa bù) để so sánh hiệu quả với hệ thống 1 (mạch đã bù).

---

## 📝 Các Công Thức Được Sử Dụng

Chương trình sử dụng các công thức gần đúng chuẩn trong thiết kế vi mạch Analog:

1. **Tần số Pole/Zero:**


2. **Hiệu ứng Miller:**
Khi bật chế độ Miller, tụ  tại các nút Pole 1 và Pole 2 được tính lại:
* Tại Pole 1 (Dominant): 
* Tại Pole 2 (Non-dominant): 


3. **Right Half Plane Zero (RHPZ):**
Zero được thêm vào sẽ làm tăng biên độ (+20dB/dec) nhưng làm giảm pha (-90°), đặc trưng của RHP Zero trong mạch Op-Amp.

---

## ⚠️ Khắc phục sự cố

* **Đồ thị bị trắng/không hiện:** Kiểm tra xem bạn đã nhập Gain và thêm ít nhất 1 Pole chưa.
* **Không kéo được Pole:** Khi đang bật chế độ Miller, việc kéo Pole bị ràng buộc bởi công thức toán học. Nếu kéo quá nhanh ra vùng tần số mà , chương trình sẽ giới hạn . Hãy thử nhập trực tiếp số vào ô Cc.
* **Lỗi hiển thị font chữ:** Đảm bảo máy tính có font Arial hoặc chỉnh sửa code phần `font=("Arial", ...)` nếu cần.

---

**Tác giả:** Nguyễn Đức Tự
**Phiên bản:** 1.0

```

```
