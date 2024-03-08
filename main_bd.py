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

    def carrega_turmas_professor(self,login):
         cursor = conexao.cursor()
         cursor.execute("SELECT id_professor, nome FROM dados_login WHERE login = %s", (login,))
         resultado = cursor.fetchone()
         cursor.close()

         id_professor = resultado[0]

         cursor = conexao.cursor()
         cursor.execute(
              "SELECT turmas.id_turma, turmas.descricao FROM turmas_professor "
              "INNER JOIN turmas ON turmas_professor.id_turma WHERE turmas_professor.id_professor = %s",
              (id_professor,))
         turmas = cursor.fetchall()
         cursor.close()
         
         linhas_tabela = ""
         for turma in turmas: 
              id_turma = turma[0]
              descricao_turma = turma[1]
              link_atividade = "<a href='//atividades_da_turma?id={}'><i class='fas fa-pencil-alt'></i></a>".format(id_turma)
              linha = "<tr><td style = 'text-align: center'>{}</td><td>{}</td><td style='text-align: center'>{}</td></tr>".format(id_turma, descricao_turma, link_atividade)
              linhas_tabela += linha

         cursor = conexao.cursor()
         cursor.execute("SELECT id_turma, descricao FROM turmas")
         turmas = cursor.fetchall()
         cursor.close()
              

         opcoes_caixa_selecao = ""
         for turma in turmas:
                   opcoes_caixa_selecao += "<option value='{}'>{}</option>".format(turma[0], turma[1])

         with open(os.path.join(os.getcwd(), 'cad_login_turma.html'), 'r', encoding='utf-8') as cad_turma_file:
                   content = cad_turma_file.read()

                   content = content.replace('{nome_professor}', resultado[1])
                   content = content.replace('{id_professor}', str(id_professor))
                   content = content.replace('{login}', str(login))

                   content = content.replace('<!-- Tabela com linhas zebradas -->', linhas_tabela)
                   print('cheguei ', opcoes_caixa_selecao)
                   content = content.replace('<!-- Opções com caixa de seleção serão inseridas aqui -->', opcoes_caixa_selecao)

                   self.send_response(200)
                   self.send_header('Content-type', 'text/html; charset=utf-8')
                   self.end_headers()

                   self.wfile.write(content.encode('utf-8'))

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
                 self.carrega_turmas_professor(login)
    
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

            descricao = form_data.get('descricao',[''])[0]

            cursor = conexao.cursor()
            cursor.execute("INSERT INTO turmas (descricao) VALUES (%s)", (descricao,))
            conexao.commit()
            cursor.close()

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

            descricao_atv = form_data.get('descricao_atv',[''])[0]

            cursor = conexao.cursor()
            cursor.execute("INSERT INTO atividades (descricao) VALUES (%s)", (descricao_atv,))
            conexao.commit()
            cursor.close()

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


            id_turma = form_data.get('id_turma',[''])[0]
            id_professor = form_data.get('id_professor',[''])[0]

            cursor = conexao.cursor()
            cursor.execute("INSERT INTO turmas_professor (id_turma, id_professor) VALUES (%s, %s)", (id_turma, id_professor))
            conexao.commit()
            cursor.close()

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

            id_atividade = form_data.get('id_atividade',[''])[0]
            descricao_atv = form_data.get('descricao_atv',[''])[0]

            cursor = conexao.cursor()
            cursor.execute("INSERT INTO atividades_turma (id_atividade, descricao_atv) VALUES (%s, %s)", (id_atividade, descricao_atv))
            conexao.commit()
            cursor.close()

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