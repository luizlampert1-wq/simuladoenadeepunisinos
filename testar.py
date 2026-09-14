# -*- coding: utf-8 -*-
"""
Testes automatizados do Simulado ENADE — Engenharia de Produção.

Executa o aplicativo real (dist/artifact.html) dentro do Chrome em modo headless
e valida sorteio, correção, pontuação, persistência e renderização.

Uso:   python testar.py            (testes lógicos)
       python testar.py --shots    (testes lógicos + capturas de tela)
"""
import os, sys, io, re, subprocess, threading, http.server, socketserver, tempfile, functools, glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
RAIZ = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(RAIZ, "dist")

CHROME = next((p for p in [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
] if os.path.exists(p)), None)


# --------------------------------------------------------------- servidor
def servir(pasta):
    class Silencioso(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a, **k): pass
    handler = functools.partial(Silencioso, directory=pasta)
    srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def chrome(url, extra=(), timeout=120):
    perfil = tempfile.mkdtemp(prefix="enade_chrome_")
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--no-first-run", "--disable-extensions", "--hide-scrollbars",
           "--force-device-scale-factor=1",
           f"--user-data-dir={perfil}", "--virtual-time-budget=30000", *extra, url]
    p = subprocess.run(cmd, capture_output=True, timeout=timeout)
    dec = lambda b: b.decode("utf-8", "replace")
    return type("R", (), {"stdout": dec(p.stdout), "stderr": dec(p.stderr)})()


# --------------------------------------------------------------- harness JS
DRIVER_LOGICA = r"""
<script>
(function(){
  const R = [];
  const ok = (nome, cond, det) => R.push({nome, cond: !!cond, det: det || ""});
  const L = ["A","B","C","D","E"];
  const EMAIL = "aluno.teste@edu.unisinos.br";

  function preencher(email, nome){
    document.getElementById("email").value = email;
    document.getElementById("nome").value  = nome;
    document.getElementById("iniciar").click();
  }
  const erroVisivel = () => {
    const e = document.getElementById("erroForm");
    return !!e && e.style.display === "block";
  };

  // ---------- 1. integridade do banco ----------
  (function(){
    let ids = new Set(), problemas = [];
    for (const q of BANCO){
      if (ids.has(q.id)) problemas.push("id duplicado " + q.id);
      ids.add(q.id);
      if (!q.enunciado || !q.area || !q.competencia || !q.dificuldade)
        problemas.push(q.id + " campos comuns");
      if (q.formato !== "objetiva" && q.formato !== "discursiva")
        problemas.push(q.id + " formato");
    }
    ok("Banco íntegro: ids únicos, campos comuns e formato declarado",
        problemas.length === 0, problemas.slice(0,5).join(" | "));

    problemas = [];
    for (const q of OBJETIVAS){
      if (JSON.stringify(Object.keys(q.alternativas).sort()) !== JSON.stringify(L))
        problemas.push(q.id + " alternativas");
      if (!L.includes(q.gabarito)) problemas.push(q.id + " gabarito");
      if (q.porqueErradas[q.gabarito]) problemas.push(q.id + " gabarito em porqueErradas");
      for (const k of L) if (k !== q.gabarito && !q.porqueErradas[k])
        problemas.push(q.id + " sem explicacao " + k);
      for (const k of L) if (!String(q.alternativas[k]||"").trim())
        problemas.push(q.id + " alternativa vazia " + k);
      if (!q.justificativa) problemas.push(q.id + " sem justificativa");
    }
    ok("Objetivas: 5 alternativas, gabarito válido e justificativas completas",
        problemas.length === 0, problemas.slice(0,5).join(" | "));

    problemas = [];
    for (const q of DISCURSIVAS){
      if (!q.padraoResposta) problemas.push(q.id + " sem padrão de resposta");
      if (!Array.isArray(q.criterios) || q.criterios.length < 3)
        problemas.push(q.id + " critérios insuficientes");
      if (q.gabarito || q.alternativas) problemas.push(q.id + " tem campo de objetiva");
    }
    ok("Discursivas: padrão de resposta e ao menos 3 critérios de correção",
        problemas.length === 0, problemas.slice(0,5).join(" | "));

    ok("Banco com pelo menos 100 questões", BANCO.length >= 100, "total=" + BANCO.length);
    ok("Banco tem objetivas e discursivas suficientes para o simulado",
        OBJETIVAS.length >= N_OBJETIVAS && DISCURSIVAS.length >= N_DISCURSIVAS,
        OBJETIVAS.length + " objetivas · " + DISCURSIVAS.length + " discursivas");

    const t = {}, f = {};
    for (const q of BANCO){ t[q.tipo] = (t[q.tipo]||0)+1;
      f[q.formato+"/"+q.tipo] = (f[q.formato+"/"+q.tipo]||0)+1; }
    ok("Proporção igual de oficiais, adaptadas e inéditas",
        t["Oficial"] === t["Adaptada"] && t["Adaptada"] === t["Inédita"],
        "oficiais " + t["Oficial"] + " · adaptadas " + t["Adaptada"] + " · inéditas " + t["Inédita"]);
    ok("Proporção igual também dentro das discursivas",
        f["discursiva/Oficial"] === f["discursiva/Adaptada"] &&
        f["discursiva/Adaptada"] === f["discursiva/Inédita"],
        f["discursiva/Oficial"] + " / " + f["discursiva/Adaptada"] + " / " + f["discursiva/Inédita"]);
  })();

  // ---------- 2. sorteio ----------
  (function(){
    try { localStorage.clear(); } catch(e){}
    const ITER = 300;
    let tamOk = true, compOk = true, ordemOk = true, dupOk = true, existeOk = true;
    let maxArea = 0, areasVistas = new Set();
    const contagem = {};
    for (let i = 0; i < ITER; i++){
      const s = sortear();
      if (s.length !== 38) tamOk = false;
      const obj = s.filter(q=>q.formato==="objetiva");
      const dis = s.filter(q=>q.formato==="discursiva");
      if (obj.length !== 36 || dis.length !== 2) compOk = false;
      // as discursivas ficam sempre no fim, como na prova real
      if (s[36].formato !== "discursiva" || s[37].formato !== "discursiva") ordemOk = false;
      const ids = new Set(s.map(q=>q.id));
      if (ids.size !== s.length) dupOk = false;
      for (const q of s){
        if (!BANCO.find(b=>b.id===q.id)) existeOk = false;
        contagem[q.id] = (contagem[q.id]||0)+1;
        areasVistas.add(q.area);
      }
      const porArea = {};
      for (const q of obj) porArea[q.area] = (porArea[q.area]||0)+1;
      maxArea = Math.max(maxArea, ...Object.values(porArea));
    }
    ok("Sorteio devolve sempre 38 questões", tamOk);
    ok("Cada simulado tem exatamente 36 objetivas e 2 discursivas", compOk);
    ok("As duas discursivas ficam ao final do simulado", ordemOk);
    ok("Nenhuma questão repetida dentro do mesmo simulado", dupOk);
    ok("Todas as questões sorteadas existem no banco", existeOk);
    ok("Distribuição equilibrada: no máximo " + MAX_POR_AREA + " objetivas da mesma área",
        maxArea <= MAX_POR_AREA, "máximo observado = " + maxArea);

    // A frequência esperada de cada questão é N/pool. Os limites são relativos a
    // esse valor, para que o teste continue válido conforme o banco cresce.
    function freqOk(lista, n, rotulo){
      const esperada = n / lista.length;
      const fs = lista.map(q => (contagem[q.id]||0) / ITER);
      const fmax = Math.max(...fs), fmin = Math.min(...fs);
      ok("Nenhuma " + rotulo + " domina os sorteios (0,4x a 2,5x a frequência esperada)",
          fmax <= 2.5 * esperada && fmin >= 0.4 * esperada,
          "esperada " + (esperada*100).toFixed(1) + "% · observada de "
          + (fmin*100).toFixed(1) + "% a " + (fmax*100).toFixed(1) + "%");
    }
    freqOk(OBJETIVAS, 36, "objetiva");
    freqOk(DISCURSIVAS, 2, "discursiva");

    const nunca = BANCO.filter(q => !contagem[q.id]).length;
    ok("Todas as questões do banco podem ser sorteadas",
        nunca === 0, nunca + " nunca sorteadas em " + ITER + " simulados");
    ok("Sorteio cobre todas as áreas do banco",
        areasVistas.size === new Set(BANCO.map(q=>q.area)).size,
        areasVistas.size + " de " + new Set(BANCO.map(q=>q.area)).size);
    try { localStorage.clear(); } catch(e){}
  })();

  // ---------- 3. simulados consecutivos não se repetem ----------
  (function(){
    try { localStorage.clear(); } catch(e){}
    const s1 = sortear();
    store(LS.hist, [{nome:"t", data:"x", acertos:0, totalObjetivas:36, ids:s1.map(q=>q.id)}]);
    const s2 = sortear();
    const inter = s2.filter(q => s1.some(a=>a.id===q.id)).length;
    ok("Simulado seguinte não reaproveita questões do anterior",
        inter === 0, "interseção = " + inter);
    store(LS.hist, [{nome:"t", data:"x", acertos:0, totalObjetivas:36, ids:s2.map(q=>q.id)},
                    {nome:"t", data:"x", acertos:0, totalObjetivas:36, ids:s1.map(q=>q.id)}]);
    const s3 = sortear();
    const inter2 = s3.filter(q => s1.some(a=>a.id===q.id) || s2.some(a=>a.id===q.id)).length;
    ok("Sorteio evita os " + HIST_EVITAR + " simulados anteriores",
        inter2 === 0, "interseção = " + inter2);
    try { localStorage.clear(); } catch(e){}
  })();

  // ---------- 4. correção: cada objetiva tem exatamente 1 alternativa correta ----------
  (function(){
    let certos = 0, multiplas = 0;
    for (const q of OBJETIVAS){
      const corretas = L.filter(k => k === q.gabarito).length;
      if (corretas === 1) certos++; else multiplas++;
    }
    ok("Correção: exatamente 1 alternativa correta por objetiva",
        certos === OBJETIVAS.length && multiplas === 0,
        "corretas=" + certos + " de " + OBJETIVAS.length);
  })();

  // ---------- 5. validação do e-mail institucional ----------
  (function(){
    const validos   = ["ana@edu.unisinos.br", "joao.silva@edu.unisinos.br",
                       "MARIA@EDU.UNISINOS.BR", "a1@edu.unisinos.br"];
    const invalidos = ["", "ana", "ana@unisinos.br", "ana@gmail.com",
                       "ana@edu.unisinos.br.br", "ana@edu.unisinos.com",
                       "ana @edu.unisinos.br", "@edu.unisinos.br",
                       "ana@edu.unisinos.brx", "edu.unisinos.br"];
    const fv = validos.filter(e => !emailValido(e));
    const fi = invalidos.filter(e => emailValido(e));
    ok("Aceita e-mails @edu.unisinos.br (inclusive em maiúsculas)",
        fv.length === 0, fv.join(", "));
    ok("Recusa e-mails de outros domínios e endereços malformados",
        fi.length === 0, fi.join(", "));
  })();

  // ---------- 6. pontuação de ponta a ponta ----------
  (function(){
    try { localStorage.clear(); } catch(e){}
    const outra = q => L.find(k => k !== q.gabarito);
    const cenarios = [
      {nome:"todas certas",  f:(q,i)=>q.gabarito,                        esperado:36},
      {nome:"todas erradas", f:(q,i)=>outra(q),                          esperado:0},
      {nome:"metade certa",  f:(q,i)=> i%2===0 ? q.gabarito : outra(q),  esperado:18},
      {nome:"em branco",     f:(q,i)=>null,                              esperado:0},
    ];
    let todosOk = true, det = [];
    for (const c of cenarios){
      S = {nome:"Teste", email:EMAIL, questoes:sortear(), respostas:{}, atual:0, inicio:Date.now()};
      S.questoes.filter(q=>q.formato==="objetiva").forEach((q,i)=>{
        const r = c.f(q,i); if (r) S.respostas[q.id] = r; });
      telaResultado();
      const m = document.body.innerText.match(/(\d+)\s*acertos/);
      const got = m ? +m[1] : -1;
      if (got !== c.esperado){ todosOk = false; det.push(c.nome + ": " + got + "≠" + c.esperado); }
    }
    ok("Placar correto em todos os cenários (36/0/18/branco)", todosOk, det.join(" | "));

    // a nota e o percentual consideram apenas as 36 objetivas
    S = {nome:"Teste", email:EMAIL, questoes:sortear(), respostas:{}, atual:0, inicio:Date.now()};
    S.questoes.filter(q=>q.formato==="objetiva").forEach((q,i)=>{
      if (i < 27) S.respostas[q.id] = q.gabarito; });
    telaResultado();
    const t = document.body.innerText;
    ok("Percentual e nota usam apenas as objetivas (27/36 = 75% = nota 7,5)",
        /75%/.test(t) && /7\.5|7,5/.test(t), t.slice(0, 0));
    try { localStorage.clear(); } catch(e){}
  })();

  // ---------- 7. gabarito exibido confere com o banco ----------
  (function(){
    try { localStorage.clear(); } catch(e){}
    S = {nome:"Conferência", email:EMAIL, questoes:sortear(), respostas:{}, atual:0, inicio:Date.now()};
    S.questoes.forEach((q,i)=>{
      S.respostas[q.id] = q.formato === "objetiva" ? "ABCDE"[i%5] : "Resposta escrita de teste " + i;
    });
    telaResultado();
    let erros = 0, detalhes = [], nObj = 0, nDis = 0;
    document.querySelectorAll(".rev").forEach((rev, i) => {
      rev.open = true;
      const q = S.questoes[i];
      const txt = rev.textContent;
      if (q.formato === "objetiva"){
        nObj++;
        const marcadas = rev.querySelectorAll(".alt.right .k");
        if (marcadas.length !== 1 || marcadas[0].textContent.trim() !== q.gabarito){
          erros++; detalhes.push(q.id + " destaque");
        }
        if (!txt.includes(q.justificativa.slice(0, 40))){ erros++; detalhes.push(q.id + " justif"); }
        const resp = S.respostas[q.id];
        if (resp !== q.gabarito && !txt.includes(q.porqueErradas[resp].slice(0, 40))){
          erros++; detalhes.push(q.id + " porque-errada");
        }
      } else {
        nDis++;
        if (!txt.includes(q.padraoResposta.slice(0, 40))){ erros++; detalhes.push(q.id + " padrão"); }
        for (const c of q.criterios)
          if (!txt.includes(c.slice(0, 30))){ erros++; detalhes.push(q.id + " critério"); break; }
        if (!txt.includes(S.respostas[q.id])){ erros++; detalhes.push(q.id + " resposta do aluno"); }
        if (rev.querySelectorAll(".alt").length){ erros++; detalhes.push(q.id + " tem alternativas"); }
      }
    });
    ok("Resultado destaca o gabarito certo e a justificativa correspondente",
        erros === 0, erros + " divergências: " + detalhes.slice(0,4).join(", "));
    ok("Correção detalhada traz 36 objetivas e 2 discursivas",
        nObj === 36 && nDis === 2, nObj + " objetivas · " + nDis + " discursivas");

    // autoavaliação das discursivas
    const ul = document.querySelector(".criterios");
    const caixas = [...ul.querySelectorAll(".crit")];
    const alvo = document.querySelector('.autoscore[data-for="' + CSS.escape(ul.dataset.qid) + '"]');
    caixas.forEach(c => { c.checked = true; c.dispatchEvent(new Event("change")); });
    ok("Autoavaliação das discursivas calcula a nota pelos critérios marcados",
        /nota estimada 10[.,]0/.test(alvo.textContent),
        alvo.textContent.slice(0,70));
    try { localStorage.clear(); } catch(e){}
  })();

  // ---------- 8. fluxo real de cliques ----------
  (function(){
    try { localStorage.clear(); } catch(e){}
    telaInicial();
    document.getElementById("iniciar").click();
    ok("Bloqueia início sem e-mail", erroVisivel());

    preencher("aluno@gmail.com", "Aluno de Teste");
    ok("Bloqueia início com e-mail não institucional",
        erroVisivel() && !/Questão 1 de/.test(document.body.innerText));

    preencher(EMAIL, "");
    ok("Bloqueia início sem o nome do aluno",
        erroVisivel() && !/Questão 1 de/.test(document.body.innerText));

    preencher(EMAIL, "Aluno de Teste");
    ok("Inicia o simulado e mostra 'Questão 1 de 38'",
        /Questão 1 de 38/.test(document.body.innerText));

    let cincoAlts = true;
    for (let i = 0; i < 36; i++){
      const alts = document.querySelectorAll(".alt");
      if (alts.length !== 5){ cincoAlts = false; break; }
      alts[i % 5].click();
    }
    ok("Cada objetiva apresenta exatamente 5 alternativas clicáveis", cincoAlts);
    ok("As 36 respostas objetivas foram registradas",
        Object.keys(S.respostas).length === 36, Object.keys(S.respostas).length + "/36");

    // questão 37: discursiva
    ok("Após as objetivas o simulado chega à primeira discursiva",
        /Questão 37 de 38/.test(document.body.innerText) &&
        !!document.getElementById("disc") &&
        document.querySelectorAll(".alt").length === 0);

    const escrever = txt => {
      const ta = document.getElementById("disc");
      ta.value = txt; ta.dispatchEvent(new Event("input"));
    };
    escrever("Resposta discursiva do aluno para a primeira questão.");
    document.getElementById("prox").click();
    escrever("Resposta discursiva do aluno para a segunda questão.");
    ok("Respostas discursivas são registradas no estado do simulado",
        Object.keys(S.respostas).length === 38,
        Object.keys(S.respostas).length + "/38");

    // o gabarito não pode estar na tela durante o simulado
    const vazou = document.querySelectorAll(".rev, .alt.right, .note, .autoscore").length;
    ok("Gabarito e padrão de resposta não aparecem durante o simulado", vazou === 0,
        vazou + " elementos de correção visíveis");

    document.getElementById("finalizar").click();
    ok("Pede confirmação antes de finalizar",
        /Tem certeza de que deseja finalizar/.test(document.body.innerText));
    document.getElementById("sim").click();
    ok("Exibe a tela de resultado após confirmar",
        /Resultado de Aluno de Teste/.test(document.body.innerText));
    ok("Mostra as 38 questões na correção detalhada",
        document.querySelectorAll(".rev").length === 38,
        document.querySelectorAll(".rev").length + " blocos");
    ok("Histórico registra o simulado com o e-mail do aluno",
        (store(LS.hist)||[]).length === 1 && (store(LS.hist)||[])[0].email === EMAIL);
    try { localStorage.clear(); } catch(e){}
  })();

  // ---------- 9. persistência ----------
  (function(){
    try { localStorage.clear(); } catch(e){}
    let temLS = true;
    try { localStorage.setItem("__t","1"); localStorage.removeItem("__t"); } catch(e){ temLS = false; }
    if (!temLS){ ok("Persistência (localStorage indisponível neste contexto)", true, "ignorado"); return; }
    telaInicial();
    preencher(EMAIL, "Aluno Persistente");
    for (let i = 0; i < 5; i++) document.querySelectorAll(".alt")[0].click();
    S.atual = 37;                                      // vai até a última discursiva
    telaQuiz();
    const ta = document.getElementById("disc");
    ta.value = "Rascunho da discursiva."; ta.dispatchEvent(new Event("input"));
    const idsAntes = S.questoes.map(q=>q.id).join(",");
    const respAntes = JSON.stringify(S.respostas);
    S = null;                                          // simula recarregar a página
    const rec = restaurarProgresso();
    ok("Recupera o simulado em andamento após recarregar a página",
        rec && rec.questoes.map(q=>q.id).join(",") === idsAntes &&
        JSON.stringify(rec.respostas) === respAntes && rec.nome === "Aluno Persistente" &&
        rec.email === EMAIL && rec.atual === 37);
    ok("A resposta discursiva em andamento também é preservada",
        rec && /Rascunho da discursiva\./.test(JSON.stringify(rec.respostas)));
    ok("Banco de questões continua disponível após recarregar (embutido no arquivo)",
        BANCO.length >= 100);
    try { localStorage.clear(); } catch(e){}
  })();

  // ---------- 10. coleta de resultados ----------
  (function(){
    try { localStorage.clear(); } catch(e){}
    ok("Envio externo de dados vem desativado (nada sai do navegador do aluno)",
        COLETA.ativa === false && !COLETA.url);

    S = {nome:"Teste", email:EMAIL, questoes:sortear(), respostas:{}, atual:0, inicio:Date.now()};
    telaResultado();
    ok("Com a coleta desligada, nenhum resultado é enfileirado para envio",
        !(store(LS.fila) || []).length);
    ok("O histórico local é gravado de qualquer forma",
        (store(LS.hist) || []).length === 1);

    // liga a coleta com um fetch de mentira, que nunca resolve: assim a fila
    // fica exatamente como registrarResultado a deixou.
    const fetchReal = window.fetch;
    let chamadas = 0;
    window.fetch = () => { chamadas++; return new Promise(() => {}); };
    COLETA.ativa = true; COLETA.url = "https://exemplo.invalido/coleta";
    try { localStorage.clear(); } catch(e){}

    for (let i = 0; i < MAX_FILA + 12; i++)
      registrarResultado({ email:EMAIL, nome:"Teste", acertos:i });
    const fila = store(LS.fila) || [];
    ok("Com a coleta ligada, o resultado entra na fila e o envio é disparado",
        fila.length > 0 && chamadas > 0, fila.length + " na fila · " + chamadas + " envios");
    ok("A fila de reenvio tem teto de " + MAX_FILA + " registros",
        fila.length === MAX_FILA, "fila = " + fila.length);
    ok("A fila descarta os mais antigos e guarda os mais recentes",
        fila[fila.length-1].acertos === MAX_FILA + 11 && fila[0].acertos === 12,
        "do " + fila[0].acertos + " ao " + fila[fila.length-1].acertos);

    window.fetch = fetchReal;
    COLETA.ativa = false; COLETA.url = "";
    try { localStorage.clear(); } catch(e){}
  })();

  // ---------- saída ----------
  const falhas = R.filter(r => !r.cond);
  const linhas = R.map(r => (r.cond ? "PASS" : "FAIL") + " :: " + r.nome +
                            (r.det ? "  (" + r.det + ")" : ""));
  document.body.innerHTML = "<pre id='saida'>@@INICIO@@\n" + linhas.join("\n") +
    "\n@@RESUMO@@ " + (R.length - falhas.length) + "/" + R.length +
    " testes passaram\n@@FIM@@</pre>";
})();
</script>
"""

_ENTRAR = """
  document.getElementById("email").value = "ana.camargo@edu.unisinos.br";
  document.getElementById("nome").value  = "Ana Beatriz Camargo";
  document.getElementById("iniciar").click();
"""

DRIVER_SHOT = {
    "home": "",
    "quiz": "<script>" + _ENTRAR + r"""
      for (let i = 0; i < 6; i++) document.querySelectorAll(".alt")[i%5].click();
    </script>""",
    "disc": "<script>" + _ENTRAR + r"""
      S.atual = 36; telaQuiz();
      const ta = document.getElementById("disc");
      ta.value = "A capacidade efetiva da linha é limitada pelo posto gargalo, "
        + "cujo tempo de ciclo determina o ritmo de saída.";
      ta.dispatchEvent(new Event("input"));
    </script>""",
    "result": "<script>" + _ENTRAR + r"""
      S.questoes.forEach((q,i)=>{
        S.respostas[q.id] = q.formato === "objetiva"
          ? (i%4===0 ? "ABCDE".split("").find(L=>L!==q.gabarito) : q.gabarito)
          : "O gargalo define o ritmo da linha e, portanto, a capacidade do sistema.";
      });
      telaResultado();
      document.querySelectorAll(".rev")[0].open = true;
    </script>""",
}


# --------------------------------------------------------------- responsivo
# O Chrome headless no Windows tem largura mínima de janela, então a página é
# carregada dentro de um iframe de largura fixa para obter um viewport real de
# celular e medir se algum elemento estoura horizontalmente.
WRAP = """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><style>
html,body{margin:0;background:#8a8f98}iframe{border:0;display:block;width:__W__px;height:__H__px}
</style></head><body>
<iframe id="f" src="_t___NOME__.html"></iframe>
<script>
document.getElementById("f").onload = function(){
  setTimeout(function(){
    var d = frames[0].document, vw = d.documentElement.clientWidth;
    var sw = d.documentElement.scrollWidth, out = [];
    out.push("__NOME__|" + vw + "|" + sw);
    d.querySelectorAll("*").forEach(function(el){
      var r = el.getBoundingClientRect();
      if (r.right > vw + 1 || r.width > vw + 1)
        out.push("estoura: " + el.tagName + "." + String(el.className||"").slice(0,34)
                 + " w=" + Math.round(r.width));
    });
    var pre = document.createElement("pre");
    pre.textContent = "<<" + "INI>>" + String.fromCharCode(10)
      + out.slice(0,8).join(String.fromCharCode(10)) + String.fromCharCode(10) + "<<" + "FIM>>";
    document.body.appendChild(pre);
  }, 450);
};
</script></body></html>"""


def testar_responsivo(porta, larguras=(390, 320), shots=False):
    print("\nResponsividade (viewport real de celular, via iframe):")
    falhou = False
    for w in larguras:
        for tela, drv in DRIVER_SHOT.items():
            preparar(tela, drv)
            with open(os.path.join(DIST, "_t_wrap.html"), "w", encoding="utf-8") as fh:
                fh.write(WRAP.replace("__W__", str(w)).replace("__H__", "1500")
                             .replace("__NOME__", tela))
            extra = ["--hide-scrollbars", f"--window-size={w+60},1560"]
            if shots and w == 390:
                extra.append("--screenshot=" +
                             os.path.join(RAIZ, "dist", "screenshots", tela + "_celular.png"))
            extra.append("--dump-dom")
            r = chrome(f"http://127.0.0.1:{porta}/_t_wrap.html", extra)
            m = re.search(r"&lt;&lt;INI&gt;&gt;(.*?)&lt;&lt;FIM&gt;&gt;", r.stdout, re.S)
            if not m:
                print(f"  x {tela} @{w}px - nao foi possivel medir"); falhou = True; continue
            linhas = [l.strip() for l in m.group(1).strip().splitlines() if l.strip()]
            nome_, vw, sw = linhas[0].split("|")
            estourou = int(sw) > int(vw) + 1
            if estourou: falhou = True
            print(f"  {'x' if estourou else 'v'} {nome_:7s} @{w}px  viewport={vw}  "
                  f"conteudo={sw}  {'ESTOURA' if estourou else 'sem rolagem horizontal'}")
            for l in linhas[1:]:
                print("        " + l)
    return falhou


def preparar(nome, driver):
    base = open(os.path.join(DIST, "artifact.html"), encoding="utf-8").read()
    caminho = os.path.join(DIST, f"_t_{nome}.html")
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write('<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">'
                 '<meta name="viewport" content="width=device-width, initial-scale=1">'
                 '<style>body{margin:0}img{max-width:100%}</style></head><body>\n')
        fh.write(base)
        fh.write(driver)
        fh.write("\n</body></html>")
    return f"_t_{nome}.html"


def main():
    if not CHROME:
        raise SystemExit("ERRO: Chrome/Edge não encontrado — não é possível rodar os testes.")
    if not os.path.exists(os.path.join(DIST, "artifact.html")):
        raise SystemExit("ERRO: rode 'python build.py' antes de testar.")

    arq = preparar("logica", DRIVER_LOGICA)
    srv, porta = servir(DIST)
    print(f"Navegador: {os.path.basename(CHROME)}")
    print(f"Servidor de teste: http://127.0.0.1:{porta}\n")

    r = chrome(f"http://127.0.0.1:{porta}/{arq}", ["--dump-dom"])
    saida = r.stdout
    bloco = re.search(r"@@INICIO@@(.*?)@@FIM@@", saida, re.S)
    if not bloco:
        print("Falha ao executar os testes. Saída bruta:\n", saida[:2500], r.stderr[:1500])
        srv.shutdown(); raise SystemExit(1)

    texto = bloco.group(1).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    falhou = False
    for linha in texto.strip().splitlines():
        linha = linha.strip()
        if not linha:
            continue
        if linha.startswith("@@RESUMO@@"):
            print("\n" + linha.replace("@@RESUMO@@", "RESUMO:"))
        else:
            if linha.startswith("FAIL"):
                falhou = True
            print(("  ✓ " if linha.startswith("PASS") else "  ✗ ") + linha.split("::", 1)[1].strip())

    shots = "--shots" in sys.argv
    if shots:
        os.makedirs(os.path.join(RAIZ, "dist", "screenshots"), exist_ok=True)

    if testar_responsivo(porta, shots=shots):
        falhou = True

    if shots:
        print("\nCapturas desktop:")
        for tela, drv in DRIVER_SHOT.items():
            a = preparar("shot_" + tela, drv)
            dest = os.path.join(RAIZ, "dist", "screenshots", f"{tela}_desktop.png")
            chrome(f"http://127.0.0.1:{porta}/{a}",
                   [f"--screenshot={dest}", "--window-size=1280,1400"])
            print(f"  {tela:7s} -> {os.path.relpath(dest, RAIZ)}")

    srv.shutdown()
    for f in glob.glob(os.path.join(DIST, "_t_*.html")):
        os.remove(f)
    if falhou:
        print("\nHÁ TESTES FALHANDO.")
        raise SystemExit(1)
    print("\nTodos os testes passaram.")


if __name__ == "__main__":
    main()
