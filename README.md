# Madruguinha-Back

Este é o backend para o projeto Madruguinha, construído com Django e Django REST Framework.

## Começando

Estas instruções permitirão que você tenha uma cópia do projeto em funcionamento na sua máquina local para fins de desenvolvimento e teste.

### Pré-requisitos

- Python 3.8+
- Pip
- Virtualenv

### Instalação

1.  **Clone o repositório**
    ```bash
    git clone https://github.com/your-username/madruguinha-back.git
    cd madruguinha-back
    ```

2.  **Crie e ative um ambiente virtual**
    ```bash
    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instale as dependências**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente**

    Crie um arquivo `.env` no diretório raiz e adicione as variáveis de ambiente necessárias. Você pode usar o `.env.example` como modelo.
    ```env
    SECRET_KEY='sua-chave-secreta'
    DEBUG=True
    ```

5.  **Aplique as migrações do banco de dados**
    ```bash
    python manage.py migrate
    ```

6.  **Execute o servidor de desenvolvimento**
    ```bash
    python manage.py runserver
    ```
    O servidor estará rodando em `http://127.0.0.1:8000/`.

## Endpoints da API

- `/api/`: Raiz da API
- `/api/admin/`: Interface de administração
- ...

## Executando Testes

Para executar os testes automatizados para este sistema:

```bash
python manage.py test
```




