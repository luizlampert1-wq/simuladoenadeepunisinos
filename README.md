# Simulado ENADE — Engenharia de Produção

Aplicativo web de treinamento para o ENADE de Engenharia de Produção, construído a partir das
provas oficiais do INEP de **2014, 2017, 2019 e 2023**.

Cada simulado reproduz a estrutura do componente específico do ENADE 2023:
**38 questões — 36 objetivas e 2 discursivas**.

---

## 1. O que é entregue

```
simulado-enade-ep/
├── banco/                          ← BANCO DE QUESTÕES (fonte da verdade)
│   ├── oficiais-2014a.json         ·  105 objetivas oficiais do ENADE
│   ├── oficiais-2014b.json
│   ├── oficiais-2017a.json  …b
│   ├── oficiais-2019a.json  …b
│   ├── oficiais-2023a.json  …b, c
│   ├── adaptadas-a.json …-f        ·  105 objetivas adaptadas (6 arquivos)
│   ├── ineditas-a.json …-h         ·  105 objetivas inéditas (8 arquivos)
│   ├── discursivas-oficiais.json   ·   10 discursivas oficiais do ENADE
│   ├── discursivas-adaptadas.json  ·   10 discursivas adaptadas
│   └── discursivas-ineditas.json   ·   10 discursivas inéditas
├── figuras/                        ← 29 figuras recortadas dos PDFs originais
├── app/index.html                  ← interface (HTML + CSS + JS)
├── coleta.json                     ← para onde vão os resultados (seção 7)
├── coleta/apps-script.gs           ← script da planilha do Google, pronto para colar
├── build.py                        ← gera o aplicativo final
├── testar.py                       ← testes automatizados
├── index.html                      ← gerado pelo build — é o que o GitHub Pages publica
├── dist/
│   ├── simulado-enade-ep.html      ← APLICATIVO PRONTO (abre com duplo clique)
│   ├── artifact.html               ← mesma coisa, para publicar na web
│   ├── publicar/index.html         ← pasta pronta para arrastar no Netlify Drop
│   └── screenshots/                ← capturas desktop e celular
└── README.md
```

**O banco está separado da interface.** Para incluir questões novas, você mexe apenas em
`banco/*.json` e roda `python build.py`. A interface não precisa ser tocada.

---

## 2. Composição do banco

| Tipo | Objetivas | Discursivas | Total | % |
|---|---:|---:|---:|---:|
| **Oficiais** | 105 | 10 | **115** | 33,3% |
| **Adaptadas** | 105 | 10 | **115** | 33,3% |
| **Inéditas** | 105 | 10 | **115** | 33,3% |
| **Total** | **315** | **30** | **345** | 100% |

Distribuídas em **23 áreas** da Engenharia de Produção.

O banco é **equilibrado em terços** — e o equilíbrio vale tanto no total quanto dentro de cada
formato. A regra que estrutura as adaptadas é **uma por oficial**: cada questão do ENADE tem uma
contraparte que cobra a mesma competência em outro contexto — útil para o aluno verificar se
aprendeu o conceito ou apenas decorou aquela questão específica. Isso vale também para as
discursivas: `ADP-D1` é a adaptação de `2014-D3`, e assim por diante.

### Por que 105 objetivas oficiais e não 110

Das 110 questões objetivas do componente específico das quatro provas:

- **2 foram anuladas pelo INEP** — ENADE 2014 questão 26 e ENADE 2017 questão 35;
- **3 foram deixadas de fora** — ENADE 2014 questão 14, ENADE 2017 questões 12 e 14. Nessas três,
  **as próprias alternativas A–E são imagens** (sequências de símbolos, fórmulas e gráficos como
  opções), o que não se transpõe de forma confiável para um quiz objetivo.

A **Formação Geral** (33 questões) não entra no banco: é conteúdo genérico de atualidades e
interpretação de texto, não de Engenharia de Produção. Se quiser incluí-la depois, basta criar um
arquivo `banco/formacao-geral.json` no mesmo formato.

### Por que 30 discursivas e não ~17

A proporção 2 : 36 do simulado é garantida **no sorteio**, não no banco. No banco, as discursivas
são 30 porque **existem exatamente 10 discursivas oficiais** de Engenharia de Produção nas quatro
provas (3 por edição em 2014, 2017 e 2019; 1 em 2023, já descontadas as de Formação Geral). Reduzir
o banco para ~17 discursivas exigiria descartar 4 questões reais do ENADE — o conteúdo mais escasso
e mais valioso do acervo. Manter as 10 e espelhá-las em 10 adaptadas + 10 inéditas preserva o terço
exato e ainda dá **15 simulados de discursivas sem repetição**.

### Questões com figura

28 objetivas e 1 discursiva dependem de figura (circuitos, boxplots, cartas de controle, diagramas
de rede, histogramas, tabelas). As figuras foram **recortadas diretamente dos PDFs originais** e
embutidas no aplicativo — nenhuma questão foi descartada por causa disso.

### Padrão de resposta das discursivas — leia isto

**O INEP não publica o padrão de resposta das questões discursivas.** Nos gabaritos oficiais, as
discursivas aparecem marcadas com `***`. Os padrões de resposta e os critérios de correção deste
aplicativo foram **elaborados para ele**, a partir do enunciado e da bibliografia da área. O
aplicativo diz isso ao aluno, na própria tela de correção. Ou seja:

- o **enunciado** das discursivas oficiais é o real da prova;
- o **padrão de resposta** é material de estudo, não gabarito oficial.

---

## 3. Como usar

### Opção A — arquivo local (sem internet)

Abra `dist/simulado-enade-ep.html` com duplo clique. Funciona offline, em qualquer navegador.
Para distribuir aos alunos, basta enviar esse único arquivo (≈2,6 MB).

### Opção B — link público na internet (para qualquer pessoa)

**1. GitHub Pages — é o que está no ar hoje**

O repositório já está configurado: o `index.html` da raiz é gerado pelo `build.py` e o GitHub
Pages o publica. Fluxo de atualização na seção 6.

**2. Netlify Drop — mais rápido, sem instalar nada**

1. Acesse **https://app.netlify.com/drop**
2. Arraste a pasta `dist/publicar/` inteira para a área indicada
3. Em segundos aparece um link público, do tipo `https://nome-aleatorio.netlify.app`

**3. Moodle da UNISINOS**

Envie o `index.html` como recurso do tipo *Arquivo* na disciplina. Os alunos acessam pelo
ambiente, já autenticados — é a única opção em que a identificação do aluno é de fato confiável
(veja a seção 7).

**4. Qualquer outra hospedagem estática**

Cloudflare Pages, Vercel, Google Sites, hospedagem da própria instituição — todas servem.
É um arquivo estático comum.

### Opção C — link do Artifact (claude.ai)

**https://claude.ai/code/artifact/8fbfb95d-dbb7-450f-b6cc-3edb66aeb321**

Este link nasce privado. Abra a página e use o menu de compartilhamento para liberar o acesso.

---

## 4. Como adicionar ou corrigir questões

Cada arquivo em `banco/` é uma **lista JSON**. Você pode criar quantos arquivos quiser — o build
junta todos automaticamente. O build **deduz o formato pelo conteúdo**: quem tem `alternativas` é
objetiva, quem tem `padraoResposta` é discursiva. Não existe campo para declarar isso.

### 4.1. Questão objetiva

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

**Obrigatórios:** `id`, `tipo`, `area`, `dificuldade`, `competencia`, `enunciado`, `alternativas`,
`gabarito`, `justificativa`, `porqueErradas`. **Opcionais:** `ano`, `referencia`, `figura`,
`observacao`.

### 4.2. Questão discursiva

```json
{
  "id": "INE-D11",
  "tipo": "Inédita",
  "ano": null,
  "referencia": "",
  "area": "Planejamento e Controle da Produção",
  "dificuldade": "Difícil",
  "competencia": "O que a questão avalia, em uma frase.",
  "valor": "10,0 pontos",
  "enunciado": "Situação-problema e o que se pede.\n\na) ...\nb) ...",
  "figura": "outra_figura.png",
  "padraoResposta": "a) Resposta esperada do item a.\n\nb) Resposta esperada do item b.",
  "criterios": [
    "Calcula corretamente o tempo de ciclo do gargalo.",
    "Identifica o posto que limita a capacidade.",
    "Justifica a proposta com base no dado numérico."
  ]
}
```

**Obrigatórios:** `id`, `tipo`, `area`, `dificuldade`, `competencia`, `enunciado`,
`padraoResposta`, `criterios` (no mínimo 3). **Opcionais:** `ano`, `referencia`, `figura`, `valor`.

Os `criterios` não são decorativos: na tela de correção o aluno marca os que atendeu e o aplicativo
calcula a nota estimada proporcional. Escreva-os como itens **verificáveis**, um por linha de
raciocínio esperada.

### 4.3. Regras que o build verifica e recusa se violadas

- `id` único em todo o banco;
- toda questão tem `alternativas` **ou** `padraoResposta` — nunca os dois, nunca nenhum;
- objetiva: exatamente 5 alternativas A–E, nenhuma vazia; `gabarito` ∈ {A,…,E}; o gabarito **não**
  pode aparecer em `porqueErradas`; `justificativa` preenchida;
- discursiva: `criterios` com ao menos 3 itens; **não** pode ter `gabarito`, `alternativas` nem
  `porqueErradas`;
- `tipo` ∈ {Oficial, Adaptada, Inédita};
- se houver `figura`, o arquivo precisa existir em `figuras/`;
- o banco precisa ter pelo menos 36 objetivas e 2 discursivas, senão o simulado não fecha.

### 4.4. Passo a passo

1. Edite um arquivo existente em `banco/` ou crie um novo (ex.: `banco/minhas-questoes.json`).
   Se criar do zero, o conteúdo deve começar com `[` e terminar com `]`.
2. Se a questão tiver figura, coloque o PNG em `figuras/` e referencie pelo nome no campo `figura`.
3. Rode o build e os testes:
   ```
   cd "simulado-enade-ep"
   python build.py
   python testar.py
   ```
4. Abra `dist/simulado-enade-ep.html` e confira.

O build recusa o arquivo se encontrar qualquer inconsistência, apontando a questão e o problema —
ou seja, **não é possível publicar um banco quebrado sem perceber**.

### 4.5. Quantos simulados sem repetir questões?

O aplicativo evita as questões dos **2 simulados anteriores** (76 questões).

- **Objetivas:** 315 no banco, 36 por simulado → o aluno faz cerca de **8 simulados** antes de
  rever uma objetiva.
- **Discursivas:** 30 no banco, 2 por simulado → **15 simulados** para percorrer todas.

### 4.6. Ajustar o tamanho do simulado

No arquivo `app/index.html`, perto do início do `<script>`:

```js
const N_OBJETIVAS   = 36;   // objetivas por simulado
const N_DISCURSIVAS = 2;    // discursivas por simulado
const MAX_POR_AREA  = 4;    // teto de objetivas da mesma área
const HIST_EVITAR   = 2;    // simulados anteriores cujas questões são evitadas
const DOMINIO       = "@edu.unisinos.br";
const MAX_LINHAS    = 15;   // limite de linhas da resposta discursiva
```

Altere e rode `python build.py` novamente. Se mexer em `N_OBJETIVAS` ou `N_DISCURSIVAS`, ajuste
também os números esperados em `testar.py`.

---

## 5. Como o simulado funciona

**Identificação.** O aluno informa o e-mail institucional `@edu.unisinos.br` e o nome. Sem os dois,
o botão não avança. Os dados ficam guardados no navegador e vêm preenchidos da próxima vez.

**Sorteio.** 36 objetivas sorteadas com teto de 4 por área (garante variedade sem distorcer a
proporção entre áreas grandes e pequenas) + 2 discursivas, preferencialmente de áreas diferentes
entre si. As discursivas ficam **ao final**, como na prova real. Questões dos 2 simulados
anteriores são evitadas.

**Durante a prova.** Navegação livre entre as 38 questões, grade de acesso rápido (as discursivas
aparecem com borda destacada), contador "Questão 7 de 38", barra de progresso e contador de
caracteres/linhas nas discursivas, com aviso quando passa das 15 linhas do ENADE. **Nenhum
gabarito, justificativa ou padrão de resposta aparece antes de finalizar** — isso é verificado por
teste automatizado.

**Pausar e continuar depois.** Cada resposta é gravada no navegador no instante em que é dada —
incluindo o rascunho das discursivas, salvo a cada tecla. O aluno pode fechar a aba, desligar o
computador e voltar dias depois: ao reabrir, a tela inicial mostra o cartão *"Simulado em
andamento"* com quantas questões já respondeu, e o botão **Retomar simulado** devolve exatamente
onde parou — as mesmas 38 questões sorteadas, as mesmas respostas, na mesma questão. Ao lado fica
**Descartar e começar novo**, para quem prefere recomeçar. Não há prazo de validade.

A ressalva: o progresso vive **naquele navegador, naquele computador**. Trocar de aparelho, usar
aba anônima ou limpar os dados do navegador apaga o simulado em andamento.

**Finalizar.** Pede confirmação e avisa quantas questões estão em branco.

**Resultado.**
- Percentual, acertos, erros e nota **das 36 objetivas** — as discursivas não entram no percentual,
  porque não têm correção automática.
- Desempenho por área, ordenado da pior para a melhor.
- Correção questão a questão: resposta do aluno, gabarito destacado, justificativa da correta,
  por que a alternativa que ele marcou está errada, e as demais sob demanda.
- Nas discursivas: a resposta que ele escreveu, o padrão de resposta, e os critérios de correção
  como **checklist de autoavaliação** — marcando os atendidos, o aplicativo estima a nota.

---

## 6. Como publicar uma nova versão

Depois de `python build.py`, todos os quatro arquivos de saída ficam atualizados.

**GitHub Pages (o link que está no ar):**

```
python build.py
python testar.py
git add -A
git commit -m "Atualiza banco de questões"
git push
```

O GitHub Pages republica sozinho em 1–2 minutos. O endereço não muda. Se a página parecer a antiga,
force o recarregamento com **Ctrl + F5** — é cache do navegador.

**Distribuição por arquivo:** envie `dist/simulado-enade-ep.html` aos alunos (e-mail, Moodle,
Drive, pendrive). Funciona offline.

**Netlify Drop:** arraste a pasta `dist/publicar/` de novo; o endereço permanece o mesmo se você
tiver conta.

**Artifact do claude.ai:** peça para eu republicar o `dist/artifact.html` — o link não muda.

---

## 7. Acesso por e-mail institucional e coleta de dados

Esta seção responde às duas perguntas de viabilidade — e o que está implementado hoje.

### 7.1. O que já funciona

O aplicativo **exige** um e-mail terminado em `@edu.unisinos.br` para liberar o simulado, e grava
esse e-mail em cada registro do histórico.

### 7.2. O que isso é e o que não é

**É identificação, não autenticação.** A validação acontece no navegador do aluno. Qualquer pessoa
pode digitar `qualquercoisa@edu.unisinos.br` e entrar; alguém com conhecimento técnico pode
contornar a validação pelo console do navegador. Isso é uma limitação **inerente a um aplicativo
sem servidor** — não há como verificar de verdade um e-mail sem alguém do outro lado conferindo.

Na prática, para um simulado de treinamento, isso costuma bastar: cumpre o papel de deixar claro
que é material da turma e de marcar quem fez a prova. Se a exigência for **acesso realmente
restrito**, há dois caminhos honestos:

- **Publicar pelo Moodle da UNISINOS.** O aluno já entra autenticado pela instituição, e o
  aplicativo herda esse controle sem precisar de nada. É de longe a opção mais simples e a única
  que resolve o problema de verdade sem infraestrutura nova.
- **Colocar um backend com login institucional** (Google Workspace / Microsoft Entra da UNISINOS).
  Resolve, mas deixa de ser um arquivo estático: exige hospedagem, cadastro de aplicação no TI da
  universidade e manutenção.

### 7.3. Coleta dos resultados — como fazer cair no Excel

Hoje o histórico (e-mail, nome, data, acertos, erros, percentual, tempo, desempenho por área e os
ids das questões sorteadas) é gravado **apenas no navegador do aluno**, em `localStorage`. Ele vê
os próprios simulados na tela inicial; você não vê nada.

Para os resultados chegarem até você, é preciso um ponto de coleta. O aplicativo já está pronto:
ele monta o registro, enfileira e envia. Falta só dizer **para onde**.

#### O que você edita

Um arquivo só, na raiz do projeto — **`coleta.json`**:

```json
{
  "ativa": false,
  "url": ""
}
```

Você não mexe em HTML nem em JavaScript. Depois de editar, `python build.py` e publique. O build
recusa a configuração se `ativa` for `true` com a `url` vazia ou sem `https://`.

#### Qual caminho escolher

| Caminho | Custo | Automático | Onde os dados ficam |
|---|---|---|---|
| **A. Google Sheets** (Apps Script) | grátis | sim | planilha do Google, que você baixa em `.xlsx` |
| **B. Power Automate + Excel Online** | exige conector **premium** | sim | arquivo `.xlsx` real no OneDrive |
| **C. Sem coleta** | grátis | não | só no navegador de cada aluno |

**A recomendação depende de uma coisa que só você pode verificar:** se a sua licença da UNISINOS
inclui **Power Automate Premium**. O gatilho que o aplicativo precisa — *"Quando uma solicitação
HTTP é recebida"* — é um conector premium, e muitas licenças acadêmicas (A1/A3) não o incluem.

Para checar, leva um minuto: entre em **make.powerautomate.com**, clique em *Criar → Fluxo de nuvem
instantâneo* e procure o gatilho *"Quando uma solicitação HTTP é recebida"*. Se ele vier com o selo
**Premium** e não deixar salvar, você não tem — vá de caminho A.

- **Tem premium?** Caminho B. É Excel de verdade, no OneDrive institucional, sem nada fora da
  Microsoft.
- **Não tem?** Caminho A. Funciona hoje, de graça, e você trabalha no Excel do mesmo jeito —
  a planilha vira `.xlsx` em dois cliques.

---

#### Caminho A — Google Sheets (grátis)

1. Crie uma planilha nova no Google Drive (de preferência na conta institucional).
2. *Extensões → Apps Script*. Apague o que estiver lá e cole o conteúdo de
   **[`coleta/apps-script.gs`](coleta/apps-script.gs)**.
3. *Implantar → Nova implantação → Aplicativo da Web*, com:
   - **Executar como:** Eu (sua conta)
   - **Quem pode acessar:** Qualquer pessoa

   Autorize quando o Google pedir e **copie a URL que termina em `/exec`**.
4. Confira: cole essa URL no navegador. Deve responder *"Coleta do Simulado ENADE ativa."*
5. No projeto, edite `coleta.json`:
   ```json
   {
     "ativa": true,
     "url": "https://script.google.com/macros/s/AKfy.../exec"
   }
   ```
6. `python build.py`, `python testar.py`, `git add -A`, `git commit -m "Liga a coleta"`, `git push`.

Cada simulado finalizado vira uma linha. O script cria o cabeçalho sozinho na primeira vez.

**Para abrir no Excel:** na planilha, *Arquivo → Fazer download → Microsoft Excel (.xlsx)*.

> **Não use "Publicar na web" para ligar o Excel direto à planilha.** Funciona, mas gera um link
> público — e a planilha tem e-mails de alunos identificados. Baixar o `.xlsx` quando precisar é
> mais trabalho nenhum e não expõe nada.

---

#### Caminho B — Power Automate + Excel Online (100% Microsoft)

**A planilha**

1. No OneDrive institucional, crie uma pasta de trabalho do Excel, por exemplo
   `Simulado ENADE - resultados.xlsx`.
2. Na primeira linha, escreva os 13 cabeçalhos:

   `Recebido em | Data do simulado | E-mail | Nome | Acertos | Total objetivas | Percentual | Nota | Discursivas respondidas | Total discursivas | Minutos | Desempenho por área | Questões sorteadas`

3. Selecione essas células, *Inserir → Tabela*, marcando **"Minha tabela tem cabeçalhos"**. Em
   *Design da Tabela → Nome da Tabela*, dê um nome fixo, como `Resultados`. Isso é obrigatório: o
   Power Automate só escreve dentro de uma Tabela, nunca em células soltas.
4. Salve e **feche** o arquivo.

**O fluxo** — em **make.powerautomate.com**, com a conta dona do arquivo:

5. *Criar → Fluxo de nuvem instantâneo*. Dê um nome e escolha o gatilho **"Quando uma solicitação
   HTTP é recebida"** (tem o losango **Premium**). *Criar*.
6. **Deixe o campo "Esquema JSON do corpo da solicitação" vazio.** Em *Mostrar opções avançadas*,
   defina **Método = POST**. Se aparecer *"Quem pode acionar o fluxo?"*, escolha **Qualquer
   pessoa** — os alunos chamam o fluxo sem estar autenticados no locatário.
7. *Nova etapa* → **Analisar JSON**:
   - **Conteúdo:** a expressão `triggerBody()` (se reclamar, use `string(triggerBody())`)
   - **Esquema:** *Usar payload de exemplo para gerar esquema*, colando:

   ```json
   {
     "nome": "Ana", "email": "ana@edu.unisinos.br",
     "data": "14/09/2026, 15:52:13", "dataISO": "2026-09-14T18:52:13.000Z",
     "acertos": 27, "erros": 9, "totalObjetivas": 36, "percentual": 75,
     "discursivasRespondidas": 2, "totalDiscursivas": 2, "minutos": 48,
     "ids": ["2023-Q20"], "porArea": {}
   }
   ```

   **Por que este passo existe:** o aplicativo envia o corpo como `text/plain`, não
   `application/json`. Não é escolha — em envio sem CORS o navegador só admite os tipos da lista
   segura, e o Power Automate não devolve cabeçalhos CORS que autorizem `application/json`. Sem o
   *Analisar JSON*, `triggerBody()` é uma string e todos os campos chegam vazios na planilha.
8. *Nova etapa* → **Excel Online (Business) → Adicionar uma linha em uma tabela**:

   | Campo | Valor |
   |---|---|
   | Local | OneDrive for Business |
   | Biblioteca de documentos | OneDrive |
   | Arquivo | o `.xlsx` criado acima |
   | Tabela | `Resultados` |

   Menu *Arquivo* vazio = conexão com outra conta. Menu *Tabela* vazio = a Tabela não foi criada.

9. Preencha as colunas com a saída do **Analisar JSON** (não do gatilho). Quatro precisam de
   expressão, o resto é conteúdo dinâmico direto:

   | Coluna | Expressão |
   |---|---|
   | Recebido em | `convertFromUtc(utcNow(), 'E. South America Standard Time', 'dd/MM/yyyy HH:mm')` |
   | Nota | `div(mul(body('Analisar_JSON')?['acertos'], 10.0), body('Analisar_JSON')?['totalObjetivas'])` |
   | Desempenho por área | `string(body('Analisar_JSON')?['porArea'])` |
   | Questões sorteadas | `join(body('Analisar_JSON')?['ids'], ' ')` |

   As duas últimas são objeto e lista: arrastadas como conteúdo dinâmico viram `[object Object]`
   ou quebram o fluxo.

10. **Salvar.** Só então o gatilho exibe a **URL HTTP POST** — copie e cole em `coleta.json`, com
    `"ativa": true`. Depois `python build.py`, `python testar.py` e publique.

O arquivo é um `.xlsx` de verdade no OneDrive: abre no Excel do computador, sincroniza sozinho, e
não tem link público.

Se o gatilho HTTP estiver bloqueado por licença, a Microsoft oferece um teste gratuito de 90 dias
do Power Automate Premium — dá para validar tudo antes de decidir. Se não valer a pena, o caminho A
entrega o mesmo resultado no Excel, de graça.

---

#### O que chega em cada linha

| Coluna | Exemplo |
|---|---|
| Recebido em | 14/09/2026 15:53 |
| Data do simulado | 14/09/2026 15:52 |
| E-mail | ana.camargo@edu.unisinos.br |
| Nome | Ana Beatriz Camargo |
| Acertos / Total objetivas | 27 / 36 |
| Percentual (%) / Nota (0-10) | 75 / 7,5 |
| Discursivas respondidas | 2 de 2 |
| Minutos | 48 |
| Desempenho por área | `{"Estatística":"4/4","Gestão de Estoques":"1/2",...}` |
| Questões sorteadas | `2023-Q20 ADP-14 INE-77 ...` |

As duas últimas colunas são texto bruto de propósito: servem para auditoria (conferir qual questão
caiu para quem) e para uma análise mais fina depois, sem poluir a planilha com 23 colunas de áreas.

#### O que o aplicativo faz para nada se perder

Se o aluno estiver sem internet ao finalizar, o registro **fica guardado no navegador dele** e é
reenviado automaticamente na próxima vez que abrir o aplicativo. A fila guarda os 50 resultados
mais recentes.

Duas limitações que vale saber:

- **O aplicativo não consegue confirmar a entrega.** O envio é feito em modo `no-cors`, então o
  navegador manda a requisição mas não lê a resposta. Só falha de rede é detectável — e é
  justamente essa que a fila reenvia. Quem confirma que chegou é a planilha.
- **A URL de coleta fica visível** no código da página publicada. Quem a encontrar pode enviar
  linhas. O script do caminho A já recusa e-mails fora de `@edu.unisinos.br`; se aparecer lixo,
  apague a linha.

### 7.4. Antes de ligar a coleta

Você passa a guardar e-mail e desempenho de alunos identificados — isso é dado pessoal sob a LGPD.
Três cuidados que custam pouco:

- **Avise na tela inicial** o que é coletado e para quê (posso incluir o texto no aplicativo);
- **Restrinja o acesso** à planilha a você e a quem precisa;
- **Não use os resultados para nota ou avaliação formal** sem comunicar a turma — é um simulado de
  treinamento, e tratá-lo assim evita qualquer discussão.

### 7.5. Desligar a coleta

Volte `coleta.json` para `{"ativa": false, "url": ""}`, rode `python build.py` e publique. O
aplicativo para de enviar na hora; o que já está na planilha continua lá.


## 8. Sobre o gabarito no código

O aplicativo é 100% client-side: não há servidor. Para a correção funcionar sem internet, o
gabarito precisa estar no navegador do aluno. O banco é gravado **codificado (XOR + base64)**,
de modo que não é legível abrindo o código-fonte da página.

Isso é **ofuscação, não segurança**: alguém com conhecimento técnico e disposição consegue
decodificar. Para impedir de fato, seria necessário um servidor que guardasse o gabarito e
corrigisse as respostas. Na prática, para um simulado de treinamento, a ofuscação resolve.

**Atenção ao repositório público:** os arquivos `banco/*.json` estão no GitHub em texto puro, com
gabaritos e justificativas legíveis por qualquer pessoa que abra o repositório. Se isso for um
problema, há duas saídas: tornar o repositório **privado** (o GitHub Pages continua funcionando em
contas gratuitas para repositório privado desde 2021) ou manter a pasta `banco/` fora do Git, num
Drive só seu, publicando apenas o `index.html` gerado.

---

## 9. Testes automatizados

`python testar.py` executa o aplicativo real dentro do Chrome em modo headless. São **58
verificações**:

**Banco**
- ids únicos, campos comuns preenchidos, formato corretamente deduzido;
- objetivas: 5 alternativas, gabarito válido, justificativa e explicações completas;
- discursivas: padrão de resposta e ao menos 3 critérios, sem campos de objetiva;
- proporção de terços entre oficiais, adaptadas e inéditas — no total e dentro das discursivas.

**Sorteio** (300 simulados simulados a cada execução)
- sempre 38 questões: exatamente 36 objetivas + 2 discursivas, com as discursivas ao final;
- nenhuma questão repetida no mesmo simulado;
- no máximo 4 objetivas da mesma área;
- nenhuma questão domina os sorteios — a frequência medida fica entre 0,4× e 2,5× a esperada,
  com limites relativos ao tamanho do banco (hoje: objetivas de 5,0% a 18,3%, esperado 11,4%);
- todas as 345 questões e todas as 23 áreas podem ser sorteadas;
- os 2 simulados anteriores não são reaproveitados.

**Identificação**
- aceita `@edu.unisinos.br`, inclusive em maiúsculas;
- recusa outros domínios e 10 variações de endereço malformado.

**Correção e resultado**
- exatamente uma alternativa correta por objetiva;
- placar correto nos cenários de 36, 0 e 18 acertos e prova em branco;
- percentual e nota calculados **só sobre as 36 objetivas** (27/36 → 75% → nota 7,5);
- o gabarito destacado e a justificativa exibida conferem com o banco, questão por questão;
- nas discursivas, a tela traz a resposta do aluno, o padrão de resposta e todos os critérios;
- a autoavaliação por critérios calcula a nota corretamente;
- questões não respondidas contam como erro.

**Fluxo de uso**
- não inicia sem e-mail, com e-mail de outro domínio, ou sem o nome;
- mostra "Questão 1 de 38" e 5 alternativas clicáveis nas objetivas;
- chega à discursiva na questão 37, com campo de texto e sem alternativas;
- **nenhum elemento de correção aparece durante o simulado**;
- pede confirmação antes de finalizar e exibe as 38 questões na correção;
- o histórico registra o e-mail do aluno;
- recupera o simulado em andamento — inclusive o rascunho da discursiva — ao recarregar a página.

**Pausar e continuar** (feito recarregando a página de verdade, três vezes seguidas)
- ao reabrir, a tela inicial oferece retomar e informa quantas questões já foram respondidas;
- retoma na questão exata em que parou, com as mesmas 38 questões e as mesmas respostas;
- o rascunho da discursiva volta escrito no campo de texto;
- o simulado sobrevive a fechar e reabrir mais de uma vez;
- "Descartar e começar novo" apaga o simulado interrompido.

**Coleta de resultados**
- vem desativada por padrão, e com ela desligada nada é enfileirado para envio;
- o histórico local é gravado de qualquer forma;
- com a coleta ligada, o resultado entra na fila e o envio é disparado;
- a fila de reenvio tem teto de 50 registros e descarta os mais antigos.

**Responsividade**
- mede o conteúdo em viewport real de **390 px e 320 px** nas quatro telas (início, objetiva,
  discursiva e resultado) e confirma que não há rolagem horizontal nem elemento estourando.

`python testar.py --shots` gera também as capturas em `dist/screenshots/`.

---

## 10. Como o texto foi extraído dos PDFs

Registro do método, caso seja preciso reprocessar as provas no futuro.

Os PDFs do INEP usam fontes CID embaralhadas: a extração normal devolve `ĞŵƉƌĞƐĂ` em vez de
`empresa`. Os códigos dos caracteres são, na verdade, **glyph IDs da fonte Calibri**. O texto foi
recuperado mapeando cada glyph ID de volta ao caractere correto pela tabela da Calibri instalada no
Windows, com tratamento das ligaduras (`fi`, `ti`, `tí`, `tt`) que não têm correspondência direta.

Resultado: menos de 10 caracteres não resolvidos por prova (contra ~1.100 na extração bruta).

Os gabaritos de 2019 e 2023 saíam desalinhados no modo tabela do `pdftotext`; foram reextraídos em
modo bruto (`-raw`) e conferidos item a item. Os gabaritos das discursivas trazem `***` — o INEP
não os divulga.

---

## 11. Requisitos

- **Python 3** — apenas para rodar `build.py` e `testar.py`. O aplicativo em si não precisa de nada.
- **Chrome ou Edge** — apenas para `testar.py`.
- O aplicativo gerado roda em qualquer navegador moderno, sem instalação e sem internet.
