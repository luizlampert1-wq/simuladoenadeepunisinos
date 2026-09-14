# -*- coding: utf-8 -*-
"""
Build do Simulado ENADE — Engenharia de Produção.

Lê todos os arquivos de banco/*.json, embute as figuras de figuras/*.png
como data URI, ofusca o banco e gera dois arquivos em dist/:

  dist/simulado-enade-ep.html   -> arquivo único, abre com duplo clique (offline)
  dist/artifact.html            -> mesmo conteúdo, sem <html>/<head>/<body>,
                                   para publicar como Artifact / hospedar

Uso:   python build.py
"""
import base64, glob, json, os, sys, io, collections, datetime, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
RAIZ = os.path.dirname(os.path.abspath(__file__))
CHAVE = "enade-ep-unisinos"
LETRAS = list("ABCDE")


# ----------------------------------------------------------------- carregar
def carregar_banco():
    banco, origem = [], {}
    arquivos = sorted(glob.glob(os.path.join(RAIZ, "banco", "*.json")))
    if not arquivos:
        raise SystemExit("ERRO: nenhum arquivo encontrado em banco/*.json")
    for caminho in arquivos:
        with open(caminho, encoding="utf-8") as fh:
            try:
                dados = json.load(fh)
            except json.JSONDecodeError as e:
                raise SystemExit(f"ERRO de JSON em {os.path.basename(caminho)}: {e}")
        if not isinstance(dados, list):
            raise SystemExit(f"ERRO: {os.path.basename(caminho)} deve conter uma lista de questões.")
        for q in dados:
            origem[q.get("id")] = os.path.basename(caminho)
        banco += dados
    return banco, origem


# ----------------------------------------------------------------- validar
def validar(banco, origem):
    """Valida o banco e marca cada questão com seu formato.

    O formato é deduzido do conteúdo, não precisa ser declarado:
      - tem "alternativas"   -> objetiva
      - tem "padraoResposta" -> discursiva
    """
    erros, avisos = [], []
    comuns = ["id", "tipo", "area", "dificuldade", "competencia", "enunciado"]
    vistos = {}
    for q in banco:
        qid = q.get("id", "<sem id>")
        onde = origem.get(qid, "?")
        tag = f"[{onde}] {qid}"

        for campo in comuns:
            if not q.get(campo):
                erros.append(f"{tag}: campo obrigatório ausente ou vazio -> {campo}")

        if qid in vistos:
            erros.append(f"{tag}: id duplicado (também em {vistos[qid]})")
        vistos[qid] = onde

        # ---- formato ----
        tem_alt = bool(q.get("alternativas"))
        tem_pad = bool(q.get("padraoResposta"))
        if tem_alt and tem_pad:
            erros.append(f"{tag}: tem 'alternativas' e 'padraoResposta' — escolha um dos dois formatos")
            continue
        if not tem_alt and not tem_pad:
            erros.append(f"{tag}: precisa ter 'alternativas' (objetiva) ou 'padraoResposta' (discursiva)")
            continue
        q["formato"] = "objetiva" if tem_alt else "discursiva"

        if q["formato"] == "objetiva":
            alts = q.get("alternativas") or {}
            if sorted(alts) != LETRAS:
                erros.append(f"{tag}: precisa ter exatamente as alternativas A, B, C, D e E")
            for L in LETRAS:
                if L in alts and not str(alts[L]).strip():
                    erros.append(f"{tag}: alternativa {L} está vazia")

            gab = q.get("gabarito")
            if gab not in LETRAS:
                erros.append(f"{tag}: gabarito inválido ({gab!r}) — use A, B, C, D ou E")

            pq = q.get("porqueErradas") or {}
            if gab in pq:
                erros.append(f"{tag}: o gabarito {gab} não deve aparecer em porqueErradas")
            faltando = [L for L in LETRAS if L != gab and L not in pq]
            if faltando:
                avisos.append(f"{tag}: sem explicação para {', '.join(faltando)}")
            if not q.get("justificativa"):
                erros.append(f"{tag}: questão objetiva sem 'justificativa'")
        else:
            crit = q.get("criterios")
            if not isinstance(crit, list) or len(crit) < 3:
                erros.append(f"{tag}: questão discursiva precisa de 'criterios' com pelo menos 3 itens")
            for campo in ("gabarito", "alternativas", "porqueErradas"):
                if q.get(campo):
                    erros.append(f"{tag}: questão discursiva não deve ter o campo '{campo}'")
            if not q.get("valor"):
                avisos.append(f"{tag}: questão discursiva sem o campo 'valor' (pontuação)")

        if q.get("tipo") not in ("Oficial", "Adaptada", "Inédita"):
            erros.append(f"{tag}: tipo deve ser Oficial, Adaptada ou Inédita")
        if q.get("tipo") == "Oficial" and not q.get("ano"):
            avisos.append(f"{tag}: questão oficial sem o ano da prova")

        fig = q.get("figura")
        if fig and not os.path.exists(os.path.join(RAIZ, "figuras", fig)):
            erros.append(f"{tag}: figura não encontrada -> figuras/{fig}")

    # ---- composição: o simulado exige 36 objetivas + 2 discursivas ----
    obj = [q for q in banco if q.get("formato") == "objetiva"]
    dis = [q for q in banco if q.get("formato") == "discursiva"]
    if len(obj) < 36:
        erros.append(f"banco: apenas {len(obj)} questões objetivas — o simulado exige 36")
    if len(dis) < 2:
        erros.append(f"banco: apenas {len(dis)} questões discursivas — o simulado exige 2")

    return erros, avisos


# ----------------------------------------------------------------- coleta
def carregar_coleta():
    """Lê coleta.json — a configuração do envio dos resultados.

    Fica fora do app de propósito: ligar a coleta é editar dois campos de um
    JSON, não mexer em HTML."""
    caminho = os.path.join(RAIZ, "coleta.json")
    if not os.path.exists(caminho):
        return {"ativa": False, "url": ""}
    with open(caminho, encoding="utf-8") as fh:
        try:
            cfg = json.load(fh)
        except json.JSONDecodeError as e:
            raise SystemExit(f"ERRO de JSON em coleta.json: {e}")

    ativa = bool(cfg.get("ativa"))
    url = str(cfg.get("url") or "").strip()
    modo = str(cfg.get("modo") or "cors").strip()
    if ativa and not url:
        raise SystemExit("ERRO: coleta.json está com \"ativa\": true e \"url\" vazia.")
    if ativa and not url.startswith("https://"):
        raise SystemExit(f"ERRO: a url da coleta precisa começar com https:// (veio {url!r})")
    if modo not in ("cors", "no-cors"):
        raise SystemExit(f"ERRO: \"modo\" em coleta.json deve ser \"cors\" ou \"no-cors\" (veio {modo!r})")
    return {"ativa": ativa, "url": url, "modo": modo}


# ----------------------------------------------------------------- figuras
def embutir_figuras(banco):
    cache, total = {}, 0
    for q in banco:
        fig = q.pop("figura", None)
        if not fig:
            continue
        if fig not in cache:
            caminho = os.path.join(RAIZ, "figuras", fig)
            with open(caminho, "rb") as fh:
                cache[fig] = "data:image/png;base64," + base64.b64encode(fh.read()).decode()
            total += os.path.getsize(caminho)
        q["figuraData"] = cache[fig]
    return len(cache), total


# ----------------------------------------------------------------- ofuscar
def ofuscar(banco):
    """XOR + base64: evita que o gabarito seja lido a olho nu no código-fonte.
    É ofuscação, não criptografia — em app 100% client-side o gabarito
    precisa estar no navegador para a correção funcionar sem servidor."""
    bruto = json.dumps(banco, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    k = CHAVE.encode("utf-8")
    misturado = bytes(b ^ k[i % len(k)] for i, b in enumerate(bruto))
    return base64.b64encode(misturado).decode("ascii")


# ----------------------------------------------------------------- gerar
def main():
    banco, origem = carregar_banco()
    erros, avisos = validar(banco, origem)

    print(f"Questões carregadas: {len(banco)}")
    for a in avisos:
        print("  aviso:", a)
    if erros:
        print("\nFALHOU — corrija os problemas abaixo:")
        for e in erros:
            print("  erro:", e)
        raise SystemExit(1)

    tipos = collections.Counter(q["tipo"] for q in banco)
    areas = collections.Counter(q["area"] for q in banco)
    fmts  = collections.Counter(q["formato"] for q in banco)
    print(f"  oficiais {tipos['Oficial']} · adaptadas {tipos['Adaptada']} · inéditas {tipos['Inédita']}")
    print(f"  objetivas {fmts['objetiva']} · discursivas {fmts['discursiva']}")
    print(f"  áreas: {len(areas)}")
    for f in ("objetiva", "discursiva"):
        t = collections.Counter(q["tipo"] for q in banco if q["formato"] == f)
        print(f"    {f:11s} oficiais {t['Oficial']:3d} · adaptadas {t['Adaptada']:3d} · inéditas {t['Inédita']:3d}")

    n_figs, bytes_figs = embutir_figuras(banco)
    print(f"  figuras embutidas: {n_figs} ({bytes_figs/1024:.0f} KB)")

    payload = ofuscar(banco)
    info = {"data": datetime.date.today().strftime("%d/%m/%Y"),
            "total": len(banco), "versao": 1}

    with open(os.path.join(RAIZ, "app", "index.html"), encoding="utf-8") as fh:
        corpo = fh.read()
    coleta = carregar_coleta()
    print("  coleta de resultados: " +
          (f"ATIVA -> {coleta['url']}" if coleta["ativa"]
           else "desativada (os dados ficam só no navegador do aluno)"))

    corpo = corpo.replace("__BANCO__", payload)
    corpo = corpo.replace("__BUILD__", json.dumps(info, ensure_ascii=False))
    corpo = corpo.replace("__COLETA__", json.dumps(coleta, ensure_ascii=False))

    os.makedirs(os.path.join(RAIZ, "dist"), exist_ok=True)

    # 1) versão autônoma (duplo clique)
    titulo = re.search(r"<title>(.*?)</title>", corpo).group(1)
    standalone = (
        "<!DOCTYPE html>\n<html lang=\"pt-BR\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{titulo}</title>\n"
        "<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n"
        "</head>\n<body>\n" + corpo + "\n</body>\n</html>\n"
    )
    p1 = os.path.join(RAIZ, "dist", "simulado-enade-ep.html")
    with open(p1, "w", encoding="utf-8") as fh:
        fh.write(standalone)

    # 2) versão para publicação (Artifact injeta o esqueleto)
    p2 = os.path.join(RAIZ, "dist", "artifact.html")
    with open(p2, "w", encoding="utf-8") as fh:
        fh.write(corpo)

    # 3) index.html na raiz — é o arquivo que o GitHub Pages publica
    p3 = os.path.join(RAIZ, "index.html")
    with open(p3, "w", encoding="utf-8") as fh:
        fh.write(standalone)

    # 4) pasta pronta para arrastar no Netlify Drop
    os.makedirs(os.path.join(RAIZ, "dist", "publicar"), exist_ok=True)
    p4 = os.path.join(RAIZ, "dist", "publicar", "index.html")
    with open(p4, "w", encoding="utf-8") as fh:
        fh.write(standalone)

    print(f"\nGerado: dist/simulado-enade-ep.html  ({os.path.getsize(p1)/1024:.0f} KB)  distribuição por arquivo")
    print(f"Gerado: dist/artifact.html           ({os.path.getsize(p2)/1024:.0f} KB)  claude.ai")
    print(f"Gerado: index.html                   ({os.path.getsize(p3)/1024:.0f} KB)  GitHub Pages")
    print(f"Gerado: dist/publicar/index.html     ({os.path.getsize(p4)/1024:.0f} KB)  Netlify Drop")
    print("\nOK — abra dist/simulado-enade-ep.html no navegador para testar.")


if __name__ == "__main__":
    main()
