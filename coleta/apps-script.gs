/**
 * Coleta de resultados do Simulado ENADE — Engenharia de Produção.
 *
 * Recebe um resultado por POST e grava uma linha na primeira aba da planilha.
 * A planilha vira a base que você abre no Excel (veja a seção 7 do README).
 *
 * Instalação, em 4 passos:
 *   1. Crie uma planilha nova no Google Drive.
 *   2. Extensões -> Apps Script. Apague o conteúdo e cole este arquivo inteiro.
 *   3. Implantar -> Nova implantação -> Aplicativo da Web
 *        Executar como:      Eu (sua conta)
 *        Quem pode acessar:  Qualquer pessoa
 *      Copie a URL que termina em /exec.
 *   4. Cole essa URL em coleta.json, mude "ativa" para true e rode:
 *        python build.py && python testar.py
 *
 * Para conferir se ficou de pé, abra a URL no navegador: deve responder
 * "Coleta do Simulado ENADE ativa."
 *
 * ATENÇÃO: a URL fica visível no código da página publicada. Qualquer pessoa
 * que a encontre pode enviar linhas. Por isso o script recusa e-mails fora do
 * domínio institucional — e, se aparecer lixo, basta apagar a linha.
 */

var DOMINIO = /^[^\s@]+@edu\.unisinos\.br$/i;

var COLUNAS = [
  'Recebido em', 'Data do simulado', 'E-mail', 'Nome',
  'Acertos', 'Total objetivas', 'Percentual (%)', 'Nota (0-10)',
  'Discursivas respondidas', 'Total discursivas', 'Minutos',
  'Desempenho por área', 'Questões sorteadas'
];

function doGet() {
  return ContentService.createTextOutput(
    'Coleta do Simulado ENADE ativa. Os resultados chegam por POST.');
}

function doPost(e) {
  var trava = LockService.getScriptLock();
  // 40 alunos terminando ao mesmo tempo gravariam por cima uns dos outros
  // sem esta trava.
  if (!trava.tryLock(30000)) {
    return ContentService.createTextOutput('ocupado, tente de novo');
  }
  try {
    var d = JSON.parse(e.postData.contents);

    if (!DOMINIO.test(String(d.email || ''))) {
      return ContentService.createTextOutput('e-mail fora do dominio institucional');
    }

    var aba = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    if (aba.getLastRow() === 0) {
      aba.appendRow(COLUNAS);
      aba.getRange(1, 1, 1, COLUNAS.length).setFontWeight('bold');
      aba.setFrozenRows(1);
    }

    var total = Number(d.totalObjetivas) || 0;
    var acertos = Number(d.acertos) || 0;

    aba.appendRow([
      new Date(),
      d.dataISO ? new Date(d.dataISO) : '',
      String(d.email).toLowerCase(),
      d.nome || '',
      acertos,
      total,
      Number(d.percentual) || 0,
      total ? Math.round(acertos / total * 100) / 10 : '',
      Number(d.discursivasRespondidas) || 0,
      Number(d.totalDiscursivas) || 0,
      Number(d.minutos) || 0,
      JSON.stringify(d.porArea || {}),
      (d.ids || []).join(' ')
    ]);

    return ContentService.createTextOutput('ok');
  } catch (err) {
    return ContentService.createTextOutput('erro: ' + err);
  } finally {
    trava.releaseLock();
  }
}
