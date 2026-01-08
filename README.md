Markdown# Advanced Bode Plot Simulator & Op-Amp Design Tool

Đây là phần mềm mô phỏng đồ thị Bode chuyên sâu được viết bằng Python. Công cụ này hỗ trợ kỹ sư và sinh viên điện tử trong việc phân tích đáp ứng tần số, đánh giá độ ổn định (Stability Analysis) và thiết kế bù tần số (Frequency Compensation) cho mạch khuếch đại thuật toán (Op-Amp).

---

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

---

## ⚙️ Yêu Cầu Cài Đặt

### 1. Phiên bản Python
Phần mềm yêu cầu **Python 3.7** trở lên (Khuyến nghị Python 3.9+).

### 2. Cài đặt thư viện
Bạn cần cài đặt các thư viện `numpy`, `matplotlib`, và `scipy`. 

Mở Terminal (hoặc CMD/PowerShell) và chạy lệnh sau:

```bash
pip install numpy matplotlib scipy
Lưu ý cho người dùng Linux (Ubuntu/Debian):Nếu gặp lỗi liên quan đến thư viện giao diện tkinter, hãy chạy lệnh sau:Bashsudo apt-get install python3-tk
(Trên Windows và macOS, tkinter thường đã được cài sẵn cùng Python).🚀 Hướng Dẫn Sử DụngBước 1: Khởi độngMở terminal tại thư mục chứa file code và chạy lệnh:Bashpython bode_simulator.py
(Thay bode_simulator.py bằng tên file bạn đã lưu)Bước 2: Thiết lập thông số cơ bảnGain DC: Nhập hệ số khuếch đại vòng hở tại DC (ví dụ: 10000000 cho 140dB) ở góc trên bên trái. Nhấn Enter hoặc nút Cập nhật Gain.Thêm Pole/Zero:Nhấn "+ Thêm Pole" để thêm các điểm cực của mạch.Nhập giá trị điện trở ($R$) và tụ điện ($C$) thực tế của mạch.Nhấn "+ Thêm Zero (RHP)" nếu mạch có điểm không nằm bên phải mặt phẳng phức (ví dụ do đường truyền thẳng qua $C_c$).Bước 3: Sử dụng Chế độ Bù Miller (Quan trọng)Đây là tính năng dùng để thiết kế ổn định cho Op-Amp 2 tầng:Điều kiện: Đảm bảo bạn đã có ít nhất 2 Poles (P1, P2) trong danh sách.Kích hoạt: Đánh dấu vào ô "Bật tính Cc (Miller)".Nhập thông số:Nhập Gain Tầng 2 (Av2) (ví dụ: 100).Điều chỉnh tụ bù:Cách 1: Nhập giá trị tụ bù vào ô Cc (ví dụ 10e-12 cho 10pF).Cách 2: Dùng chuột kéo đường P2 (hoặc P1) trên đồ thị. Chương trình sẽ tự động tính ngược ra $C_c$ cần thiết và cập nhật vị trí của Pole còn lại.Kết quả: Quan sát Phase Margin (PM) ở bảng thông tin góc dưới bên trái. Mục tiêu thường là $PM \approx 60^\circ$.⚠️ Khắc phục sự cốLỗi hiển thị: Nếu đồ thị bị trắng, hãy kiểm tra xem bạn đã nhập Gain DC chưa.Không kéo được Pole: Khi đang bật chế độ Miller, việc kéo Pole bị ràng buộc bởi công thức toán học. Nếu kéo quá nhanh ra vùng tần số không hợp lệ (làm cho $C_{total} < C_{goc}$), $C_c$ sẽ về 0. Hãy thử nhập trực tiếp số vào ô Cc để chính xác hơn.Phiên bản: 1.1
