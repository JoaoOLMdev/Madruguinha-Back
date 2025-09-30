# Documentação da API - Madruguinha Services

API RESTful desenvolvida para o backend do projeto Madruguinha Services, uma plataforma para conectar prestadores de serviço a clientes.

Esta API permite o gerenciamento de usuários, prestadores, tipos de serviços e solicitações de serviço.

## Tecnologias Utilizadas

-   **Linguagem:** Python 3.12
-   **Framework:** Django 5.2
-   **API:** Django REST Framework (DRF)
-   **Autenticação:** Simple JWT (JSON Web Tokens)
-   **Banco de Dados:** PostgreSQL (via Neon DB)

## Configuração do Ambiente de Desenvolvimento

1.  **Clone o repositório:**
    ```bash
    git clone [link-para-seu-repositorio]
    cd madruguinha-back
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    Crie um arquivo `.env` na raiz do projeto e adicione as configurações necessárias:
    ```ini
    SECRET_KEY=sua-chave-secreta-super-dificil
    DATABASE_URL=postgres://user:password@host:port/dbname
    DEBUG=True
    ```

5.  **Execute as migrações do banco de dados:**
    ```bash
    python manage.py migrate
    ```

6.  **Crie um superusuário (para acesso ao Admin):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```
    A API estará disponível em `http://127.0.0.1:8000/`.

## Autenticação

A API utiliza JWT (JSON Web Token) para autenticação. Para acessar endpoints protegidos, você deve primeiro obter um token de acesso e incluí-lo no cabeçalho de todas as requisições subsequentes.

### 1. Obter Token de Acesso

Faça uma requisição `POST` para `/api/token/` com suas credenciais de usuário.

-   **Endpoint:** `POST /api/token/`
-   **Corpo da Requisição:**
    ```json
    {
        "username": "seu_usuario",
        "password": "sua_senha"
    }
    ```
-   **Resposta de Sucesso (200 OK):**
    ```json
    {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```

### 2. Utilizando o Token

Em todas as requisições para endpoints protegidos, adicione o seguinte cabeçalho:

`Authorization: Bearer <seu_access_token>`

## Endpoints da API

A URL base para todos os endpoints é `http://127.0.0.1:8000/api/`.

### Usuários (`/users/`)

Gerenciamento de contas de usuário.

| Método | URL     | Descrição                      | Permissão       | Corpo da Requisição (Exemplo)                                                                                             |
| :----- | :------ | :----------------------------- | :-------------- | :------------------------------------------------------------------------------------------------------------------------ |
| `POST` | `/`     | Registra um novo usuário.      | Público         | `{ "username": "...", "email": "...", "password": "...", "first_name": "...", "last_name": "...", "endereco": "..." }`      |
| `GET`  | `/`     | Lista todos os usuários.       | Autenticado     | N/A                                                                                                                       |
| `GET`  | `/{id}/` | Detalha um usuário.            | Autenticado     | N/A                                                                                                                       |
| `PUT`  | `/{id}/` | Atualiza um usuário.           | Dono da conta\* | `{ "first_name": "...", "last_name": "...", "endereco": "..." }`                                                          |
| `PATCH` | `/{id}/` | Atualiza parcialmente um usuário. | Dono da conta\* | `{ "endereco": "Nova Rua, 123" }`                                                                                         |

\*Nota: A permissão de dono da conta precisa ser implementada com permissões customizadas.

### Tipos de Serviço (`/service-type/`)

Gerenciamento das categorias de serviços disponíveis na plataforma.

| Método   | URL     | Descrição                     | Permissão           | Corpo da Requisição (Exemplo)     |
| :------- | :------ | :---------------------------- | :------------------ | :-------------------------------- |
| `GET`    | `/`     | Lista todos os tipos de serviço. | Público             | N/A                               |
| `POST`   | `/`     | Cria um novo tipo de serviço.   | Autenticado (Admin) | `{ "nome": "Eletricista", "descricao": "..." }` |
| `GET`    | `/{id}/` | Detalha um tipo de serviço.   | Público             | N/A                               |
| `PUT`    | `/{id}/` | Atualiza um tipo de serviço.  | Autenticado (Admin) | `{ "nome": "Eletricista Predial" }` |
| `DELETE` | `/{id}/` | Deleta um tipo de serviço.    | Autenticado (Admin) | N/A                               |

### Prestadores (`/providers/`)

Gerenciamento dos perfis de prestadores de serviço.

| Método   | URL     | Descrição                 | Permissão     |
| :------- | :------ | :------------------------ | :------------ |
| `GET`    | `/`     | Lista todos os prestadores. | Público       |
| `POST`   | `/`     | Cria um novo prestador.   | Autenticado   |
| `GET`    | `/{id}/` | Detalha um prestador.     | Público       |
| `PUT`    | `/{id}/` | Atualiza um prestador.    | Dono da conta |
| `DELETE` | `/{id}/` | Deleta um prestador.      | Dono da conta |

**Corpo para `POST` (Criar):**

```json
{
    "usuario_id": 1,
    "descricao": "Especialista em instalações elétricas.",
    "disponivel": true,
    "tipos_de_servico_ids": [1, 3]
}
```

### Solicitações de Serviço (`/service-requests/`)

Gerenciamento de pedidos de serviço feitos por clientes.

| Método   | URL     | Descrição                       | Permissão     |
| :------- | :------ | :------------------------------ | :------------ |
| `GET`    | `/`     | Lista as solicitações do usuário. | Autenticado   |
| `POST`   | `/`     | Cria uma nova solicitação.      | Autenticado   |
| `GET`    | `/{id}/` | Detalha uma solicitação.        | Dono da conta |
| `PUT`    | `/{id}/` | Atualiza uma solicitação.       | Dono da conta |
| `DELETE` | `/{id}/` | Deleta uma solicitação.         | Dono da conta |

**Corpo para `POST` (Criar):**

```json
{
    "titulo": "Instalar chuveiro novo",
    "descricao": "Preciso trocar o chuveiro antigo por um novo no banheiro principal.",
    "endereco": "Rua das Flores, 456, Apto 101",
    "tipo_servico_id": 1
}
```

## API Navegável

Para facilitar os testes, a API possui uma interface web navegável. Para acessá-la, inicie o servidor e acesse as seguintes URLs no seu navegador:

-   **Raiz da API:** `http://127.0.0.1:8000/api/`
-   **Login/Logout (para a interface web):** `http://127.0.0.1:8000/api-auth/login/`

Use as credenciais do superusuário ou de qualquer outro usuário criado para fazer login e interagir diretamente com os endpoints.