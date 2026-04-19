# 🔴 BRAZTELA — Addon Kodi

> **Plataforma de streaming premium desenvolvida por Braz Junior.**
> Cores: Vermelho e Preto | Versão: 1.0.0 | Kodi 19+ (Matrix) e 20+ (Nexus)

---

## Estrutura do Repositório

```
braztela/                          ← raiz do repositório GitHub
├── servers.json                   ← lista dos 20 servidores (edite aqui)
├── passwords.json                 ← senhas individuais dos clientes
├── parental.json                  ← palavras-chave para controle parental
├── README.md                      ← este arquivo
├── repository.braztela/           ← addon do repositório Kodi
│   ├── addon.xml
│   ├── icon.png
│   └── fanart.jpg
└── zips/                          ← pacotes para instalação via Kodi
    ├── addons.xml
    ├── addons.xml.md5
    ├── plugin.video.braztela/
    │   └── plugin.video.braztela-1.0.0.zip
    └── repository.braztela/
        └── repository.braztela-1.0.0.zip
```

---

## Como Instalar no Kodi

### Passo 1 — Habilitar fontes desconhecidas

No Kodi: **Configurações → Sistema → Complementos → Fontes desconhecidas → Ativar**

### Passo 2 — Instalar o Repositório

1. Vá em **Complementos → Instalar a partir de arquivo zip**
2. Selecione o arquivo `repository.braztela-1.0.0.zip`
3. Aguarde a mensagem de confirmação

### Passo 3 — Instalar o Addon

1. Vá em **Complementos → Instalar a partir do repositório → BRAZTELA Repository**
2. Selecione **Complementos de vídeo → BRAZTELA → Instalar**
3. Aguarde a instalação

### Passo 4 — Primeiro Acesso

1. Abra o addon BRAZTELA
2. Insira o **Código do Cliente** e a **Senha** fornecidos por Braz Junior
3. Configure um **PIN de 4 dígitos** para o Controle Parental
4. Selecione um servidor em **TROCAR SERVIDOR**
5. Informe o usuário e senha do painel Xtream do servidor escolhido

---

## Gerenciar Servidores (`servers.json`)

Edite o arquivo `servers.json` diretamente no GitHub. Cada servidor tem os campos:

| Campo    | Descrição                                       |
|----------|-------------------------------------------------|
| `id`     | Número único de 1 a 20                          |
| `name`   | Nome exibido no menu                            |
| `dns`    | URL completa do painel (ex: `http://ip:porta`)  |
| `active` | `true` para exibir, `false` para ocultar        |
| `note`   | Observação opcional (ex: "HD", "4K", "Backup")  |

**Exemplo:**
```json
{ "id": 1, "name": "Servidor Brasil HD", "dns": "http://192.168.1.1:8080", "active": true, "note": "Principal" }
```

---

## Gerenciar Clientes (`passwords.json`)

Cada cliente tem um registro com os campos:

| Campo      | Descrição                                          |
|------------|----------------------------------------------------|
| `code`     | Código único do cliente (maiúsculas, ex: `CLI001`) |
| `password` | Senha de acesso do cliente                         |
| `expires`  | Data de expiração no formato `YYYY-MM-DD`          |
| `active`   | `true` = ativo, `false` = bloqueado                |
| `label`    | Nome do cliente para exibição                      |

**Para criar um novo cliente**, adicione uma entrada ao array `passwords`:
```json
{
  "code": "CLIENTE002",
  "password": "minhasenha123",
  "expires": "2027-12-31",
  "active": true,
  "label": "João Silva"
}
```

**Para bloquear um cliente**, altere `"active": false`.

> As senhas são verificadas em tempo real a cada abertura do addon (cache de 15 minutos).

---

## Controle Parental (`parental.json`)

Adicione palavras-chave ao array `adult_keywords` para filtrar categorias/canais adultos. O addon oculta automaticamente qualquer item cujo nome contenha uma dessas palavras (em minúsculo).

---

## Player Avançado — Anti-Travamento

O BRAZTELA usa uma combinação de tecnologias para garantir reprodução contínua:

| Recurso                     | Descrição                                                          |
|-----------------------------|--------------------------------------------------------------------|
| **InputStream Adaptive**    | Player HLS/DASH nativo do Kodi, sem dependência de player externo  |
| **Reconexão Automática**    | Detecta parada inesperada e reconecta em até N tentativas          |
| **Fallback de extensão**    | Tenta `.m3u8` → `.ts` → `.mp4` automaticamente                    |
| **advancedsettings.xml**    | Buffer de 50–250 MB configurável, otimizado para streaming         |
| **Cache inteligente**       | Dados do servidor em cache local com TTL configurável              |

Para aplicar as otimizações de buffer, acesse **Configurações → Gravar advancedsettings.xml** e reinicie o Kodi.

---

## Atualizar o Addon

Após editar qualquer arquivo neste repositório:

1. O Kodi buscará automaticamente as atualizações via repositório instalado.
2. Para forçar atualização imediata: **Addon → Configurações → Atualizar Servidores/Senhas Agora**.
3. Para publicar nova versão do addon: edite a versão em `addon.xml`, reempacote com `build.sh` e faça commit/push dos novos zips.

---

## Créditos

**Desenvolvido por Braz Junior — 2026**
Todos os direitos reservados. Uso não autorizado é proibido.
