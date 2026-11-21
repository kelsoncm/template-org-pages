<!-- template:start -->
# template-org-pages

Template do portal `<org>.github.io` de uma organização: site estático bilíngue (`/en/` e `/pt-br/`, com
redirecionamento pelo idioma do navegador), tema claro/escuro, página 404 e publicação no GitHub Pages por Actions.
Sem fontes, ícones ou scripts de terceiros.

## Como usar

1. **Use this template > Create a new repository** com o nome exato `<org>.github.io`, **público**, dentro da
   organização.
2. Clone e rode o inicializador (só biblioteca padrão do Python 3.10+):

   ```bash
   python template_init.py --title "Minha Suite" --tagline-en "..." --tagline-pt "..."
   ```

3. Em *Settings > Pages*, escolha *Source: GitHub Actions*.
4. Troque `img/logo.svg`, a cor `--brand` em `css/style.css` e os cartões de projetos nas duas línguas.

---
<!-- template:end -->
# {{OWNER}}.github.io

Portal da organização **{{TITLE}}**: <https://{{OWNER}}.github.io>.

Site estático bilíngue publicado pelo workflow `pages.yml` a cada push na `main`.

| Caminho | Conteúdo |
|---|---|
| `index.html` | Redireciona para `/en/` ou `/pt-br/` conforme o idioma do navegador |
| `en/`, `pt-br/` | Página principal em cada língua (mantenha as duas em sincronia) |
| `css/style.css` | Estilos e cores (variável `--brand`), tema claro/escuro |
| `js/main.js` | Alternância de tema |
| `img/logo.svg` | Logo e favicon |

A documentação de cada projeto fica no Pages do próprio repositório: `https://{{OWNER}}.github.io/<repositório>/`.
