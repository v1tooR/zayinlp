# Zayin Ar Condicionado

Site estático da Zayin, publicado em `https://zayinarcondicionado.com.br/`.

## Gerar o site

```powershell
uv run --python 3.13 python build.py
```

O gerador cria as 14 páginas indexáveis em `dist/`, além de `sitemap.xml`, `robots.txt`, metadados e dados estruturados. A raiz do repositório é o diretório publicado na Hostinger; o `.htaccess` entrega as rotas limpas a partir dos arquivos de `dist/` e redireciona URLs duplicadas.

Depois de publicar, envie `https://zayinarcondicionado.com.br/sitemap.xml` no Google Search Console e solicite a indexação da home. Sempre rode o gerador antes de subir alterações de conteúdo.
