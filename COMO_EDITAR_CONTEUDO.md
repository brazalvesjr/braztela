# 📝 COMO EDITAR OS CONTEÚDOS NO GITHUB

## 🎬 CANAIS (TV AO VIVO)

Arquivo: `canais.json`

### Estrutura:
```json
{
  "categorias": ["Notícias", "HBO", "Esportes"],
  "canais": [
    {
      "id": 1,
      "nome": "Band News 4K",
      "url": "http://seu-link-do-video.m3u8",
      "logo": "http://seu-link-da-imagem.png",
      "categoria": "Notícias",
      "ativo": true
    }
  ]
}
```

### Como adicionar um novo canal:
1. Abra o arquivo `canais.json`
2. Copie um canal existente
3. Mude os valores:
   - `"id"` → número único (1, 2, 3...)
   - `"nome"` → nome do canal
   - `"url"` → link do stream (M3U8)
   - `"logo"` → link da imagem/logo
   - `"categoria"` → escolha uma categoria (Notícias, HBO, Esportes)
   - `"ativo"` → true ou false

### Exemplo:
```json
{
  "id": 10,
  "nome": "Novo Canal",
  "url": "http://seu-servidor.com/novo-canal.m3u8",
  "logo": "http://seu-servidor.com/novo-canal.png",
  "categoria": "Notícias",
  "ativo": true
}
```

---

## 🎥 FILMES

Arquivo: `filmes.json`

### Estrutura:
```json
{
  "categorias": ["4K", "Ação", "Comédia", "Drama", "Terror"],
  "filmes": [
    {
      "id": 1,
      "nome": "Nome do Filme",
      "url": "http://seu-link-do-filme.mp4",
      "logo": "http://seu-link-do-poster.jpg",
      "categoria": "Ação",
      "sinopse": "Descrição do filme",
      "ativo": true
    }
  ]
}
```

### Como adicionar um novo filme:
1. Abra o arquivo `filmes.json`
2. Copie um filme existente
3. Mude os valores:
   - `"id"` → número único
   - `"nome"` → nome do filme
   - `"url"` → link do filme (MP4, MKV, etc)
   - `"logo"` → link do poster
   - `"categoria"` → escolha uma categoria (4K, Ação, Comédia, Drama, Terror)
   - `"sinopse"` → descrição do filme
   - `"ativo"` → true ou false

---

## 📺 SÉRIES

Arquivo: `series.json`

### Estrutura:
```json
{
  "categorias": ["TURCAS", "NETFLIX", "PRIME VÍDEO", "NOVELAS", "AMC", "APPLE", "BRASIL PARALELO", "DISCOVERY PLUS", "DISNEY PLUS"],
  "series": [
    {
      "id": 1,
      "nome": "Nome da Série",
      "url": "http://seu-link-da-serie.mp4",
      "logo": "http://seu-link-do-poster.jpg",
      "categoria": "NETFLIX",
      "sinopse": "Descrição da série",
      "ativo": true
    }
  ]
}
```

### Como adicionar uma nova série:
1. Abra o arquivo `series.json`
2. Copie uma série existente
3. Mude os valores:
   - `"id"` → número único
   - `"nome"` → nome da série
   - `"url"` → link da série
   - `"logo"` → link do poster
   - `"categoria"` → escolha uma categoria (TURCAS, NETFLIX, PRIME VÍDEO, etc)
   - `"sinopse"` → descrição da série
   - `"ativo"` → true ou false

---

## 👤 CLIENTES (Autenticação)

Arquivo: `clientes.json`

### Estrutura:
```json
{
  "clientes": [
    {
      "codigo": "TESTE",
      "senha": "123456",
      "nome": "Teste",
      "ativo": true
    }
  ]
}
```

### Como adicionar um novo cliente:
1. Abra o arquivo `clientes.json`
2. Copie um cliente existente
3. Mude os valores:
   - `"codigo"` → código de acesso (ex: BRAZ)
   - `"senha"` → senha (ex: admin2026)
   - `"nome"` → nome do cliente
   - `"ativo"` → true ou false

---

## ⚙️ PASSO A PASSO PARA EDITAR

1. Abra o GitHub: https://github.com/brazalvesjr/braztela
2. Clique na pasta com o arquivo que quer editar (canais.json, filmes.json, series.json)
3. Clique no lápis (✏️) para editar
4. Faça as mudanças
5. Clique em "Commit changes" (verde)
6. Escreva uma mensagem (ex: "Adicionado novo canal")
7. Clique em "Commit"
8. **Reinicie o addon no Kodi** para carregar as mudanças

---

## 📌 DICAS IMPORTANTES

- ✅ Sempre use URLs válidas (links que funcionam)
- ✅ Use `true` ou `false` (sem aspas) para ativo/inativo
- ✅ Sempre termine com uma vírgula (`,`) entre os itens, EXCETO no último
- ✅ Mantenha a mesma estrutura (chaves, valores, etc)
- ✅ Se der erro, copie um item existente e modifique

---

## ❌ ERROS COMUNS

### Erro: "JSON inválido"
- Falta de vírgula entre itens
- Aspas faltando
- Chaves não fechadas

### Erro: "Conteúdo não aparece"
- URL inválida ou link quebrado
- Categoria errada (não existe)
- `"ativo": false` (mude para `true`)

---

**Qualquer dúvida, me avisa!** 🎬
