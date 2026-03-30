from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_o_ifood'

# --- BANCO DE DADOS TEMPORÁRIO ---
pedidos_geral = []

# 🔥 IMAGENS DIRETO NA RAIZ DO STATIC
hamburgueres = [
    {"id": 1, "nome": "X-Burger", "preco": 15.0, "descricao": "Pão, carne e queijo",
     "imagem_url": "imagens.jpg"},
    {"id": 2, "nome": "X-Salada", "preco": 18.0, "descricao": "Alface, tomate e queijo",
     "imagem_url": "xsalada.jpg"},
    {"id": 3, "nome": "X-Bacon", "preco": 20.0, "descricao": "Com bacon crocante",
     "imagem_url": "xbacon.jpg"},
    {"id": 4, "nome": "X-Tudo", "preco": 25.0, "descricao": "Completo com tudo",
     "imagem_url": "xtudo.jpg"},
]

bebidas = [
    {"id": 1, "nome": "Refrigerante", "preco": 8.0, "descricao": "Lata 350ml",
     "imagem_url": "refri.jpg"},
    {"id": 2, "nome": "Suco Natural", "preco": 10.0, "descricao": "Diversos sabores",
     "imagem_url": "suco.jpg"},
]


@app.route('/')
def index():
    itens_carrinho = session.get('carrinho', [])
    return render_template('index.html',
                           hamburgueres=hamburgueres,
                           bebidas=bebidas,
                           carrinho=itens_carrinho)


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

    # 🔥 BLOQUEIA DUPLICAÇÃO
    if not itens:
        return redirect(url_for('index'))

    horario_agora = datetime.now().strftime('%d/%m/%Y %H:%M')

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

    # 🔥 LIMPA CARRINHO
    session.pop('carrinho', None)

    # 🔥 SALVA CONFIRMAÇÃO
    session['ultimo_pedido'] = {
        "nome": nome,
        "mesa": mesa,
        "horario": horario_agora
    }

    # 🔥 REDIRECT (anti-duplicação)
    return redirect(url_for('pedido_confirmado'))


# --- LOGIN ADMIN ---

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


# 🔥 UPLOAD AJUSTADO PARA /static DIRETO
@app.route('/adicionar_produto', methods=['POST'])
def adicionar_produto():
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    preco = request.form.get('preco')
    imagem = request.files['imagem']

    nome_arquivo = secure_filename(imagem.filename)

    caminho = os.path.join('static', nome_arquivo)
    imagem.save(caminho)

    novo_produto = {
        "id": len(hamburgueres) + 1,
        "nome": nome,
        "descricao": descricao,
        "preco": float(preco),
        "imagem_url": nome_arquivo  # 🔥 AGORA CORRETO
    }

    hamburgueres.append(novo_produto)

    return redirect(url_for('admin_painel'))
@app.route('/excluir_produto', methods=['POST'])
def excluir_produto():
    if not session.get('admin_logado'):
        return redirect(url_for('login'))

    id_p = int(request.form.get('id'))
    cat = request.form.get('categoria')

    lista = hamburgueres if cat == 'hamburguer' else bebidas

    for item in lista:
        if item['id'] == id_p:
            lista.remove(item)
            break

    return redirect(url_for('admin_painel'))
@app.route('/pedidos_json')
def pedidos_json():
    return {"pedidos": pedidos_geral}

@app.route('/pedido_confirmado')
def pedido_confirmado():
    pedido = session.get('ultimo_pedido', {})

    return render_template(
        'pedido_confirmado.html',
        nome=pedido.get('nome'),
        mesa=pedido.get('mesa'),
        horario=pedido.get('horario')
    )


if __name__ == '__main__':
    app.run(debug=True)
