from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from database import (
    init_db, adicionar_animal, listar_animais, obter_animal, editar_animal, excluir_animal,
    adicionar_relatorio, listar_relatorios, adicionar_produto, listar_produtos,
    atualizar_produto, excluir_produto, adicionar_usuario, obter_usuario_por_email,
    get_db_connection
)
import csv
import io
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import bcrypt

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Substitua por uma chave segura

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

class User(UserMixin):
    def __init__(self, id, email, nome):
        self.id = id
        self.email = email
        self.nome = nome

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if usuario:
        return User(usuario['id'], usuario['email'], usuario['nome'])
    return None

# Inicializa o banco de dados
init_db()

@app.route('/')
@login_required
def principal():
    animais = listar_animais()
    produtos = listar_produtos()
    relatorios = listar_relatorios()
    
    total_animais = len(animais)
    estoque_baixo = len([p for p in produtos if p['quantidade'] <= 5])
    atendimentos_hoje = len([r for r in relatorios if r['data'] == datetime.now().strftime('%d/%m/%Y')])
    
    return render_template('principal.html', total_animais=total_animais, 
                         estoque_baixo=estoque_baixo, atendimentos_hoje=atendimentos_hoje, 
                         usuario=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        senha = request.form['senha'].encode('utf-8')
        usuario = obter_usuario_por_email(email)
        if usuario and bcrypt.checkpw(senha, usuario['senha'].encode('utf-8')):
            user = User(usuario['id'], usuario['email'], usuario['nome'])
            login_user(user)
            flash(f'Bem-vindo(a), {usuario["nome"]}!', 'success')
            return redirect(url_for('principal'))
        flash('E-mail ou senha inválidos.', 'error')
    return render_template('login.html')

@app.route('/cadastro_usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    if request.method == 'POST':
        try:
            nome = request.form['nome'].strip()
            email = request.form['email'].strip()
            senha = request.form['senha'].encode('utf-8')
            senha_hash = bcrypt.hashpw(senha, bcrypt.gensalt()).decode('utf-8')
            
            usuario = {'nome': nome, 'email': email, 'senha': senha_hash}
            adicionar_usuario(usuario)
            flash('Usuário cadastrado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Erro ao cadastrar usuário: {e}', 'error')
    return render_template('cadastro_usuario.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro():
    if request.method == 'POST':
        try:
            nome_dono = request.form['nome_dono'].strip()
            telefone = request.form['telefone'].strip()
            email = request.form.get('email', '').strip()
            nome = request.form['nome'].strip()
            tipo = request.form['tipo']
            idade = int(request.form['idade'])
            raca = request.form.get('raca', '').strip()
            descricao = request.form.get('descricao', '').strip()
            servicos = request.form.getlist('servicos')
            horario = request.form.get('horario', '')

            servicos_str = ', '.join(servicos)
            if 'Consulta' in servicos and horario:
                servicos_str += f' às {horario}'

            animal = {
                'nome_dono': nome_dono, 'telefone': telefone, 'email': email,
                'nome': nome, 'tipo': tipo, 'idade': idade, 'raca': raca,
                'descricao': descricao, 'servicos': servicos_str
            }
            adicionar_animal(animal)

            quantidade = sum(1 for _ in servicos)
            total = sum(50 if s == 'Banho' else 70 if s == 'Tosa' else 80 for s in servicos)

            relatorio = {
                'data': datetime.now().strftime('%d/%m/%Y'),
                'tipo': 'Atendimento',
                'quantidade': quantidade,
                'total': f'R$ {total:.2f}'
            }
            adicionar_relatorio(relatorio)

            flash('Animal cadastrado com sucesso!', 'success')
            return redirect(url_for('animais'))
        except ValueError as e:
            flash(f'Erro nos dados numéricos: {e}', 'error')
            return render_template('cadastro.html', erro=f'Erro nos dados numéricos: {e}')
        except Exception as e:
            flash(f'Erro ao cadastrar: {e}', 'error')
            return render_template('cadastro.html', erro=f'Erro ao cadastrar: {e}')
    return render_template('cadastro.html', usuario=current_user)

@app.route('/animais')
@login_required
def animais():
    animais = listar_animais()
    return render_template('animais.html', animais=animais, usuario=current_user)

@app.route('/detalhes/<int:id>')
@login_required
def detalhes(id):
    animal = obter_animal(id)
    if animal:
        return render_template('detalhes.html', animal=animal, usuario=current_user)
    return redirect(url_for('animais'))

@app.route('/relatorio')
@login_required
def relatorio():
    relatorios = listar_relatorios()
    return render_template('relatorio.html', relatorios=relatorios, usuario=current_user)

@app.route('/relatorio/exportar')
@login_required
def exportar_relatorio():
    relatorios = listar_relatorios()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Data', 'Tipo de Relatório', 'Quantidade', 'Total'])
    for r in relatorios:
        writer.writerow([r['data'], r['tipo'], r['quantidade'], r['total']])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv', as_attachment=True,
                     download_name='relatorio_petshop.csv')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    animal = obter_animal(id)
    if not animal:
        return redirect(url_for('animais'))
    
    if request.method == 'POST':
        try:
            nome_dono = request.form['nome_dono'].strip()
            telefone = request.form['telefone'].strip()
            email = request.form.get('email', '').strip()
            nome = request.form['nome'].strip()
            tipo = request.form['tipo']
            idade = int(request.form['idade'])
            raca = request.form.get('raca', '').strip()
            descricao = request.form.get('descricao', '').strip()
            servicos = request.form.getlist('servicos')
            horario = request.form.get('horario', '')

            servicos_str = ',  '.join(servicos)
            if 'Consulta' in servicos and horario:
                servicos_str += f'  {horario}'

            animal = {
                'nome_dono': nome_dono, 'telefone': telefone, 'email': email,
                'nome': nome, 'tipo': tipo, 'idade': idade, 'raca': raca,
                'descricao': descricao, 'servicos': servicos_str
            }
            editar_animal(id, animal)
            flash('Animal editado com sucesso!', 'success')
            return redirect(url_for('animais'))
        except ValueError as e:
            flash(f'Erro nos dados numéricos: {e}', 'error')
            return render_template('cadastro.html', erro=f'Erro nos dados numéricos: {e}', 
                                 animal=animal, id=id, usuario=current_user)
        except Exception as e:
            flash(f'Erro ao editar: {e}', 'error')
            return render_template('cadastro.html', erro=f'Erro ao editar: {e}', 
                                 animal=animal, id=id, usuario=current_user)
    return render_template('cadastro.html', animal=animal, id=id, usuario=current_user)

@app.route('/excluir/<int:id>')
@login_required
def excluir(id):
    excluir_animal(id)
    flash('Animal excluído com sucesso!', 'success')
    return redirect(url_for('animais'))

@app.route('/estoque', methods=['GET', 'POST'])
@login_required
def estoque():
    if request.method == 'POST':
        try:
            nome = request.form['nome'].strip()
            quantidade = int(request.form['quantidade'])
            preco = float(request.form['preco'])

            produto = {'nome': nome, 'quantidade': quantidade, 'preco': preco}
            adicionar_produto(produto)
            flash('Produto adicionado ao estoque!', 'success')
            return redirect(url_for('estoque'))
        except ValueError as e:
            produtos = listar_produtos()
            flash(f'Erro nos dados numéricos: {e}', 'error')
            return render_template('estoque.html', produtos=produtos, 
                                 erro=f'Erro nos dados numéricos: {e}', usuario=current_user)
        except Exception as e:
            produtos = listar_produtos()
            flash(f'Erro ao adicionar: {e}', 'error')
            return render_template('estoque.html', produtos=produtos, 
                                 erro=f'Erro ao adicionar: {e}', usuario=current_user)
    
    produtos = listar_produtos()
    return render_template('estoque.html', produtos=produtos, usuario=current_user)

@app.route('/estoque/atualizar/<int:id>', methods=['POST'])
@login_required
def atualizar_estoque(id):
    try:
        quantidade = int(request.form['quantidade'])
        atualizar_produto(id, quantidade)
        flash('Estoque atualizado com sucesso!', 'success')
        return redirect(url_for('estoque'))
    except ValueError as e:
        produtos = listar_produtos()
        flash(f'Erro na quantidade: {e}', 'error')
        return render_template('estoque.html', produtos=produtos, 
                             erro=f'Erro na quantidade: {e}', usuario=current_user)
    except Exception as e:
        produtos = listar_produtos()
        flash(f'Erro ao atualizar: {e}', 'error')
        return render_template('estoque.html', produtos=produtos, 
                             erro=f'Erro ao atualizar: {e}', usuario=current_user)

@app.route('/estoque/excluir/<int:id>')
@login_required
def excluir_produto_estoque(id):
    excluir_produto(id)
    flash('Produto excluído do estoque!', 'success')
    return redirect(url_for('estoque'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)