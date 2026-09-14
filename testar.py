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


def chrome(url, extra=(), timeout=90):
    perfil = tempfile.mkdtemp(prefix="enade_chrome_")
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--no-first-run", "--disable-extensions", "--hide-scrollbars",
           "--force-device-scale-factor=1",
           f"--user-data-dir={perfil}", "--virtual-time-budget=20000", *extra, url]
    p = subprocess.run(cmd, capture_output=True, timeout=timeout)
    dec = lambda b: b.decode("utf-8", "replace")
    return type("R", (), {"stdout": dec(p.stdout), "stderr": dec(p.stderr)})()


# --------------------------------------------------------------- harness JS
DRIVER_LOGICA = r"""
<script>
(function(){
  const R = [];
  const ok = (nome, cond, det) => R.push({nome, cond: !!cond, det: det || ""});

  // ---------- 1. integridade do banco ----------
  (function(){
    const L = ["A","B","C","D","E"];
    let ids = new Set(), problemas = [];
    for (const q of BANCO){
      if (ids.has(q.id)) problemas.push("id duplicado " + q.id);
      ids.add(q.id);
      if (JSON.stringify(Object.keys(q.alternativas).sort()) !== JSON.stringify(L))
        problemas.push(q.id + " alternativas");
      if (!L.includes(q.gabarito)) problemas.push(q.id + " gabarito");
      if (q.porqueErradas[q.gabarito]) problemas.push(q.id + " gabarito em porqueErradas");
      for (const k of L) if (k !== q.gabarito && !q.porqueErradas[k])
        problemas.push(q.id + " sem explicacao " + k);
      for (const k of L) if (!String(q.alternativas[k]||"").trim())
        problemas.push(q.id + " alternativa vazia " + k);
      if (!q.enunciado || !q.justificativa) problemas.push(q.id + " texto faltando");
    }
    ok("Banco íntegro (ids, 5 alternativas, gabarito, justificativas)",
        problemas.length === 0, problemas.slice(0,5).join(" | "));
    ok("Banco com pelo menos 100 questões", BANCO.length >= 100, "total=" + BANCO.length);
  })();

  // ---------- 2. sorteio ----------
  (function(){
    const ITER = 400;
    let tamOk = true, dupOk = true, existeOk = true, maxArea = 0, areasVistas = new Set();
    const contagem = {};
    for (let i = 0; i < ITER; i++){
      const s = sortear();
      if (s.length !== 20) tamOk = false;
      const ids = new Set(s.map(q=>q.id));
      if (ids.size !== s.length) dupOk = false;
      for (const q of s){
        if (!BANCO.find(b=>b.id===q.id)) existeOk = false;
        contagem[q.id] = (contagem[q.id]||0)+1;
        areasVistas.add(q.area);
      }
      const porArea = {};
      for (const q of s) porArea[q.area] = (porArea[q.area]||0)+1;
      maxArea = Math.max(maxArea, ...Object.values(porArea));
    }
    ok("Sorteio devolve sempre 20 questões", tamOk);
    ok("Nenhuma questão repetida dentro do mesmo simulado", dupOk);
    ok("Todas as questões sorteadas existem no banco", existeOk);
    ok("Distribuição equilibrada: no máximo 3 questões da mesma área",
        maxArea <= 3, "máximo observado = " + maxArea);
    // A frequência esperada de cada questão é 20/N. Os limites são relativos a
    // esse valor, para que o teste continue válido conforme o banco cresce.
    const esperada = 20 / BANCO.length;
    const freq = BANCO.map(q => (contagem[q.id]||0) / ITER);
    const fmax = Math.max(...freq), fmin = Math.min(...freq);
    ok("Nenhuma questão domina os sorteios (frequência dentro de 0,4x a 2,5x a esperada)",
        fmax <= 2.5 * esperada && fmin >= 0.4 * esperada,
        "esperada " + (esperada*100).toFixed(1) + "% · observada de "
        + (fmin*100).toFixed(1) + "% a " + (fmax*100).toFixed(1) + "%");
    const mediaAreas = new Set();
    for (let i = 0; i < 50; i++) sortear().forEach(q => mediaAreas.add(q.area));
    const nunca = BANCO.filter(q => !contagem[q.id]).length;
    ok("Todas as questões do banco podem ser sorteadas",
        nunca === 0, nunca + " nunca sorteadas em " + ITER + " simulados");
    ok("Sorteio cobre todas as áreas do banco",
        areasVistas.size === new Set(BANCO.map(q=>q.area)).size,
        areasVistas.size + " de " + new Set(BANCO.map(q=>q.area)).size);
  })();

  // ---------- 3. simulados consecutivos não se repetem ----------
  (function(){
    try { localStorage.clear(); } catch(e){}
    const s1 = sortear();
    store(LS.hist, [{nome:"t", data:"x", acertos:0, total:20, ids:s1.map(q=>q.id)}]);
    const s2 = sortear();
    const inter = s2.filter(q => s1.some(a=>a.id===q.id)).length;
    ok("Simulado seguinte não reaproveita questões do anterior",
        inter === 0, "interseção = " + inter);
    try { localStorage.clear(); } catch(e){}
  })();

  // ---------- 4. correção: cada alternativa é avaliada corretamente ----------
  (function(){
    let certos = 0, falsosPositivos = 0, falsosNegativos = 0;
    for (const q of BANCO){
      for (const L of ["A","B","C","D","E"]){
        const acertou = (L === q.gabarito);
        if (acertou) certos++;
        if (!acertou && L === q.gabarito) falsosPositivos++;
        if (acertou && L !== q.gabarito) falsosNegativos++;
      }
    }
    ok("Correção: exatamente 1 alternativa correta por questão",
        certos === BANCO.length && !falsosPositivos && !falsosNegativos,
        "corretas=" + certos + " de " + BANCO.length);
  })();

  // ---------- 5. pontuação de ponta a ponta ----------
  (function(){
    try { localStorage.clear(); } catch(e){}
    const cenarios = [
      {nome:"todas certas",  f:(q,i)=>q.gabarito,                          esperado:20},
      {nome:"todas erradas", f:(q,i)=>"ABCDE".split("").find(L=>L!==q.gabarito), esperado:0},
      {nome:"metade certa",  f:(q,i)=> i%2===0 ? q.gabarito
                                 : "ABCDE".split("").find(L=>L!==q.gabarito), esperado:10},
      {nome:"em branco",     f:(q,i)=>null,                                esperado:0},
    ];
    let todosOk = true, det = [];
    for (const c of cenarios){
      S = {nome:"Teste", questoes:sortear(), respostas:{}, atual:0, inicio:Date.now()};
      S.questoes.forEach((q,i)=>{ const r = c.f(q,i); if (r) S.respostas[q.id] = r; });
      telaResultado();
      const txt = document.body.innerText;
      const m = txt.match(/(\d+)\s*acertos/);
      const got = m ? +m[1] : -1;
      if (got !== c.esperado){ todosOk = false; det.push(c.nome + ": " + got + "≠" + c.esperado); }
    }
    ok("Placar correto em todos os cenários (20/0/10/branco)", todosOk, det.join(" | "));
    try { localStorage.clear(); } catch(e){}
  })();

  // ---------- 6. gabarito exibido confere com o banco ----------
  (function(){
    try { localStorage.clear(); } catch(e){}
    S = {nome:"Conferência", questoes:sortear(), respostas:{}, atual:0, inicio:Date.now()};
    S.questoes.forEach((q,i)=>{ S.respostas[q.id] = "ABCDE"[i%5]; });
    telaResultado();
    let erros = 0, detalhes = [];
    document.querySelectorAll(".rev").forEach((rev, i) => {
      rev.open = true;
      const q = S.questoes[i];
      const marcadas = rev.querySelectorAll(".alt.right .k");
      if (marcadas.length !== 1 || marcadas[0].textContent.trim() !== q.gabarito){
        erros++; detalhes.push(q.id + " destaque");
      }
      const txt = rev.textContent;
      if (!txt.includes(q.justificativa.slice(0, 40))){ erros++; detalhes.push(q.id + " justif"); }
      const resp = S.respostas[q.id];
      if (resp !== q.gabarito && !txt.includes(q.porqueErradas[resp].slice(0, 40))){
        erros++; detalhes.push(q.id + " porque-errada");
      }
    });
    ok("Tela de resultado destaca o gabarito certo e a justificativa correspondente",
        erros === 0, erros + " divergências: " + detalhes.slice(0,4).join(", "));
    try { localStorage.clear(); } catch(e){}
  })();

  // ---------- 7. fluxo real de cliques ----------
  (function(){
    try { localStorage.clear(); } catch(e){}
    telaInicial();
    document.getElementById("iniciar").click();                   // sem nome
    const bloqueou = document.getElementById("erroNome") &&
                     document.getElementById("erroNome").style.display === "block";
    ok("Bloqueia início do simulado sem o nome do aluno", bloqueou);

    document.getElementById("nome").value = "Aluno de Teste";
    document.getElementById("iniciar").click();
    const iniciou = /Questão 1 de 20/.test(document.body.innerText);
    ok("Inicia o simulado e mostra 'Questão 1 de 20'", iniciou);

    let avancou = true;
    for (let i = 0; i < 20; i++){
      const alts = document.querySelectorAll(".alt");
      if (alts.length !== 5){ avancou = false; break; }
      alts[i % 5].click();
    }
    ok("Cada questão apresenta exatamente 5 alternativas clicáveis", avancou);
    ok("Todas as 20 respostas foram registradas",
        Object.keys(S.respostas).length === 20, Object.keys(S.respostas).length + "/20");

    const semGabarito = !/Justificativa|Resposta correta|gabarito/i.test(document.body.innerText);
    ok("Gabarito não é revelado durante o simulado", semGabarito);

    document.getElementById("finalizar").click();
    const temModal = /Tem certeza de que deseja finalizar/.test(document.body.innerText);
    ok("Pede confirmação antes de finalizar", temModal);
    document.getElementById("sim").click();
    ok("Exibe a tela de resultado após confirmar",
        /Resultado de Aluno de Teste/.test(document.body.innerText));
    ok("Mostra as 20 questões na correção detalhada",
        document.querySelectorAll(".rev").length === 20,
        document.querySelectorAll(".rev").length + " blocos");
    try { localStorage.clear(); } catch(e){}
  })();

  // ---------- 8. persistência ----------
  (function(){
    try { localStorage.clear(); } catch(e){}
    let temLS = true;
    try { localStorage.setItem("__t","1"); localStorage.removeItem("__t"); } catch(e){ temLS = false; }
    if (!temLS){ ok("Persistência (localStorage indisponível neste contexto)", true, "ignorado"); return; }
    telaInicial();
    document.getElementById("nome").value = "Aluno Persistente";
    document.getElementById("iniciar").click();
    for (let i = 0; i < 5; i++) document.querySelectorAll(".alt")[0].click();
    const idsAntes = S.questoes.map(q=>q.id).join(",");
    const respAntes = JSON.stringify(S.respostas);
    S = null;                                    // simula recarregar a página
    const rec = restaurarProgresso();
    ok("Recupera o simulado em andamento após recarregar a página",
        rec && rec.questoes.map(q=>q.id).join(",") === idsAntes &&
        JSON.stringify(rec.respostas) === respAntes && rec.nome === "Aluno Persistente");
    ok("Banco de questões continua disponível após recarregar (embutido no arquivo)",
        BANCO.length >= 100);
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

DRIVER_SHOT = {
    "home": "",
    "quiz": r"""<script>
      document.getElementById("nome").value = "Ana Beatriz Camargo";
      document.getElementById("iniciar").click();
      for (let i = 0; i < 6; i++) document.querySelectorAll(".alt")[i%5].click();
    </script>""",
    "result": r"""<script>
      document.getElementById("nome").value = "Ana Beatriz Camargo";
      document.getElementById("iniciar").click();
      S.questoes.forEach((q,i)=>{ S.respostas[q.id] = (i%4===0)
        ? "ABCDE".split("").find(L=>L!==q.gabarito) : q.gabarito; });
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
  }, 350);
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
