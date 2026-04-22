# BRAZTELA - Addon Premium para Kodi

**Desenvolvido por Braz Junior**

Plataforma completa de streaming para Kodi com TV ao vivo, filmes, séries, autenticação por cliente e controle parental.

---

## Instalação no Kodi

### Método 1 - Via Repositório (Recomendado)

1. No Kodi, vá em **Configurações** → **Sistema** → **Add-ons**
2. Ative **Fontes Desconhecidas**
3. Volte para **Configurações** → **Gerenciador de Arquivos** → **Adicionar fonte**
4. Cole esta URL:
   ```
   https://raw.githubusercontent.com/brazalvesjr/braztela/main/zips/
   ```
5. Nomeie como `BRAZTELA` e clique em **OK**
6. Volte ao menu principal → **Add-ons** → **Instalar de arquivo zip**
7. Selecione `BRAZTELA` → `repository.braztela-1.0.0.zip`
8. Aguarde a notificação "Add-on instalado"
9. Clique em **Instalar do repositório** → **BRAZTELA Repository** → **Add-ons de Vídeo** → **BRAZTELA** → **Instalar**

### Método 2 - Direto via ZIP

1. Baixe o arquivo: [plugin.video.braztela-1.0.0.zip](https://raw.githubusercontent.com/brazalvesjr/braztela/main/zips/plugin.video.braztela-1.0.0.zip)
2. No Kodi: **Add-ons** → **Instalar de arquivo zip** → Selecione o arquivo

---

## Clientes Padrão

| Código | Senha | Status |
|--------|-------|--------|
| TESTE | 123456 | Ativo |
| BRAZ | admin2026 | Ativo (Admin) |
| CLIENTE001 | senha123456 | Ativo |
| CLIENTE002 | acesso2026 | Ativo |
| CLIENTE003 | premium789 | Ativo |
| CLIENTE004 | streaming001 | Ativo |
| CLIENTE005 | braztela2026 | Ativo |

---

## Recursos

- **TV ao Vivo** com categorias (Esportes, Filmes, Notícias, Variedades, Infantil)
- **Filmes** com sinopse, capa e metadados
- **Séries** com episódios e categorias
- **20 servidores** configuráveis
- **Autenticação individual** por cliente
- **Controle Parental** com PIN de 4 dígitos
- **Cores oficiais**: Vermelho e Preto

---

## Como adicionar/bloquear clientes

Edite o arquivo `plugin.video.braztela/default.py` na seção `CLIENTES`:

```python
CLIENTES = {
    "NOVOCLIENTE": {
        "senha": "minhasenha",
        "nome": "Nome do Cliente",
        "ativo": True,         # False para bloquear
        "validade": "2026-12-31"
    },
}
```

Depois faça commit no GitHub. Os usuários receberão a atualização automaticamente pelo Kodi.

---

## Como configurar os servidores

Edite a seção `SERVIDORES` no `default.py`:

```python
SERVIDORES = [
    {"id": 1, "nome": "Premium HD #1", "dns": "http://seu-servidor-real.com:8080", "ativo": True},
]
```

---

**BRAZTELA v1.0.0 - 2026 © Braz Junior**
