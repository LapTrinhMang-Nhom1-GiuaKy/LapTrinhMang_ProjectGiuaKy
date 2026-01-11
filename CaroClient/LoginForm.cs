using System;
using System.Windows.Forms;
using System.Drawing;
// --- BỎ VÀO ĐÂY: Thêm 2 dòng này để dùng được mạng ---
using System.Net.Sockets;
using System.Text;
// --------------------------------------------------

public class LoginForm : Form
{
    private TextBox txtUsername;
    private Button btnLogin;

    public LoginForm()
    {
        this.Text = "Đăng Nhập Game Caro";
        this.Size = new Size(300, 200);

        txtUsername = new TextBox() { Left = 50, Top = 50, Width = 200 };
        this.Controls.Add(txtUsername);

        btnLogin = new Button() { Text = "Vào Sảnh", Left = 100, Top = 100 };
        // Gán sự kiện click cho nút bấm
        btnLogin.Click += BtnLogin_Click; 
        this.Controls.Add(btnLogin);
    }

    private void BtnLogin_Click(object sender, EventArgs e)
    {
        // --- BỎ VÀO ĐÂY: Logic kết nối khi nhấn nút ---
        string playerName = txtUsername.Text;
        if (string.IsNullOrEmpty(playerName)) {
            MessageBox.Show("Vui lòng nhập tên!");
            return;
        }

        try {
            // Kết nối tới server Python (IP 127.0.0.1, Port 8000)
            TcpClient client = new TcpClient("127.0.0.1", 8000);
            NetworkStream stream = client.GetStream();

            // Gửi lệnh HELLO theo đúng yêu cầu của server.py
            byte[] data = Encoding.UTF8.GetBytes("HELLO " + playerName + "\n");
            stream.Write(data, 0, data.Length);

            MessageBox.Show("Kết nối thành công! Đang vào sảnh chờ...");
            
            // Sau này bạn sẽ code thêm phần mở Form1 (Sảnh chờ) ở đây
        }
        catch (Exception ex) {
            MessageBox.Show("Không kết nối được Server: " + ex.Message);
        }
        // --------------------------------------------------
    }
}