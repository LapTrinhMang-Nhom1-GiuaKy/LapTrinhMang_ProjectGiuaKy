using System;
using System.Windows.Forms;
using System.Drawing;

public class LoginForm : Form
{
    private TextBox txtUsername;
    private Button btnLogin;

    public LoginForm()
    {
        // Thiết lập tiêu đề cửa sổ
        this.Text = "Đăng Nhập Game Caro";
        this.Size = new Size(300, 200);

        // Tạo ô nhập tên
        txtUsername = new TextBox() { Left = 50, Top = 50, Width = 200 };
        this.Controls.Add(txtUsername);

        // Tạo nút bấm
        btnLogin = new Button() { Text = "Vào Sảnh", Left = 100, Top = 100 };
        btnLogin.Click += BtnLogin_Click; // Gán sự kiện khi click
        this.Controls.Add(btnLogin);
    }

    private void BtnLogin_Click(object sender, EventArgs e)
    {
        MessageBox.Show("Chào mừng " + txtUsername.Text + " đến với Game Caro!");
        // Ở đây bạn sẽ viết thêm code để chuyển sang Form1 (Sảnh chờ)
    }
}