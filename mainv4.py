from http.server import SimpleHTTPRequestHandler
import socketserver
import os 
from urllib.parse import parse_qs

class MyHandler(SimpleHTTPRequestHandler):
 
    def do_GET(self):
        if self.path =='/atividades':
            try:
                with open(os.path.join(os.getcwd(),'cad_atividades.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404,"File not found")

        else: 
            super().do_GET()            

    def do_POST(self):
        if self.path =='/cad_atividades':
            content_lenght = int(self.headers['Content-Length'])
            body = self.rfile.read(content_lenght).decode('utf-8')
            form_data = parse_qs(body)

            print('Dados do formulário:')
            print('Código:', form_data.get('codigo',[''])[0])
            print('Descrição:', form_data.get('descricao',[''])[0])

            codigo = form_data.get('codigo',[''])[0]
            descricao = form_data.get('descricao',[''])[0]

            with open('dados_atividades.txt', 'r', encoding='utf-8') as file:
                    line = file.readlines()

            with open('dados_atividades.txt', 'w', encoding='utf-8') as file:
                        line = f'{codigo};{descricao};\n'
                        file.write(line)

            with open(os.path.join(os.getcwd(),'dados_ok.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
            self.send_response(302)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        
        else: 
            super(MyHandler,self).do_POST()

    
endereco_ip = "0.0.0.0"

porta = 8000

with socketserver.TCPServer((endereco_ip,porta),MyHandler) as httpd:
    print(f'Servidor iniciado em {endereco_ip} na porta {porta}')
    httpd.serve_forever()