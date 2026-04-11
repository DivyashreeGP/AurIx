import * as vscode from 'vscode';
import axios from 'axios';

let diagCollection: vscode.DiagnosticCollection | undefined;
let analysisTimeout: NodeJS.Timeout | undefined;
let analysisPanel: vscode.WebviewPanel | undefined;
let currentAnalysisData: any = null;

const analyzeCode = async (doc: vscode.TextDocument, triggerAI: boolean = false) => {
  try {
    const codeToSend = doc.getText();
    if (!codeToSend || codeToSend.trim().length === 0) {
      if (diagCollection) diagCollection.set(doc.uri, []);
      console.log('AurIx: empty document, cleared diagnostics.');
      return;
    }

    console.log(`AurIx: analyzing ${doc.uri.fsPath} (len=${codeToSend.length})`);

    const endpoints = ['http://localhost:8000/analyze', 'http://127.0.0.1:8000/analyze'];
    let resp: any = null;
    let lastErr: any = null;
    for (let i = 0; i < endpoints.length; i++) {
      const url = endpoints[i];
      try {
        resp = await axios.post(url, { code: codeToSend }, { timeout: 8000 });
        console.log(`AurIx: backend responded from ${url}`);
        lastErr = null;
        break;
      } catch (err: any) {
        lastErr = err;
        const emsg = (err && (err.message || err.toString())) ? (err.message || err.toString()) : JSON.stringify(err);
        console.warn(`AurIx: request to ${url} failed:`, emsg);
      }
    }

    if (!resp) {
      console.error('AurIx: all backend requests failed.', lastErr);
      if (diagCollection) diagCollection.set(doc.uri, []);
      return;
    }

    const result = (resp && resp.data) ? resp.data : null;
    const diagnostics: vscode.Diagnostic[] = [];

    if (result && Array.isArray(result.issues) && result.issues.length > 0) {
      console.log(`AurIx: Found ${result.issues.length} vulnerabilities`);
      
      for (let i = 0; i < result.issues.length; i++) {
        const issue: any = result.issues[i];
        let rawLine = (issue && issue.line) ? Number(issue.line) : 1;
        let rawCol = (issue && issue.column) ? Number(issue.column) : 1;
        if (isNaN(rawLine)) rawLine = 1;
        if (isNaN(rawCol)) rawCol = 1;

        let line = Math.max(0, rawLine - 1);
        if (line >= doc.lineCount) line = Math.max(0, doc.lineCount - 1);

        let col = Math.max(0, rawCol - 1);
        const lineText = doc.lineAt(line).text;
        if (col > lineText.length) col = Math.max(0, lineText.length - 1);

        const pos = new vscode.Position(line, col);
        const wordRange = doc.getWordRangeAtPosition(pos);
        const range = wordRange ?? new vscode.Range(pos, new vscode.Position(line, Math.min(col + 1, lineText.length)));

        const typeText = (issue && issue.type) ? String(issue.type) : (issue && issue.description) ? String(issue.description) : 'VULNERABILITY';
        const descText = (issue && issue.description) ? String(issue.description) : 'Security vulnerability detected';
        const message = `${typeText}: ${descText}`;

        const sevText = (issue && issue.severity) ? String(issue.severity).toLowerCase() : 'warning';
        const severity = sevText === 'high' || sevText === 'critical' ? vscode.DiagnosticSeverity.Error : vscode.DiagnosticSeverity.Warning;

        const diagnostic = new vscode.Diagnostic(range, message, severity);
        diagnostics.push(diagnostic);
        console.log(`  [Line ${rawLine}] ${typeText}: ${descText}`);
      }
    } else {
      if (diagCollection) diagCollection.set(doc.uri, []);
      console.log('AurIx: no vulnerabilities detected for', doc.uri.fsPath);
      if (triggerAI) {
        showSecureMessage();
      }
      return;
    }

    if (diagCollection) diagCollection.set(doc.uri, diagnostics);
    console.log(`AurIx: set ${diagnostics.length} diagnostic(s) for ${doc.uri.fsPath}`);

    if (triggerAI && result.issues && result.issues.length > 0) {
      await analyzeWithAI(codeToSend, result.issues);
    }
  } catch (err: any) {
    console.error('AurIx: unexpected error while analyzing:', err && (err.message ?? err.toString()) ? (err.message ?? err.toString()) : err);
  }
};

const analyzeWithAI = async (code: string, issues: any[]) => {
  try {
    console.log('AurIx: Sending to AI analysis engine...');
    
    // If no issues, show secure message immediately
    if (!issues || issues.length === 0) {
      showSecureMessage();
      return;
    }
    
    const endpoints = ['http://localhost:8000/analyze-with-ai', 'http://127.0.0.1:8000/analyze-with-ai'];
    let resp: any = null;
    
    for (let i = 0; i < endpoints.length; i++) {
      try {
        resp = await axios.post(endpoints[i], { code, issues }, { timeout: 30000 });
        console.log(`AurIx AI: response from ${endpoints[i]}`);
        break;
      } catch (err: any) {
        console.warn(`AurIx AI: request to ${endpoints[i]} failed`, err.message);
      }
    }
    
    if (!resp) {
      vscode.window.showErrorMessage('Failed to connect to AI analysis engine');
      return;
    }
    
    const analysisResult = resp.data;
    
    // Check if analysis indicates secure code
    if (analysisResult.analysis && analysisResult.analysis.toLowerCase().includes('no vulnerabilities')) {
      showSecureMessage();
      return;
    }
    
    showAnalysisPanel('Vulnerability Analysis', analysisResult, code);
  } catch (err: any) {
    console.error('AurIx AI: error', err);
    vscode.window.showErrorMessage('AI analysis failed: ' + (err.message || 'Unknown error'));
  }
};

const showSecureMessage = () => {
  if (analysisPanel) {
    analysisPanel.dispose();
    analysisPanel = undefined;
  }
  
  analysisPanel = vscode.window.createWebviewPanel('aurix-analysis', 'AurIx Analysis', vscode.ViewColumn.Beside, { enableScripts: true });
  analysisPanel.webview.html = getSecureMessageContent();
};

const showAnalysisPanel = (title: string, analysis: any, code: string) => {
  if (analysisPanel) {
    analysisPanel.dispose();
    analysisPanel = undefined;
  }
  
  analysisPanel = vscode.window.createWebviewPanel('aurix-analysis', 'AurIx Analysis', vscode.ViewColumn.Beside, { enableScripts: true });
  const html = getWebviewContent(analysis, code);
  analysisPanel.webview.html = html;
  currentAnalysisData = { analysis, code };
};

const parseMarkdownToHtml = (text: string): string => {
  const escapeHtmlStr = (txt: string) => {
    const map: {[key: string]: string} = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'};
    return txt.replace(/[&<>"']/g, m => map[m]);
  };

  let html = escapeHtmlStr(text);
  
  // Headers: ### text → <h3>text</h3>
  html = html.replace(/^### (.*?)$/gm, '<h4 style="margin-top: 12px; margin-bottom: 6px; font-weight: 600; font-size: 13px;">$1</h4>');
  html = html.replace(/^## (.*?)$/gm, '<h3 style="margin-top: 12px; margin-bottom: 6px; font-weight: 600; font-size: 14px;">$1</h3>');
  
  // Bold: **text** → <strong>text</strong>
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Italic: *text* → <em>text</em>
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  // Code: `text` → <code>text</code>
  html = html.replace(/`(.*?)`/g, '<code style="background: rgba(0,0,0,0.2); padding: 2px 6px; border-radius: 3px; font-size: 11px;">$1</code>');
  
  // Collapse multiple newlines into single line break
  html = html.replace(/(\n\s*)+/g, '<br/>');
  
  return html;
};

const getWebviewContent = (analysis: any, originalCode: string = ''): string => {
  const analysisText = analysis.analysis || '';
  const secureCode = analysis.secure_code || '';
  const explanation = analysis.explanation || '';
  const error = analysis.error || '';
  const code = originalCode;

  const escapeHtmlStr = (txt: string) => {
    const map: {[key: string]: string} = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'};
    return txt.replace(/[&<>"']/g, m => map[m]);
  };

  const cssStyles = `
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
      background: var(--vscode-editor-background);
      color: var(--vscode-editor-foreground);
      line-height: 1.6;
    }
    .container { max-width: 900px; margin: 0 auto; }
    .header {
      background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(76, 175, 80, 0.1) 100%);
      border-bottom: 1px solid var(--vscode-panel-border);
      padding: 24px 20px;
    }
    .header-content { display: flex; align-items: center; gap: 12px; }
    .header-icon { font-size: 28px; }
    .header h1 { font-size: 20px; font-weight: 600; color: var(--vscode-editor-foreground); }
    .header p { font-size: 12px; color: var(--vscode-descriptionForeground); margin-top: 4px; }
    .section { padding: 24px 20px; border-bottom: 1px solid var(--vscode-panel-border); }
    .section:last-child { border-bottom: none; }
    .section-header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
    .section-title { font-size: 14px; font-weight: 600; color: var(--vscode-editor-foreground); text-transform: uppercase; letter-spacing: 0.5px; }
    .section-icon { font-size: 18px; }
    .code-block { background: var(--vscode-editor-background); border: 1px solid var(--vscode-panel-border); border-radius: 6px; padding: 12px; font-family: 'Monaco', 'Menlo', monospace; font-size: 12px; line-height: 1.5; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; }
    .code-original { background: rgba(255, 107, 107, 0.05); border-left: 3px solid #FF6B6B; }
    .code-secure { background: rgba(76, 175, 80, 0.05); border-left: 3px solid #4CAF50; }
    .copy-btn { background: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: 500; margin-top: 12px; transition: all 0.2s; }
    .copy-btn:hover { background: #45a049; transform: translateY(-1px); }
    .explanation-box { background: linear-gradient(135deg, rgba(76, 175, 80, 0.05) 0%, rgba(76, 175, 80, 0.02) 100%); border-left: 3px solid #4CAF50; padding: 16px; border-radius: 4px; font-size: 12px; line-height: 1.8; word-wrap: break-word; }
    .explanation-box code { background: rgba(0,0,0,0.1); padding: 2px 6px; border-radius: 3px; font-family: 'Monaco', 'Menlo', monospace; font-size: 11px; }
    .explanation-box strong { color: #4CAF50; font-weight: 600; }
    .explanation-box em { color: var(--vscode-editor-foreground); font-style: italic; }
    .vuln-text { font-size: 12px; line-height: 1.6; color: var(--vscode-editor-foreground); }
  `;

  const vulnerabilitiesHtml = escapeHtmlStr(analysisText)
    .replace(/\*\*Line/g, '<strong>Line')
    .replace(/\*\*/g, '</strong>')
    .replace(/\n/g, '<br/>');

  const explanationHtml = explanation ? '<div class="section"><div class="section-header"><span class="section-icon">📚</span><span class="section-title">How to Fix</span></div><div class="explanation-box">' + parseMarkdownToHtml(explanation) + '</div></div>' : '';
  const errorHtml = error ? '<div class="section"><div style="background: rgba(255,107,107,0.1); border: 1px solid #FF6B6B; color: #FF6B6B; padding: 12px; border-radius: 6px; font-size: 12px;">Error: ' + escapeHtmlStr(error) + '</div></div>' : '';

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AurIx Analysis</title>
  <style>${cssStyles}</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="header-content">
        <div class="header-icon">🔒</div>
        <div>
          <h1>Security Analysis</h1>
          <p>Powered by AurIx Vulnerability Detection</p>
        </div>
      </div>
    </div>
    
    ${errorHtml}
    
    <div class="section">
      <div class="section-header">
        <span class="section-icon">📝</span>
        <span class="section-title">Original Code</span>
      </div>
      <div class="code-block code-original">${escapeHtmlStr(code)}</div>
    </div>
    
    <div class="section">
      <div class="section-header">
        <span class="section-icon">⚠️</span>
        <span class="section-title">Vulnerabilities Detected</span>
      </div>
      <div class="vuln-text">${vulnerabilitiesHtml}</div>
    </div>
    
    <div class="section">
      <div class="section-header">
        <span class="section-icon">✅</span>
        <span class="section-title">Secure Code</span>
      </div>
      <div class="code-block code-secure" id="secureCodeBlock">${escapeHtmlStr(secureCode || code)}</div>
      ${secureCode && secureCode !== code ? '<button class="copy-btn" onclick="copySecureCode()">📋 Copy Secure Code</button>' : ''}
    </div>
    
    ${explanationHtml}
  </div>

  <script>
    function copySecureCode() {
      const block = document.getElementById('secureCodeBlock');
      const text = block.innerText;
      navigator.clipboard.writeText(text).then(() => {
        alert('✓ Secure code copied!');
      }).catch(err => {
        alert('Failed to copy');
      });
    }
  </script>
</body>
</html>`;
};

const getSecureMessageContent = (): string => {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Code is Secure</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
      background: var(--vscode-editor-background);
      color: var(--vscode-editor-foreground);
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 20px;
    }
    .container {
      text-align: center;
      background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
      border: 2px solid #4CAF50;
      border-radius: 12px;
      padding: 60px 40px;
      max-width: 500px;
      box-shadow: 0 8px 32px rgba(76, 175, 80, 0.1);
    }
    .checkmark {
      font-size: 80px;
      margin-bottom: 20px;
      animation: scaleIn 0.6s ease-out;
    }
    h1 {
      font-size: 32px;
      color: #4CAF50;
      margin-bottom: 12px;
      font-weight: 700;
    }
    p {
      font-size: 16px;
      color: var(--vscode-editor-foreground);
      opacity: 0.9;
      line-height: 1.6;
      margin-bottom: 20px;
    }
    .details {
      font-size: 13px;
      color: var(--vscode-descriptionForeground);
      padding-top: 20px;
      border-top: 1px solid rgba(76, 175, 80, 0.2);
      margin-top: 20px;
    }
    @keyframes scaleIn {
      from {
        transform: scale(0);
        opacity: 0;
      }
      to {
        transform: scale(1);
        opacity: 1;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="checkmark">✅</div>
    <h1>Code is Secure</h1>
    <p>No vulnerabilities detected in your code. Your implementation follows security best practices.</p>
    <div class="details">
      <strong>Keep it up!</strong> Continue following secure coding practices.
    </div>
  </div>
</body>
</html>`;
};

function escapeHtml(text: string): string {
  const map: {[key: string]: string} = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'};
  return text.replace(/[&<>"']/g, m => map[m]);
}

export function activate(context: vscode.ExtensionContext) {
  console.log('AurIx extension activating');

  if (!diagCollection) {
    diagCollection = vscode.languages.createDiagnosticCollection('aurix');
  }

  const changeDisposable = vscode.workspace.onDidChangeTextDocument(async (event) => {
    if (analysisTimeout) clearTimeout(analysisTimeout);
    analysisTimeout = setTimeout(() => {
      analyzeCode(event.document, false);
    }, 500);
  });

  const saveDisposable = vscode.workspace.onDidSaveTextDocument((doc) => {
    analyzeCode(doc, true);
  });

  const closeDisposable = vscode.workspace.onDidCloseTextDocument(() => {
    if (analysisPanel) {
      analysisPanel.dispose();
      analysisPanel = undefined;
    }
  });

  context.subscriptions.push(changeDisposable, saveDisposable, closeDisposable);
  if (diagCollection) context.subscriptions.push(diagCollection);

  console.log('AurIx activated');
}

export function deactivate() {
  if (diagCollection) {
    diagCollection.dispose();
    diagCollection = undefined;
  }
}
