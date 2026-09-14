# Simulado ENADE — Engenharia de Produção

Aplicativo web de treinamento para o ENADE de Engenharia de Produção, construído a partir das
provas oficiais do INEP de **2014, 2017, 2019 e 2023**.

---

## 1. O que é entregue

```
simulado-enade-ep/
├── banco/                     ← BANCO DE QUESTÕES (fonte da verdade)
│   ├── oficiais-2014a.json    ·  105 questões oficiais do ENADE
│   ├── oficiais-2014b.json
│   ├── oficiais-2017a.json
│   ├── oficiais-2017b.json
│   ├── oficiais-2019a.json
│   ├── oficiais-2019b.json
│   ├── oficiais-2023a.json
│   ├── oficiais-2023b.json
│   ├── oficiais-2023c.json
│   ├── adaptadas-a.json …-f   ·  105 questões adaptadas (6 arquivos)
│   └── ineditas-a.json …-h    ·  105 questões inéditas (8 arquivos)
├── figuras/                   ← 28 figuras recortadas dos PDFs originais
├── app/index.html             ← interface (HTML + CSS + JS)
├── build.py                   ← gera o aplicativo final
├── testar.py                  ← testes automatizados
├── dist/
│   ├── simulado-enade-ep.html ← APLICATIVO PRONTO (abre com duplo clique)
│   ├── artifact.html          ← mesma coisa, para publicar na web
│   └── screenshots/           ← capturas desktop e celular
└── README.md
```

**O banco está separado da interface.** Para incluir questões novas, você mexe apenas em
`banco/*.json` e roda `python build.py`. A interface não precisa ser tocada.

---

## 2. Composição do banco

| Tipo | Qtd. | % | Observação |
|---|---:|---:|---|
| **Oficiais** | 105 | 33,3% | Componente específico das provas de 2014, 2017, 2019 e 2023, com gabarito definitivo do INEP |
| **Adaptadas** | 105 | 33,3% | Uma para cada oficial: mesma competência, com contexto e dados alterados |
| **Inéditas** | 105 | 33,3% | Criadas no padrão ENADE, com situações-problema aplicadas |
| **Total** | **315** | 100% | distribuídas em 23 áreas |

O banco é **equilibrado em terços**. A regra que estrutura as adaptadas é **uma por oficial**:
cada questão do ENADE tem uma contraparte que cobra a mesma competência em outro contexto — útil
para o aluno verificar se aprendeu o conceito ou apenas decorou aquela questão específica.

### Por que 105 e não 110 oficiais

Das 110 questões objetivas do componente específico das quatro provas:

- **2 foram anuladas pelo INEP** — ENADE 2014 questão 26 e ENADE 2017 questão 35;
- **3 foram deixadas de fora** — ENADE 2014 questão 14, ENADE 2017 questões 12 e 14. Nessas três,
  **as próprias alternativas A–E são imagens** (sequências de símbolos, fórmulas e gráficos como
  opções), o que não se transpõe de forma confiável para um quiz objetivo.

A **Formação Geral** (33 questões) não entra no banco: é conteúdo genérico de atualidades e
interpretação de texto, não de Engenharia de Produção. Se quiser incluí-la depois, basta criar um
arquivo `banco/formacao-geral.json` no mesmo formato.

### Questões com figura

27 questões dependem de figura (circuitos, boxplots, cartas de controle, diagramas de rede,
histogramas, tabelas). As figuras foram **recortadas diretamente dos PDFs originais** e embutidas
no aplicativo — nenhuma questão foi descartada por causa disso.

---

## 3. Como usar

### Opção A — arquivo local (sem internet)

Abra `dist/simulado-enade-ep.html` com duplo clique. Funciona offline, em qualquer navegador.
Para distribuir aos alunos, basta enviar esse único arquivo (≈2,3 MB).

### Opção B — link público na internet (para qualquer pessoa)

A pasta **`dist/publicar/`** já está pronta: contém um único `index.html` autossuficiente.
Escolha uma das opções abaixo — nenhuma exige servidor, banco de dados ou backend.

**1. Netlify Drop — mais rápido, sem instalar nada**

1. Acesse **https://app.netlify.com/drop**
2. Arraste a pasta `dist/publicar/` inteira para a área indicada
3. Em segundos aparece um link público, do tipo `https://nome-aleatorio.netlify.app`

Qualquer pessoa abre esse link, sem login e sem conta. Criando uma conta gratuita você mantém
o link permanente e pode trocar o nome do site.

**2. GitHub Pages — gratuito e permanente**

1. Crie um repositório **público** no github.com
2. Envie o `index.html` para a raiz do repositório
3. Em *Settings → Pages*, selecione a branch `main` e a pasta `/ (root)`, e salve
4. O endereço fica `https://SEU-USUARIO.github.io/NOME-DO-REPO/`

**3. Moodle da UNISINOS**

Envie o `index.html` como recurso do tipo *Arquivo* na disciplina. Os alunos acessam pelo
ambiente, já autenticados.

**4. Qualquer outra hospedagem estática**

Cloudflare Pages, Vercel, Google Sites, hospedagem da própria instituição — todas servem.
É um arquivo estático comum.

### Opção C — link do Artifact (claude.ai)

**https://claude.ai/code/artifact/8fbfb95d-dbb7-450f-b6cc-3edb66aeb321**

Este link nasce privado. Abra a página e use o menu de compartilhamento para liberar o acesso —
confira ali quais níveis de acesso estão disponíveis na sua conta. Para uma turma inteira, as
opções 1 a 3 acima são mais previsíveis, por não dependerem de conta em nenhuma plataforma.

---

## 4. Como adicionar ou corrigir questões

### 4.1. Formato de uma questão

Cada arquivo em `banco/` é uma **lista JSON**. Você pode criar quantos arquivos quiser — o build
junta todos automaticamente. Modelo:

```json
{
  "id": "INE-31",
  "tipo": "Inédita",
  "ano": null,
  "referencia": "",
  "area": "Gestão da Qualidade",
  "dificuldade": "Média",
  "competencia": "O que a questão avalia, em uma frase.",
  "enunciado": "Texto do enunciado.\n\nUse \\n para quebrar linha.",
  "figura": "minha_figura.png",
  "alternativas": {
    "A": "texto da alternativa A",
    "B": "texto da alternativa B",
    "C": "texto da alternativa C",
    "D": "texto da alternativa D",
    "E": "texto da alternativa E"
  },
  "gabarito": "C",
  "justificativa": "Por que a alternativa C é a correta.",
  "porqueErradas": {
    "A": "Por que A está errada.",
    "B": "Por que B está errada.",
    "D": "Por que D está errada.",
    "E": "Por que E está errada."
  },
  "observacao": "Campo opcional, para ressalvas sobre a questão."
}
```

**Campos obrigatórios:** `id`, `tipo`, `area`, `dificuldade`, `competencia`, `enunciado`,
`alternativas`, `gabarito`, `justificativa`, `porqueErradas`.

**Regras que o build verifica e recusa se violadas:**

- `id` único em todo o banco;
- exatamente 5 alternativas: A, B, C, D e E, nenhuma vazia;
- `gabarito` ∈ {A, B, C, D, E};
- o gabarito **não** pode aparecer em `porqueErradas`;
- `tipo` ∈ {Oficial, Adaptada, Inédita};
- se houver `figura`, o arquivo precisa existir em `figuras/`.

Campos opcionais: `ano`, `referencia`, `figura`, `observacao`.

### 4.2. Passo a passo

1. Edite um arquivo existente em `banco/` ou crie um novo (ex.: `banco/minhas-questoes.json`).
   Se criar do zero, o conteúdo deve começar com `[` e terminar com `]`.
2. Se a questão tiver figura, coloque o PNG em `figuras/` e referencie pelo nome no campo `figura`.
3. Rode o build:
   ```
   cd "simulado-enade-ep"
   python build.py
   ```
4. Rode os testes:
   ```
   python testar.py
   ```
5. Abra `dist/simulado-enade-ep.html` e confira.

O build recusa o arquivo se encontrar qualquer inconsistência, apontando a questão e o problema —
ou seja, **não é possível publicar um banco quebrado sem perceber**.

### 4.3. Quantos simulados sem repetir questões?

Com 315 questões e 20 por simulado, o aplicativo evita as questões dos **3 simulados anteriores**
(60 questões). Na prática, o aluno faz cerca de 15 simulados antes de rever qualquer questão.

### 4.4. Ajustar o tamanho do simulado

No arquivo `app/index.html`, perto do início do `<script>`:

```js
const N_QUESTOES   = 20;   // questões por simulado
const MAX_POR_AREA = 3;    // teto de questões da mesma área
const HIST_EVITAR  = 3;    // simulados anteriores cujas questões são evitadas
```

Altere e rode `python build.py` novamente.

---

## 5. Como publicar uma nova versão

Depois de `python build.py`, o arquivo `dist/artifact.html` fica atualizado.

- **Distribuição por arquivo:** envie `dist/simulado-enade-ep.html` aos alunos (e-mail, Moodle,
  Drive, pendrive). Funciona offline.
- **Hospedagem pública (Netlify, GitHub Pages, Moodle):** copie o novo
  `dist/simulado-enade-ep.html` por cima de `dist/publicar/index.html` e republique. No Netlify
  Drop, basta arrastar a pasta de novo; o endereço permanece o mesmo se você tiver conta.
- **Artifact do claude.ai:** peça para eu republicar o `dist/artifact.html` — o link não muda.

---

## 6. Testes automatizados

`python testar.py` executa o aplicativo real dentro do Chrome em modo headless e verifica:

**Banco e sorteio**
- integridade de todas as questões (ids únicos, 5 alternativas, gabarito válido, justificativas);
- o sorteio devolve sempre 20 questões, sem nenhuma repetida no mesmo simulado;
- distribuição equilibrada — no máximo 3 questões da mesma área;
- nenhuma questão domina os sorteios (frequência medida em 400 simulados, com limites
  relativos ao tamanho do banco);
- todas as 315 questões e todas as 23 áreas podem ser sorteadas;
- o simulado seguinte não reaproveita questões do anterior.

**Correção e resultado**
- exatamente uma alternativa correta por questão;
- placar correto nos cenários de 20 acertos, 0 acertos, 10 acertos e prova em branco;
- a tela de resultado destaca o gabarito certo e mostra a justificativa correspondente;
- questões não respondidas contam como erro.

**Fluxo de uso**
- não inicia sem o nome do aluno;
- mostra "Questão 1 de 20" e 5 alternativas clicáveis;
- **o gabarito não aparece em nenhum momento durante o simulado**;
- pede confirmação antes de finalizar;
- exibe as 20 questões na correção detalhada;
- recupera o simulado em andamento se a página for recarregada.

**Responsividade**
- mede o conteúdo em viewport real de **390 px e 320 px** e confirma que não há rolagem horizontal
  nem elemento estourando, nas três telas.

`python testar.py --shots` gera também as capturas em `dist/screenshots/`.

---

## 7. Sobre o gabarito no código

O aplicativo é 100% client-side: não há servidor. Para a correção funcionar sem internet, o
gabarito precisa estar no navegador do aluno. O banco é gravado **codificado (XOR + base64)**,
de modo que não é legível abrindo o código-fonte da página.

Isso é **ofuscação, não segurança**: alguém com conhecimento técnico e disposição consegue
decodificar. Para impedir de fato, seria necessário um servidor que guardasse o gabarito e
corrigisse as respostas — o que exigiria hospedagem e sairia do escopo de um arquivo único.
Na prática, para um simulado de treinamento, a ofuscação resolve.

---

## 8. Como o texto foi extraído dos PDFs

Registro do método, caso seja preciso reprocessar as provas no futuro.

Os PDFs do INEP usam fontes CID embaralhadas: a extração normal devolve `ĞŵƉƌĞƐĂ` em vez de
`empresa`. Os códigos dos caracteres são, na verdade, **glyph IDs da fonte Calibri**. O texto foi
recuperado mapeando cada glyph ID de volta ao caractere correto pela tabela da Calibri instalada no
Windows, com tratamento das ligaduras (`fi`, `ti`, `tí`, `tt`) que não têm correspondência direta.

Resultado: menos de 10 caracteres não resolvidos por prova (contra ~1.100 na extração bruta).

Os gabaritos de 2019 e 2023 saíam desalinhados no modo tabela do `pdftotext`; foram reextraídos em
modo bruto (`-raw`) e conferidos item a item.

---

## 9. Requisitos

- **Python 3** — apenas para rodar `build.py` e `testar.py`. O aplicativo em si não precisa de nada.
- **Chrome ou Edge** — apenas para `testar.py`.
- O aplicativo gerado roda em qualquer navegador moderno, sem instalação e sem internet.


---

## 10. Link do aplicativo

**https://claude.ai/code/artifact/8fbfb95d-dbb7-450f-b6cc-3edb66aeb321**

Lembre-se de compartilhar a página (ela começa privada) antes de divulgar o endereço aos alunos.
