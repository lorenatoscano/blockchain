from logging import NullHandler
from flask import Flask, request
from blockchain import Blockchain, json

blockchain = Blockchain()

app = Flask(__name__)

#Arquivo usado para implementar os endpoints da API
""" 
[POST] /transactions/create para criar uma nova transação a ser incluída no próximo bloco. No corpo da requisicão HTTP, usando POST, inclua as informações necessárias para criação de uma nova transação.
[GET] /transactions/mempool para retornar a memory pool do nó.
[GET] /mine para informar o nó para criar e minerar um novo bloco. Ou seja, um nó que for requisitado a partir desse end-point deve pegar todas as transações incluídas em seu memory pool, montar um bloco e minera-lo.
[GET] /chain para retornar o blockchain completo daquele nó.
[POST] /nodes/register para aceitar uma lista de novos nós no formato de URLs. Note que já existe uma variável do tipo conjunto (set) chamado nodes para armazenar os nós registrados.
[GET] /nodes/resolve para executar o modelo de consenso, resolvendo conflitos e garantindo que contém a cadeia de blocos correta. Basicamente o que deve ser feito pelo nó é solicitar a todos os seus nós registrados os seus respectivos blockchains. Então deve-se conferir se o blockchain é válido, e, se for maior (mais longo) que o atual, deve substitui-lo.
Para auxiliar no desenvolvimento do consenso, implemente os métodos isValidChain() e resolveConflicts(). As assinaturas e a descrição já estão no código exemplo. 
"""


@app.route('/transactions/create', methods=['POST'])
def create_transaction():
    transactionData = request.json
    blockchain.createTransaction(
      transactionData['sender'],
      transactionData['recipient'],
      transactionData['amount'],
      transactionData['timestamp'],
      transactionData['privWifKey'],
    )
    return json.dumps(transactionData)

@app.route('/transactions/mempool', methods=['GET'])
def mempool_return():
    return { 'memPool': blockchain.memPool }

@app.route('/mine', methods=['GET'])
def mine():
    blockchain.createBlock()
    blockchain.mineProofOfWork(blockchain.prevBlock)
    return blockchain.prevBlock

@app.route('/chain', methods=['GET'])
def chain():
    return { 'chain': blockchain.chain }

@app.route('/nodes/register', methods=['POST'])
def register_node():
    nodesData = request.json
    for url in nodesData['urls']:
      blockchain.nodes.add(url)
    return { 'nodeUrls': list(blockchain.nodes) }

@app.route('/nodes/resolve', methods=['GET'])
def resolve_node():
    blockchain.resolveConflicts()
    return { 'chain': blockchain.chain }

if __name__ == '__main__':
    app.run(port=5001)