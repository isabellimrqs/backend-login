from http.server import SimpleHTTPRequestHandler
import socketserver
import os 
from urllib.parse import parse_qs, urlparse
import hashlib

class MyHandler(SimpleHTTPRequestHandler):  
    def do_GET(self):   
        if self.path =='/atividades_da_turma':
                with open(os.path.join(os.getcwd(),'cad_atividades_turma.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))

        else: 
            super().do_GET()

    def usuario_existente(self,login,senha):
        with open('dados_login.txt','r') as file:
            for line in file:
                if line.strip():
                    stored_login, stored_senha_hash, stored_nome = line.strip().split(';')
                    if login == stored_login:
                        print('cheguei aqui significando que localizei o login informado')
                        print('senha ' + senha)
                        print('senha armazenada ' + senha)

                        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
                        print(senha_hash)
                        print(stored_senha_hash)
                        return senha_hash == stored_senha_hash
            return False
        
    def adicionar_usuario(self,login,senha,nome):
        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
        print(senha_hash + 'senha hash')
        with open('dados_login.txt', 'a', encoding='utf-8') as file:
            file.write(f'{login};{senha_hash};{nome}\n')
        
    def remover_ultima_linha(self,arquivo):
        print('vou excluir a ultima linha')
        with open(arquivo, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        with open(arquivo, 'w', encoding='utf-8') as file:
            lines = file.writelines(lines[:-1])
            

    def do_POST(self):
        if self.path =='/cad_atividades_da_turma':
            content_lenght = int(self.headers['Content-Length'])
            body = self.rfile.read(content_lenght).decode('utf-8')
            form_data = parse_qs(body)

            print('Dados do formulário:')
            print('Turma:', form_data.get('codigo_turma',[''])[0])
            print('Atividade:', form_data.get('codigo_atv_turma',[''])[0])

            codigo_turma = form_data.get('codigo_turma',[''])[0]
            codigo_atv_turma = form_data.get('codigo_atv_turma',[''])[0]

            with open('dados_atividades_da_turma.txt', 'r', encoding='utf-8') as file:
                    line = file.readlines()

            with open('dados_atividades_da_turma.txt', 'w', encoding='utf-8') as file:
                        line = f'{codigo_turma};{codigo_atv_turma}\n'
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