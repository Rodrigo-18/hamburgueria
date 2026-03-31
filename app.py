from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_o_ifood'

# --- BANCO DE DADOS TEMPORÁRIO ---
pedidos_geral = []

# --- PRODUTOS ---
hamburgueres = [
    {"id": 1, "nome": "Pastel de Carne", "preco": 8.0, "descricao": "Pastel frito de Carne", "imagem_url": "pastel_de_carne.jpg"},
    {"id": 2, "nome": "Coxinha de Frango", "preco": 8.0, "descricao": "Coxinha frita de Frango", "imagem_url": "coxinha.jpg"},
    {"id": 3, "nome": "Bolinha de Presunto e Queijo", "preco": 8.0, "descricao": "Salgado frito de presunto e queijo", "imagem_url": "bolinha.jpg"},
    {"id": 4, "nome": "Bolinho de Aimpim", "preco": 8.0, "descricao": "Salgado Frito de Aimpim", "imagem_url": "bolinho_aimpim.jpg"},
    {"id": 5, "nome": "Pão de Queijo", "preco": 8.0, "descricao": "Pão de Queijo", "imagem_url": "pao_de_queijo.jpg"},
    {"id": 6, "nome": "Pastel de Frango", "preco": 10.0, "descricao": "Pastel Assado de Frango", "imagem_url": "pastel_frango.jpg"},
    {"id": 7, "nome": "Hambúrguer assado", "preco": 10.0, "descricao": "Hambúrguer assado", "imagem_url": "hamburguer.jpg"},
]

bebidas = [
    {"id": 1, "nome": "Cerveja", "preco": 10.0, "descricao": "Long neck 330ml", "imagem_url": "bebida.jpg"},
    {"id": 2, "nome": "Coca-Cola", "preco": 6.0, "descricao": "Original ou Zero", "imagem_url": "coca_cola.jpg"},
    {"id": 3, "nome": "Fanta", "preco": 6.0, "descricao": "Uva, Laranja", "imagem_url": "fanta.jpg"},
    {"id": 4, "nome": "Suco Del Valle", "preco": 6.0, "descricao": "Manga, Uva", "imagem_url": "valle.jpg"},
    {"id": 5, "nome": "Água de Coco", "preco": 6.0, "descricao": "330ml", "imagem_url": "coco.jpg"},
    {"id": 6, "nome": "Água", "preco": 3.0, "descricao": "Sem gás", "imagem_url": "agua.jpg"},
    {"id": 7, "nome": "Água com Gás", "preco": 4.0, "descricao": "Com gás", "imagem_url": "agua_gas.jpg"},
    {"id": 8, "nome": "Toddynho", "preco": 4.0, "descricao": "200ml", "imagem_url": "toddynho.jpg"},
    {"id": 9, "nome": "Red Bull", "preco": 12.0, "descricao": "250ml", "imagem_url": "bull.jpg"},
]

doces = [
    {"id": 1, "nome": "Talento", "preco": 12.0, "descricao": "Chocolate 85g", "imagem_url": "talento.jpg"},
    {"id": 2, "nome": "Palha Italiana", "preco": 6.0, "descricao": "", "imagem_url": "palha.jpg"},
    {"id": 3, "nome": "Cocada", "preco": 6.0, "descricao": "", "imagem_url": "cocada.jpg"},
    {"id": 4, "nome": "Amendoim Doce", "preco": 6.0, "descricao": "", "imagem_url": "amendoim.jpg"},
    {"id": 5, "nome": "Snickers", "preco": 6.0, "descricao": "", "imagem_url": "snickers.jpg"},
    {"id": 6, "nome": "Doces Diversos", "preco": 3.0, "descricao": "Mentos, Trident e Halls", "imagem_url": "bala.jpg"},
]

# 🔥 CATEGORIAS CENTRALIZADAS
categorias = {
    "hamburguer": hamburgueres,
    "bebida": bebidas,
    "doce": doces
}

# --- ROTAS ---

@app.route('/')
def index():
    return render_template(
        'index.html',
        hamburgueres=hamburgueres,
        bebidas=bebidas,
        doces=doces,
        carrinho=session.get('carrinho', [])
    )

@app.route('/adicionar', methods=['POST'])
def adicionar_carrinho():
    if 'carrinho' not in session:
        session['carrinho'] = []

    item = {
        'nome': request.form.get('nome'),
        'preco': request.form.get('preco'),
        'observacao': request.form.get('observacao')
    }

    session['carrinho'].append(item)
    session.modified = True

    return redirect(url_for('index'))

@app.route('/carrinho')
def mostrar_carrinho():
    return render_template('pedido.html', carrinho=session.get('carrinho', []))

@app.route('/limpar')
def limpar_carrinho():
    session.pop('carrinho', None)
    return redirect(url_for('index'))

@app.route('/confirmar', methods=['POST'])
def confirmar_pedido():
    itens = session.get('carrinho', [])

    if not itens:
        return redirect(url_for('index'))

    nome = request.form.get('cliente_nome')
    mesa = request.form.get('mesa')

    horario = datetime.now().strftime('%d/%m/%Y %H:%M')
    total = sum(float(item['preco']) for item in itens)

    pedidos_geral.append({
        "cliente": nome,
        "mesa": mesa,
        "itens": itens,
        "total": total,
        "horario": horario,
        "status": "Pendente"
    })

    session.pop('carrinho', None)

    session['ultimo_pedido'] = {
        "nome": nome,
        "mesa": mesa,
        "horario": horario
    }

    return redirect(url_for('pedido_confirmado'))

@app.route('/pedido_confirmado')
def pedido_confirmado():
    pedido = session.get('ultimo_pedido', {})
    return render_template('pedido_confirmado.html',
                           nome=pedido.get('nome'),
                           mesa=pedido.get('mesa'),
                           horario=pedido.get('horario'))

# --- ADMIN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('usuario') == 'restaurante' and request.form.get('senha') == '*1234*':
            session['admin_logado'] = True
            return redirect(url_for('admin_painel'))
        return "Acesso negado!", 403

    return render_template('login.html')

@app.route('/admin')
def admin_painel():
    if not session.get('admin_logado'):
        return redirect(url_for('login'))

    return render_template('admin.html',
                           pedidos=pedidos_geral,
                           hamburgueres=hamburgueres,
                           bebidas=bebidas,
                           doces=doces)

@app.route('/admin/limpar')
def limpar_pedidos_admin():
    pedidos_geral.clear()
    return redirect(url_for('admin_painel'))

@app.route('/admin/atualizar_produto', methods=['POST'])
def atualizar_produto():
    cat = request.form.get('categoria')
    lista = categorias.get(cat, [])

    for item in lista:
        if item['id'] == int(request.form.get('id')):
            item['descricao'] = request.form.get('descricao')
            item['preco'] = float(request.form.get('preco'))
            break

    return redirect(url_for('admin_painel'))

@app.route('/excluir_produto', methods=['POST'])
def excluir_produto():
    cat = request.form.get('categoria')
    lista = categorias.get(cat, [])

    for item in lista:
        if item['id'] == int(request.form.get('id')):
            lista.remove(item)
            break

    return redirect(url_for('admin_painel'))

@app.route('/adicionar_produto', methods=['POST'])
def adicionar_produto():
    categoria = request.form.get('categoria')
    lista = categorias.get(categoria, [])

    imagem = request.files['imagem']
    nome_arquivo = secure_filename(imagem.filename)
    imagem.save(os.path.join('static', nome_arquivo))

    lista.append({
        "id": len(lista) + 1,
        "nome": request.form.get('nome'),
        "descricao": request.form.get('descricao'),
        "preco": float(request.form.get('preco')),
        "imagem_url": nome_arquivo
    })

    return redirect(url_for('admin_painel'))

# --- API ---

@app.route('/pedidos_json')
def pedidos_json():
    return {"pedidos": pedidos_geral}

@app.route('/atender/<int:index>')
def atender_pedido(index):
    if 0 <= index < len(pedidos_geral):
        pedidos_geral[index]['status'] = 'Atendido'
    return '', 204

# --- RUN ---
if __name__ == '__main__':
    app.run(debug=True)