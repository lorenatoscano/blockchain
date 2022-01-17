## Sobre
Compilado das atividades semanais da disciplina de Tópicos Especiais em Internet das Coisas D (Blockchain) do BTI, que resultaram na implementação de um blockchain em Python. Alguns métodos foram fornecidos pelo professor [Danilo Curvelo](https://github.com/danilocurvelo) e outros foram implementados durante as atividades.

A API de acesso ao blockchain foi construída em dupla com [João Vitor](https://github.com/joaovdxavier), utilizando o *framework* [Flask](https://palletsprojects.com/p/flask/), e possui os endpoints:

- **[POST]** `/transactions/create` para criar uma nova transação a ser incluída no próximo bloco. No corpo da requisicão HTTP, usando POST, inclua as informações necessárias para criação de uma nova transação. Exemplo:
  ```json
  {
    "sender": "19sXoSbfcQD9K66f5hwP5vLwsaRyKLPgXF",
    "recipient": "1MxTkeEP2PmHSMze5tUZ1hAV3YTKu2Gh1N", 
    "amount": 0.1, 
    "timestamp": 1637953954,
    "privWifKey": "L1US57sChKZeyXrev9q7tFm2dgA2ktJe2NP3xzXRv6wizom5MN1U"
  }
  ```
- **[GET]** `/transactions/mempool` para retornar a *memory pool* do nó.
- **[GET]** `/mine` para informar o nó para criar e minerar um novo bloco. Ou seja, um nó que for requisitado a partir desse end-point deve pegar todas as transações incluídas em seu memory pool, montar um bloco e minera-lo.
- **[GET]** `/chain` para retornar o blockchain completo daquele nó.
- **[POST]** `/nodes/register` para aceitar uma lista de novos nós no formato de URLs. Exemplo:
  ```json
  {
    "urls": [ "http://127.0.0.1:5002"]
  }
  ```
- **[GET]** `/nodes/resolve` para executar o modelo de consenso, resolvendo conflitos e garantindo que contém a cadeia de blocos correta. Basicamente o que deve ser feito pelo nó é solicitar a todos os seus nós registrados os seus respectivos blockchains. Então deve-se conferir se o blockchain é válido, e, se for maior (mais longo) que o atual, deve substitui-lo.

## Como rodar?

```
pip install -r requirements.txt
python blockchain_api.py
```
Acesse a API em `http://127.0.0.1:5001/[endpoint]`. Se quiser subir outro nó em uma porta diferente, altere a última linha do arquivo `blockchain_api.py` e execute o programa novamente.

## Licença
[MIT](https://choosealicense.com/licenses/mit/)