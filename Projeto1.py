from fastapi import FastAPI
from typing import List
from pydantic import BaseModel

app = FastAPI()

OK = "OK"
FALHA = "FALHA"

# Classe representando os dados do endereço do cliente
class Endereco(BaseModel):
    rua: str
    cep: str
    cidade: str
    estado: str

# Classe representando os dados do cliente
class Usuario(BaseModel):
    id: int
    nome: str
    email: str
    senha: str

# Classe representando a lista de endereços de um cliente
class ListaDeEnderecosDoUsuario(BaseModel):
    usuario: Usuario
    enderecos: List[Endereco] = []

# Classe representando os dados do produto
class Produto(BaseModel):
    id_produto: int
    nome: str
    descricao: str
    preco: float

# Classe representando o carrinho de compras de um cliente com uma lista de produtos
class CarrinhoDeCompras(BaseModel):
    id_usuario: int
    id_produtos: List[Produto] = [] # precisa associar a quantidade List[ProdutoCarrinho] = [] e Produto carrinho já vier com a qtd
    preco_total: float
    quantidade_de_produtos: int


# Usuários

db_usuarios = []

@app.post("/usuario")
async def criar_usuarios(novo_usuario: Usuario):
    print(novo_usuario.dict())
    novo_usuario = regras_usuario_cadastrar(novo_usuario.dict())
    return novo_usuario

def regras_usuario_cadastrar(novo_usuario):
    novo_usuario = persistencia_usuario_salvar(novo_usuario)
    return novo_usuario

def persistencia_usuario_salvar(novo_usuario):
    db_usuarios.append(novo_usuario)
    return novo_usuario

@app.get("/usuario")
def rota_usuario_pesquisar_todos(nome: str = None):
    if nome:
        return regras_usuario_pesquisar_pelo_nome(nome)
    return regras_usuario_pesquisar_todos()

def regras_usuario_pesquisar_todos():
    return persistencia_usuario_pesquisar_todos()

def persistencia_usuario_pesquisar_todos():
    lista_usuarios = list(db_usuarios)
    return lista_usuarios

def regras_usuario_pesquisar_pelo_nome(nome):
    return persistencia_pesquisar_pelo_nome(nome)

def persistencia_pesquisar_pelo_nome(nome: str):
    for usuario in db_usuarios:
        primeiro_nome = usuario.get('nome', "").split(' ')
        if primeiro_nome[0].lower() == nome.lower():
            return usuario

@app.get("/usuario/{id_usuario}")
async def rota_usuario_pesquisar_pelo_id(id_usuario:int):
    print("Consulta pelo id: ", id_usuario)
    return regras_usuario_pesquisar_pelo_id(id_usuario)

def regras_usuario_pesquisar_pelo_id(id_usuario):
    return persistencia_pesquisar_pelo_id(id_usuario)

def persistencia_pesquisar_pelo_id(id_usuario):
    id_procurado = None
    for usuario in db_usuarios:
        if usuario.get('id', None) == id_usuario:
            id_procurado = usuario
            break
    return id_procurado

@app.delete("/usuario/{id}")
async def deletar_usuario(id:int):
    return regras_deletar_usuario_pelo_id(id)

def regras_deletar_usuario_pelo_id(id):
    return persistencia_deletar_pelo_id(id)

def persistencia_deletar_pelo_id(id: int):
    for chave, usuario in enumerate(db_usuarios):
        if usuario['id'] == id:
            del db_usuarios[chave]
            return OK
    return FALHA

@app.get("/usuarios/email")
async def retornar_emails(dominio_email: str):
    lista_emails = []
    usuarios = persistencia_usuario_pesquisar_todos()
    for usuario in usuarios:
        email = usuario.get('email', None)
        dominio = email.split('@')[1]
        if dominio == dominio_email:
            lista_emails.append(email)
    return lista_emails

#Endereços

db_enderecos = []

@app.post("/endereco/{id_usuario}")
async def criar_endereco(endereco: Endereco, id_usuario: int):
    print(novo_endereco.dict())
    novo_endereco = regras_endereco_cadastrar(novo_endereco.dict())
    return novo_endereco

def regras_endereco_cadastrar(novo_endereco):
    novo_endereco = persistencia_endereco_salvar(novo_endereco)
    return novo_endereco

def persistencia_endereco_salvar(novo_endereco):
    id_novo_endereco = len(db_enderecos) + 1
    novo_endereco["id_novo_endereco"] = id_novo_endereco
    db_enderecos.append(novo_endereco)
    return novo_endereco

@app.post("/usuario/{id_usuario}/endereco")
async def criar_endereco(endereco: Endereco, id_usuario: int):
    usuario = persistencia_pesquisar_pelo_id(id_usuario)
    if not usuario: 
        return FALHA
    endereco_db = endereco.dict()
    endereco_db["id_usuario"] = usuario.get('id')
    endereco_db["id"] = len(db_enderecos) + 1
    db_enderecos.append(endereco_db)
    return OK

@app.get("/usuario/{id_usuario}/endereco")
async def listar_endereco(id_usuario: int):
    return db_enderecos

@app.delete("/usuario/{id_usuario}/endereco/{endereco_id}")
async def deletar_endereco(endereco_id: int, id_usuario: int):
    for chave, endereco in enumerate(db_enderecos):
        if endereco['id'] == endereco_id and endereco['id_usuario'] == id_usuario:
            del db_enderecos[chave]
            return OK
    return FALHA

# Produtos

db_produtos = []

@app.post("/produto")
async def criar_produto(produto: Produto):
    print(produto.dict())
    produto = regras_produto_cadastrar(produto.dict())
    return produto

def regras_produto_cadastrar(produto):
    produto = persistencia_produto_salvar(produto)
    return produto

def persistencia_produto_salvar(produto):
    db_produtos.append(produto)
    return produto

@app.delete("/produto/{id_produto}")
async def deletar_produto(id_produto:int):
    return regras_deletar_produto(id_produto)

def regras_deletar_produto(id_produto):
    return persistencia_deletar_produto(id_produto)

def persistencia_deletar_produto(id_produto):
    for chave, produto in enumerate(db_produtos):
        if produto['id_produto'] == id_produto:
            del db_produtos[chave]
            return OK
    return FALHA

@app.get("/produto/{id_produto}")
async def rota_produto_pesquisar_pelo_id(id_produto:int):
    print("Consulta pelo id: ", id_produto)
    return regras_produto_pesquisar_pelo_id(id_produto)

def regras_produto_pesquisar_pelo_id(id_produto):
    return persistencia_pesquisar_produto_pelo_id(id_produto)

def persistencia_pesquisar_produto_pelo_id(id_produto):
    id_procurado = None
    for produto in db_produtos:
        if produto.get('id_produto', None) == id_produto:
            id_procurado = produto
            break
    return id_procurado

# Carrinho de Compras

db_carrinhos = []

def persistencia_pesquisar_carrinho_id_usuario(id_usuario):
    for carrinho in db_carrinhos:
        if carrinho.get('id_usuario', None) == id_usuario:
            return carrinho
    return None

@app.post("/usuario/{id_usuario}/carrinho")
async def criar_carrinho(id_produto: int, id_usuario: int):
    usuario = persistencia_pesquisar_pelo_id(id_usuario)
    if not usuario: 
        return FALHA
    produto = persistencia_pesquisar_produto_pelo_id(id_produto)
    if not produto: 
        return FALHA
    carrinho = persistencia_pesquisar_carrinho_id_usuario(id_usuario)
    if carrinho:
        carrinho["produtos"].append(produto)
    else:
        carrinho = {
            "id_usuario": id_usuario,
            "produtos": [produto]
        }
        db_carrinhos.append(carrinho)
    return db_carrinhos

@app.delete("/usuario/{id_usuario}/carrinho")
async def deletar_produto(id_produto: int, id_usuario: int):
    usuario = persistencia_pesquisar_pelo_id(id_usuario)
    if not usuario: 
        return FALHA
    produto = persistencia_pesquisar_produto_pelo_id(id_produto)
    if not produto: 
        return FALHA
    for carrinho in db_carrinhos:
        if carrinho.get('id_usuario', None) == id_usuario:
            produtos = carrinho.get('produtos', None)
            if produtos == None:
                return FALHA
            index = 0
            for produto in produtos:
                if produto.get("id_produto", -1) == id_produto:
                    produtos.pop(index)
                index += 1
    return db_carrinhos
        
@app.get("/carrinho/{id_usuario}")
async def retornar_total_carrinho(id_usuario: int):
    carrinho = persistencia_pesquisar_carrinho_id_usuario(id_usuario)
    if not carrinho:
        return FALHA
    numero_itens = 0
    valor_total = 0.0
    for produto in carrinho.get("produtos", []):
        numero_itens += 1
        valor_total += float(produto.get("preco", 0.0))
    return {
        "numero_itens": numero_itens,
        "valor_total": valor_total
    }

@app.delete("/carrinho/{id_usuario}")
async def deletar_carrinho(id_usuario: int):
    carrinho = persistencia_pesquisar_carrinho_id_usuario(id_usuario)
    if not carrinho:
        return FALHA
    for carrinho in db_carrinhos:
        carrinho.clear()
        return db_carrinhos
    return FALHA

@app.get("/saudacao")
async def boas_vindas():
    site = "Seja bem-vindo(a). Estamos felizes por ter você conosco!"
    return site