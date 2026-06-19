import http.server
import socketserver
import os

PORT = 5000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 处理根路径
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>胶卷价格追踪应用</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                    }
                    h1 {
                        color: #333;
                    }
                    .film {
                        border: 1px solid #ddd;
                        padding: 10px;
                        margin: 10px 0;
                        border-radius: 5px;
                    }
                    .film h2 {
                        margin-top: 0;
                        color: #555;
                    }
                </style>
            </head>
            <body>
                <h1>胶卷价格追踪应用</h1>
                <p>欢迎使用胶卷价格追踪应用！</p>
                <div class="film">
                    <h2>柯达 Gold 200</h2>
                    <p>品牌: 柯达</p>
                    <p>型号: Gold 200</p>
                    <p>ISO: 200</p>
                    <p>格式: 35mm</p>
                    <p>当前价格: ¥45.00</p>
                </div>
                <div class="film">
                    <h2>富士 Superia X-Tra 400</h2>
                    <p>品牌: 富士</p>
                    <p>型号: Superia X-Tra 400</p>
                    <p>ISO: 400</p>
                    <p>格式: 35mm</p>
                    <p>当前价格: ¥52.00</p>
                </div>
            </body>
            </html>
            '''
            self.wfile.write(html.encode('utf-8'))
        else:
            # 处理其他路径
            super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"服务器运行在 http://localhost:{PORT}")
        print("按 Ctrl+C 停止服务器")
        httpd.serve_forever()
