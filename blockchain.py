import hashlib
import json
from time import time
import copy
import bitcoinlib # pip install bitcoin
from tabulate import tabulate
import requests

DIFFICULTY = 4 # Quantidade de zeros (em hex) iniciais no hash valido.

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.memPool = []
        self.nodes = set() # Conjunto para armazenar as urls dos nós registrados.
        self.createGenesisBlock()

    def createGenesisBlock(self):
        # Cria o bloco genêsis
        self.createBlock(previousHash='0'*64, nonce=0)
        self.mineProofOfWork(self.prevBlock) 

    def createBlock(self, nonce=0, previousHash=None):
        # Retorna um novo bloco criado e adicionado ao blockchain (ainda não minerado).
        if (previousHash == None):
            previousBlock = self.chain[-1]
            previousBlockCopy = copy.copy(previousBlock)
            previousBlockCopy.pop('transactions')

        block = {
            'index': len(self.chain) + 1,
            'timestamp': int(time()),
            'transactions': self.memPool,
            'merkleRoot': self.generateMerkleRoot(self.memPool),
            'nonce': nonce,
            'previousHash': previousHash or self.generateHash(previousBlockCopy),
        }

        self.memPool = []
        self.chain.append(block)
        return block

    def mineProofOfWork(self, prevBlock):
        # Retorna o nonce que satisfaz a dificuldade atual para o bloco passado como argumento.
        nonce = 0
        while self.isValidProof(prevBlock, nonce) is False:
            nonce += 1
        prevBlock['nonce'] = nonce
        return nonce

    def createTransaction(self, sender, recipient, amount, timestamp, privWifKey):
        # Cria uma nova transação, assinada pela chave privada WIF do remetente.
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'timestamp': timestamp
        }
 
        transaction['signature'] = self.sign(privWifKey, json.dumps(transaction, sort_keys=True))
        self.memPool.append(transaction)

        return transaction

    def isValidChain(self, chain):
        # Dado uma chain passada como parâmetro, faz toda a verificação se o blockchain é válido:
        # 1. PoW válido
        # 2. Transações assinadas e válidas
        # 3. Merkle Root válido

        for block in chain:
            # Verifica se a PoW do bloco é válida
            if (Blockchain.isValidProof(block, block['nonce'])):
                # Verifica se alguma transação é inválida
                for tx in block['transactions']:
                    txCopy = copy.copy(tx)
                    txCopy.pop('signature')
                    if (not Blockchain.verifySignature(tx['sender'], tx['signature'], json.dumps(txCopy, sort_keys=True))):
                        return False
                # Verifica se o merkle root é válido
                if (block['merkleRoot'] != Blockchain.generateMerkleRoot(block['transactions'])):
                    return False

        return True      

    def resolveConflicts(self):
        # Consulta todos os nós registrados, e verifica se algum outro nó tem um blockchain com mais PoW e válido. Em caso positivo,
        # substitui seu próprio chain.
        for nodeUrl in self.nodes:
            response = requests.get(nodeUrl + '/chain')
            nodeChain = response.json()['chain']
            if (self.isValidChain(nodeChain) and len(nodeChain) > len(self.chain)):
              # Verifica as transações do nó atual que não estão no nó vencedor e coloca elas no memory pool
              txSet = Blockchain.getTransactionsHashes(nodeChain)
              for block in self.chain:
                  for tx in block['transactions']:
                      if Blockchain.generateHash(tx) not in txSet:
                          self.memPool.append(tx)
              
              # Substitui o chain do nó atual
              self.chain = nodeChain

    @staticmethod
    def generateMerkleRoot(transactions):
        # Gera a Merkle Root de um bloco com as respectivas transações.
        branches = [ Blockchain.generateHash(t) for t in transactions]

        while (len(branches) > 1):
            if (len(branches) % 2) == 1:
                branches.append(branches[-1])
            branches = [Blockchain.generateHash(a + b) for (a, b) in zip(branches[0::2], branches[1::2])]
        
        merkleRoot = branches[0] if len(branches) else '0'*64

        return merkleRoot
    
    @staticmethod
    def isValidProof(block, nonce):
        # Retorna True caso o nonce satisfaça a dificuldade atual para o bloco passado como argumento.
        blockCopy = copy.copy(block)
        blockCopy['nonce'] = nonce
        hashResult = Blockchain.getBlockID(blockCopy)
        return hashResult[:DIFFICULTY] == '0' * DIFFICULTY 

    @staticmethod
    def generateHash(data):
        # Retorna o SHA256 do argumento passado.
        dataString = json.dumps(data, sort_keys=True)
        return hashlib.sha256(dataString.encode()).hexdigest()

    @staticmethod
    def getBlockID(block):
        # Retorna o ID (hash do cabeçalho) do bloco passado como argumento.
        blockHeader = copy.copy(block)
        blockHeader.pop('transactions')
        return Blockchain.generateHash(blockHeader)

    def printChain(self):
        # Imprime no console um formato verboso do blockchain.
        for block in self.chain:
            table = [
                ['ID', self.getBlockID(block)], 
                ['Índice', block['index']],
                ['Timestamp', block['timestamp']],
                ['Nonce', block['nonce']],
                ['Merkle Root', block['merkleRoot']],
                ['Hash do bloco anterior', block['previousHash']],
                ['Transações:', '']
            ]

            transactionsTable = []
            for t in block['transactions']:
                transactionsTable.append(['- Remetente', t['sender']])
                transactionsTable.append(['- Destinatário', t['recipient']])
                transactionsTable.append(['- Valor', t['amount']])
                transactionsTable.append(['- Timestamp', t['timestamp']])
                transactionsTable.append(['- Assinatura', t['signature']])
                transactionsTable.append(['', ''])

            table = table + transactionsTable
            print(tabulate(table))
            print('                                                       |                                                         ')

    @property
    def prevBlock(self):
        # Retorna o último bloco incluído no blockchain.
        return self.chain[-1]

    @staticmethod
    def getWifCompressedPrivateKey(private_key=None):
        # Retorna a chave privada no formato WIF-compressed da chave privada hex.
        if private_key is None:
            private_key = bitcoinlib.random_key()
        return bitcoinlib.encode_privkey(bitcoinlib.decode_privkey((private_key + '01'), 'hex'), 'wif')
        
    @staticmethod
    def getBitcoinAddressFromWifCompressed(wif_pkey):
        # Retorna o endereço Bitcoin da chave privada WIF-compressed.
        return bitcoinlib.pubtoaddr(bitcoinlib.privkey_to_pubkey(wif_pkey))

    @staticmethod
    def sign(wifCompressedPrivKey, message):
        # Retorna a assinatura digital da mensagem e a respectiva chave privada WIF-compressed.
        return bitcoinlib.ecdsa_sign(message, wifCompressedPrivKey)

    @staticmethod
    def verifySignature(address, signature, message):
        # Verifica se a assinatura é correspondente a mensagem e o endereço BTC.
        # Você pode verificar aqui também: https://tools.bitcoin.com/verify-message/
        return bitcoinlib.ecdsa_verify(message, signature, address)

    @staticmethod
    def getTransactionsHashes(chain):
        # Retorna o conjunto de hashes das transações da chain 
        txHashes = set()
        for block in chain:
            for tx in block['transactions']:
              txHashes.add(Blockchain.generateHash(tx))
        return txHashes
              
  