# 🎮 Rock Paper Scissors - Multi Client - Server Game

## Mô tả
- Đây là ứng dụng Game Kéo – Búa – Bao (Rock – Paper – Scissors) được xây dựng theo mô hình Client – Server sử dụng Socket trong Python.

- Server có khả năng xử lý nhiều client cùng lúc (Multi-client), cho phép nhiều người chơi kết nối, tham gia chơi game và nhận kết quả trực tiếp từ server.

## Công nghệ sử dụng
- Python 3.9+
- Thư viện chuẩn:
    + socket
    + threading

## Cấu trúc thư mục


## Cách chạy

### Chạy server
python server.py

### Chạy client
python client.py

Sau đó nhập:
- Nhập tên người chơi: <Tên bất kỳ>
- Sau khi kết nối thành công, người chơi có thể chọn: Kéo / Búa / Bao

## Luật chơi
- Rock (Kéo) thắng Scissors (Bao)
- Scissors (Bao) thắng Paper (Búa)
- Paper (Búa) thắng Rock (Kéo)
- Hai lựa chọn giống nhau → Hòa
