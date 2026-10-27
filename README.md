# arsmagnalab.com

Web de [Ars Magna Lab](https://www.youtube.com/@arsmagna_lab), el canal de YouTube de Edu Herraiz,
servida con GitHub Pages en https://arsmagnalab.com. En español, catalán e inglés
(español en la raíz, el resto en `/ca/` y `/en/`).

- Portada con el índice de proyectos, `llull/` (por qué el nombre) y `futbolin/` (el futbolín con Home Assistant).
- `python3 build.py` genera todo desde `content.json` y `_src/`; `--check` comprueba los enlaces externos.
- Las páginas del futbolín se escriben a mano, una por idioma, en `_src/futbolin.<idioma>.html`.
  La media y los diagramas están una sola vez en `futbolin/`; los diagramas, solo en español
  (los copia `futbolin/diagramas.py` desde el repo del futbolín).

Las demos de cada proyecto van en su propio subdominio, desde su repo (por ejemplo,
[ars-domus.arsmagnalab.com](https://ars-domus.arsmagnalab.com)).
