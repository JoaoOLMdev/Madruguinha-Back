# Documentação da API - Madruguinha Services

API RESTful desenvolvida para o backend do projeto Madruguinha Services, uma plataforma para conectar prestadores de serviço a clientes.

Esta API permite o gerenciamento de usuários, prestadores, tipos de serviços e solicitações de serviço.

## Tecnologias Utilizadas
-   **Banco de Dados:** PostgreSQL (via Neon DB)

## Configuração do Ambiente de Desenvolvimento

1.  **Clone o repositório:**
    ```bash
    git clone <URL-do-repositório>
    cd madruguinha-back
    ```

2.  **Crie e ative um ambiente virtual:**
    ```powershell
    python -m venv venv
    # Windows (PowerShell)
    .\venv\Scripts\Activate.ps1
    # (ou, se estiver usando cmd.exe)
    .\venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```powershell
    pip install -r requirements.txt
    ```

4.  **Crie as migrações e aplique no banco de dados:**
    ```powershell
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Crie um superusuário (para acesso ao Admin):**
    ```powershell
    python manage.py createsuperuser
    ```

6.  **Inicie o servidor de desenvolvimento:**
    ```powershell
    python manage.py runserver
    ```

### Endpoints e comportamentos (resumo atualizado)

A URL base para todos os endpoints é `http://127.0.0.1:8000/api/`.

    Observação geral sobre permissões
    - `GET` em muitos recursos é público ou `AllowAny` (ver endpoints individuais).
    - `POST`/`PUT`/`PATCH`/`DELETE` costumam exigir autenticação; algumas actions têm regras custom (ex.: criação de `Provider` é admin-only, atualização de `Provider` é permitida apenas ao dono do perfil).

    1) Autenticação (JWT)
    - `POST /api/token/` — obtém access + refresh tokens. Corpo: `{ "username": "...", "password": "..." }`.
    - `POST /api/token/refresh/` — renova token de acesso a partir do refresh.

    2) Usuários (`/api/users/`)
    - `POST /api/users/` — registra um novo usuário (AllowAny).
    - `GET /api/users/` — retorna o usuário autenticado (ou todos para staff).
    - `GET /api/users/{id}/`, `PUT`, `PATCH`, `DELETE` — padrão `ModelViewSet` com `IsOwnerOrReadOnly` (apenas dono pode modificar).

    3) Tipos de serviço (`/api/service-types/`)
    - `GET /api/service-types/` — lista todos os tipos de serviço (público).
    - `POST /api/service-types/` — cria tipo (requer autenticação; geralmente admin).
    - `GET /api/service-types/{id}/`, `PUT`, `PATCH`, `DELETE` — gerenciamento padrão.

    4) Prestadores (`/api/providers/`)
    - `GET /api/providers/` — lista pública de providers (AllowAny). Filtre por `is_active` no front-end se desejar apenas ativos.
    `POST /api/providers/` — criar provider: se o requisitante for administrador cria o `Provider` imediatamente; se for um usuário comum, cria uma `ProviderApplication` (solicitação) com status `PENDING` que deve ser aprovada por um administrador. Admins podem revisar via `/api/provider-applications/` e usar `/api/provider-applications/{id}/approve/` ou `/reject/`.
    - `POST /api/providers/` — criar provider: atualmente restrito a administradores.
    - `PUT` / `PATCH` / `DELETE` em `/api/providers/{id}/` — permitido apenas ao dono do provider (`IsOwnerOnly`) ou staff.

    Campos importantes no `Provider` API:
    - `service_types` — representação nested (read-only) dos `ServiceType` associados.
    - `service_types_ids` — write-only (array de IDs) usado para criar/atualizar a associação; exemplo: `{ "service_types_ids": [1,3] }`.
    - `stars` — read-only: média calculada a partir das `ratings`.

    5) Solicitações de Serviço (`/api/service-requests/`)
    - `GET /api/service-requests/` — comportamento depende do usuário:
        - Staff: lista todas as requests.
        - Provider (usuário com `provider_profile`): lista as requests PENDING que correspondem aos `service_types` do provider (útil para providers verem trabalhos disponíveis).
        - Cliente (usuário comum): lista apenas as requests criadas por ele.
    - `POST /api/service-requests/` — cria uma nova solicitação; `client` é definido automaticamente como `request.user`.
    - `GET /api/service-requests/{id}/` — detalhes da solicitação (inclui `provider` quando atribuído, `status`, e `rating` quando presente).
    - `PUT` / `PATCH` / `DELETE` — permitidos ao dono da request (client) ou staff conforme `IsOwnerOrReadOnly`.

    Actions customizadas (sub-rotas):
    - `POST /api/service-requests/{id}/accept/` — Providers autenticados (usuário com `provider_profile`) podem aceitar uma request PENDING que corresponda a um de seus `service_types`; isso atribui o `provider` e muda `status` para `IN_PROGRESS`.
        - Regras: request deve ser PENDING; provider não pode ser o client; provider deve oferecer o `service_type` requisitado.
    - `POST /api/service-requests/{id}/rate/` — Cliente (criador da request) pode avaliar o provider após a conclusão (`status == COMPLETED`). Só pode ser feito uma vez por request.

    Exemplo de criação de ServiceRequest
    ```json
    {
        "title": "Instalar chuveiro novo",
        "description": "Preciso trocar o chuveiro antigo por um novo no banheiro principal.",
        "address": "Rua das Flores, 456, Apto 101",
        "service_type": 1
    }
    ```

    Exemplo de provider aceitando request (provider autenticado):
    POST /api/service-requests/123/accept/

    Exemplo de avaliação (depois de `status` == COMPLETED):
    POST /api/service-requests/123/rate/
    Body:
    ```json
    {
        "score": "4.50",
        "comment": "Ótimo trabalho, chegou no horário."
    }
    ```

    ## API Navegável

    Para facilitar os testes, a API possui uma interface web navegável. Para acessá-la, inicie o servidor e acesse as seguintes URLs no seu navegador:

    - **Raiz da API:** `http://127.0.0.1:8000/api/`
    - **Login/Logout (para a interface web):** `http://127.0.0.1:8000/api-auth/login/`

    Use as credenciais do superusuário ou de qualquer outro usuário criado para fazer login e interagir diretamente com os endpoints.
| `POST` | `/`     | Registra um novo usuário.      | Público         | `{ "username": "...", "email": "...", "password": "...", "first_name": "...", "last_name": "...", "address": "..." }`      |
| `GET`  | `/`     | Lista todos os usuários.       | Autenticado     | N/A                                                                                                                       |
| `GET`  | `/{id}/` | Detalha um usuário.            | Autenticado     | N/A                                                                                                                       |
| `PUT`  | `/{id}/` | Atualiza um usuário.           | Dono da conta\* | `{ "first_name": "...", "last_name": "...", "address": "..." }`                                                          |
| `PATCH` | `/{id}/` | Atualiza parcialmente um usuário. | Dono da conta\* | `{ "address": "Nova Rua, 123" }`                                                                                         |

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
    "description": "Especialista em instalações elétricas.",
    "cpf": "000.000.000-00",
    "service_types": [1, 3]
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
    "title": "Instalar chuveiro novo",
    "description": "Preciso trocar o chuveiro antigo por um novo no banheiro principal.",
    "address": "Rua das Flores, 456, Apto 101",
    "service_type": 1
}
```

## API Navegável

Para facilitar os testes, a API possui uma interface web navegável. Para acessá-la, inicie o servidor e acesse as seguintes URLs no seu navegador:
-   **Login/Logout (para a interface web):** `http://127.0.0.1:8000/api-auth/login/`

Use as credenciais do superusuário ou de qualquer outro usuário criado para fazer login e interagir diretamente com os endpoints.

## Docs automáticas e exemplos

O projeto expõe um schema OpenAPI e uma UI Swagger (via `drf-spectacular`):
- Swagger UI: `GET /api/docs/`

Quick examples (curl)

1) Obter token JWT
```bash
curl -X POST http://127.0.0.1:8000/api/token/ -H 'Content-Type: application/json' \
    -d '{"username":"<USER>","password":"<PASS>"}'
```

2) Criar ServiceRequest (cliente autenticado)
```bash
curl -X POST http://127.0.0.1:8000/api/service-requests/ \
    -H 'Authorization: Bearer <ACCESS>' -H 'Content-Type: application/json' \
    -d '{"title":"Instalar chuveiro","description":"...","address":"Rua X","service_type":1}'
```

3) Provider listar requests compatíveis (provider autenticado)
```bash
curl -X GET http://127.0.0.1:8000/api/service-requests/ -H 'Authorization: Bearer <PROVIDER_ACCESS>'
```

4) Provider aceitar request
```bash
curl -X POST http://127.0.0.1:8000/api/service-requests/<ID>/accept/ \
    -H 'Authorization: Bearer <PROVIDER_ACCESS>'
```

5) Cliente avaliar provider (após COMPLETED)
```bash
curl -X POST http://127.0.0.1:8000/api/service-requests/<ID>/rate/ \
    -H 'Authorization: Bearer <ACCESS>' -H 'Content-Type: application/json' \
    -d '{"score":"4.50","comment":"Bom serviço"}'
```

6) Atualizar provider com tipos de serviço (owner ou admin)
```bash
curl -X PATCH http://127.0.0.1:8000/api/providers/<ID>/ \
    -H 'Authorization: Bearer <ACCESS>' -H 'Content-Type: application/json' \
    -d '{"service_types_ids":[1,2]}'
```


-   Endpoints de prestadores exigem autenticação para criar/editar e permitem leitura pública.
-   Em desenvolvimento, se `DATABASE_URL` não for definido, a aplicação usa SQLite local automaticamente.