from http.server import SimpleHTTPRequestHandler
import socketserver
import os 
from urllib.parse import parse_qs, urlparse
import hashlib
from database import conectar

conexao = conectar()

class MyHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try: 
            with open(os.path.join(path, 'home.html'),'r',encoding='utf-8') as f:
                self.send_response(200)
                self.send_header('Content-type','text/html; charset=UTF-8')
                self.end_headers()
                self.wfile.write(f.read().encode('utf-8'))
                f.close()
            return None
        except FileNotFoundError:
            pass

        return super().list_directory(path)
    
    def do_GET(self):
        if self.path =='/login':
            try:
                with open(os.path.join(os.getcwd(),'login.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404,"File not found")

        elif self.path == "/login_failed":
            self.send_response(200)
            self.send_header('Content-type', 'text/html;charset=utf-8')
            self.end_headers()
             
            with open(os.path.join(os.getcwd(), 'login.html'),'r',encoding='utf-8') as login_file:
                content = login_file.read()

            mensagem = "Login e/ou senha incoreta. Tente novamente"
            content = content.replace('<!-- Mensagem de erro será inserida aqui -->', f'<div class="error_message">{mensagem}</div>')
            self.wfile.write(content.encode('utf-8'))

        elif self.path.startswith('/cadastro'):
            query_pramas = parse_qs(urlparse(self.path).query)
            login = query_pramas.get('email',[''])[0]
            senha = query_pramas.get('senha',[''])[0]

            welcome_message = f'Olá {login}, seja bem-vindo Percebemos que você é novo por aqui'

            self.send_response(200)
            self.send_header('Content-type', 'text/html;charset=utf-8')
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cadastro.html'),'r', encoding='utf-8') as cadastro_file:
                content = cadastro_file.read()

            content = content.replace('{email}',login)
            content = content.replace('{senha}',senha)
            content = content.replace('{welcome_message}',welcome_message)

            self.wfile.write(content.encode('utf-8'))
            return
        
        elif self.path =='/turmas':
            try:
                with open(os.path.join(os.getcwd(),'cad_turma2.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404,"File not found")

        elif self.path =='/atividades':
                with open(os.path.join(os.getcwd(),'cad_atividades2.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
        
        elif self.path =='/turmas_professor':
                with open(os.path.join(os.getcwd(),'cad_login_turma.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))

        elif self.path =='/atividades_da_turma':
                with open(os.path.join(os.getcwd(),'cad_atividades_turma.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))

        else: 
            super().do_GET()

    def usuario_existente(self,login,senha):
        cursor = conexao.cursor()
        cursor.execute("SELECT senha FROM dados_login WHERE login = %s", (login,))
        resultado = cursor.fetchone()
        cursor.close()
                    
        if resultado:
            senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
            return senha_hash == resultado[0]
        
        return False
        
    def adicionar_usuario(self,login,senha,nome):
        cursor = conexao.cursor()

        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
        cursor.execute("INSERT INTO dados_login (login, senha, nome) VALUES (%s, %s, %s)", (login, senha_hash, nome))

        conexao.commit()

        cursor.close()
        
    def do_POST(self):
        if self.path =='/enviar_login':
            content_lenght = int(self.headers['Content-Length'])
            body = self.rfile.read(content_lenght).decode('utf-8')
            form_data = parse_qs(body)

            print('Email:', form_data.get('email',[''])[0])
            print('Senha:', form_data.get('senha',[''])[0])

            login = form_data.get('email',[''])[0]
            senha = form_data.get('senha',[''])[0]

            if self.usuario_existente(login,senha):
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                    mensagem = f'Usuário {login} logado com sucesso!'
                    self.wfile.write(mensagem.encode('utf-8'))
    
            else: 
                cursor = conexao.cursor()
                cursor.execute("SELECT login FROM dados_login WHERE login = %s", (login,))
                resultado = cursor.fetchone()

                if resultado:
                    self.send_response(302)
                    self.send_header('Location', '/login_failed')
                    self.end_headers()
                    cursor.close()
                    return
                
                else:
                    self.send_response(302)
                    self.send_header('Location', f'/cadastro?login={login}&senha={senha}')
                    self.end_headers()
                    cursor.close()
                    return
                          
        elif self.path.startswith('/confirmar_cadastro'):
            content_lenght = int(self.headers['Content-Length'])
            body = self.rfile.read(content_lenght).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            login = form_data.get('email',[''])[0]
            senha = form_data.get('senha',[''])[0]
            nome = form_data.get('nome',[''])[0]

            self.adicionar_usuario(login, senha, nome)

            with open(os.path.join(os.getcwd(),'dados_ok.html'), 'rb')as file:
                    content = file.read().decode('utf-8')

            content = content.replace('{login}', login)
            content = content.replace('{nome}', nome)

            self.send_response(200)
            self.send_header('Content-type','text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path =='/cad_turma':
            content_lenght = int(self.headers['Content-Length'])
            body = self.rfile.read(content_lenght).decode('utf-8')
            form_data = parse_qs(body)

            print('Dados do formulário:')
            print('Código:', form_data.get('codigo',[''])[0])
            print('Descrição:', form_data.get('descricao',[''])[0])

            codigo = form_data.get('codigo',[''])[0]
            descricao = form_data.get('descricao',[''])[0]

            with open('dados_turma.txt', 'r', encoding='utf-8') as file:
                    line = file.readlines()

            with open('dados_turma.txt', 'w', encoding='utf-8') as file:
                        line = f'{codigo};{descricao};\n'
                        file.write(line)

            with open(os.path.join(os.getcwd(),'dados_ok.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
            self.send_response(302)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path =='/cad_atividades':
            content_lenght = int(self.headers['Content-Length'])
            body = self.rfile.read(content_lenght).decode('utf-8')
            form_data = parse_qs(body)

            print('Dados do formulário:')
            print('Código:', form_data.get('codigo_atv',[''])[0])
            print('Descrição:', form_data.get('descricao_atv',[''])[0])

            codigo_atv = form_data.get('codigo_atv',[''])[0]
            descricao_atv = form_data.get('descricao_atv',[''])[0]

            with open('dados_atividades.txt', 'r', encoding='utf-8') as file:
                    line = file.readlines()

            with open('dados_atividades.txt', 'w', encoding='utf-8') as file:
                        line = f'{codigo_atv};{descricao_atv}\n'
                        file.write(line)

            with open(os.path.join(os.getcwd(),'dados_ok.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
            self.send_response(302)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path =='/cad_professor_turma':
            content_lenght = int(self.headers['Content-Length'])
            body = self.rfile.read(content_lenght).decode('utf-8')
            form_data = parse_qs(body)

            print('Dados do formulário:')
            print('E-mail:', form_data.get('email',[''])[0])
            print('Turma:', form_data.get('turma',[''])[0])

            email = form_data.get('email',[''])[0]
            turma = form_data.get('turma',[''])[0]

            with open('dados_login_turma.txt', 'r', encoding='utf-8') as file:
                    line = file.readlines()

            with open('dados_login_turma.txt', 'w', encoding='utf-8') as file:
                        line = f'{email};{turma}\n'
                        file.write(line)

            with open(os.path.join(os.getcwd(),'dados_ok.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
            self.send_response(302)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path =='/cadastro_atividade_turma':
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