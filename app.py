from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_o_ifood'

# --- BANCO DE DADOS TEMPORÁRIO ---
pedidos_geral = []

hamburgueres = [
    {"id": 1, "nome": "X-Burger", "preco": 15.0, "descricao": "Pão, carne e queijo"},
    {"id": 2, "nome": "X-Salada", "preco": 18.0, "descricao": "Alface, tomate e queijo"},
    {"id": 3, "nome": "X-Bacon", "preco": 20.0, "descricao": "Com bacon crocante"},
    {"id": 4, "nome": "X-Tudo", "preco": 25.0, "descricao": "Completo com tudo"},
    {"id": 5, "nome": "X-Frango", "preco": 17.0, "descricao": "Frango grelhado"},
    {"id": 6, "nome": "X-Egg", "preco": 19.0, "descricao": "Com ovo"},
    {"id": 7, "nome": "X-Calabresa", "preco": 22.0, "descricao": "Com calabresa"}
]

bebidas = [
    {"id": 1, "nome": "Refrigerante", "preco": 8.0, "descricao": "Lata 350ml"},
    {"id": 2, "nome": "Suco Natural", "preco": 10.0, "descricao": "Diversos sabores"},
    {"id": 3, "nome": "Água", "preco": 5.0, "descricao": "Sem gás"},
    {"id": 4, "nome": "Água com gás", "preco": 6.0, "descricao": "Gelada"},
    {"id": 5, "nome": "Milkshake", "preco": 12.0, "descricao": "Chocolate, morango ou baunilha"}
]


@app.route('/')
def index():
    itens_carrinho = session.get('carrinho', [])
    return render_template('index.html', hamburgueres=hamburgueres, bebidas=bebidas, carrinho=itens_carrinho)


@app.route('/adicionar', methods=['POST'])
def adicionar_carrinho():
    if 'carrinho' not in session:
        session['carrinho'] = []

    item = {
        'nome': request.form.get('nome'),
        'preco': request.form.get('preco'),
        'observacao': request.form.get('observacao')
    }

    lista = session['carrinho']
    lista.append(item)
    session['carrinho'] = lista
    session.modified = True
    return redirect(url_for('index'))


@app.route('/carrinho')
def mostrar_carrinho():
    itens = session.get('carrinho', [])
    return render_template('pedido.html', carrinho=itens)


@app.route('/limpar')
def limpar_carrinho():
    session.pop('carrinho', None)
    return redirect(url_for('index'))


@app.route('/confirmar', methods=['POST'])
def confirmar_pedido():
    nome = request.form.get('cliente_nome')
    mesa = request.form.get('mesa')
    itens = session.get('carrinho', [])

    horario_agora = datetime.now().strftime('%d/%m/%Y %H:%M')

    if itens:
        total_pedido = sum(float(item['preco']) for item in itens)

        novo_pedido = {
            "cliente": nome,
            "mesa": mesa,
            "itens": itens,
            "total": total_pedido,
            "horario": horario_agora,
            "status": "Pendente"
        }

        pedidos_geral.append(novo_pedido)
        session.pop('carrinho', None)

    return render_template('pedido_confirmado.html', nome=nome, mesa=mesa, horario=horario_agora)


# --- ÁREA ADMINISTRATIVA ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        if usuario == 'restaurante' and senha == '*1234*':
            session['admin_logado'] = True
            return redirect(url_for('admin_painel'))
        else:
            return "Acesso negado!", 403

    return render_template('login.html')


@app.route('/admin')
def admin_painel():
    if not session.get('admin_logado'):
        return redirect(url_for('login'))

    # CORREÇÃO: Passando as listas para o template aparecer os produtos!
    return render_template('admin.html',
                           pedidos=pedidos_geral,
                           hamburgueres=hamburgueres,
                           bebidas=bebidas)


@app.route('/admin/limpar')
def limpar_pedidos_admin():
    pedidos_geral.clear()
    return redirect(url_for('admin_painel'))


@app.route('/admin/atualizar_produto', methods=['POST'])
def atualizar_produto():
    if not session.get('admin_logado'):
        return redirect(url_for('login'))

    # CORREÇÃO: Removido o render_template daqui (esta rota apenas processa dados)
    id_p = int(request.form.get('id'))
    nova_desc = request.form.get('descricao')
    novo_preco = float(request.form.get('preco'))
    cat = request.form.get('categoria')

    lista = hamburgueres if cat == 'hamburguer' else bebidas

    for item in lista:
        if item['id'] == id_p:
            item['descricao'] = nova_desc
            item['preco'] = novo_preco
            break

    return redirect(url_for('admin_painel'))



if __name__ == '__main__':
    app.run(debug=True)