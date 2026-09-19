const form = document.querySelector('#url-form');
const input = document.querySelector('#url');
const result = document.querySelector('#result');
const quality = document.querySelector('#quality');
const message = document.querySelector('#message');
const searchButton = document.querySelector('#search-button');
const downloadButton = document.querySelector('#download-button');

function say(text, ok = false) { message.textContent = text; message.className = `message${ok ? ' ok' : ''}`; }
function busy(button, state, text) { button.disabled = state; if (text) button.textContent = text; }

async function downloadUrl(url, itag = 'best') {
  const response = await fetch('/api/download', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({url: url, itag: itag}) });
  const data = await response.json();
  if (!response.ok) { throw new Error(data.error || 'Falha ao baixar.'); }
  console.log('Salvo em:', data.path);
  return data;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault(); result.hidden = true; say('');
  
  const urls = input.value.split('\n').map(u => u.trim()).filter(u => u);
  if (urls.length === 0) return;

  if (urls.length > 1) {
    // Lote Automático
    busy(searchButton, true, 'Baixando lote...');
    say('Baixando lote, isso pode levar um tempo...', true);
    let successCount = 0;
    let errors = [];
    for (const url of urls) {
      try {
        await downloadUrl(url, 'best');
        successCount++;
      } catch (err) {
        errors.push(err.message);
      }
    }
    busy(searchButton, false, 'Processar / Baixar Lote');
    if (errors.length > 0) {
      say(`Lote concluído com erros. Sucesso: ${successCount}. Erros: ${errors.join(' | ')}`);
    } else {
      say(`Lote concluído com sucesso! ${successCount} vídeo(s) baixado(s).`, true);
    }
  } else {
    // URL Única
    busy(searchButton, true, 'Buscando...');
    try {
      const response = await fetch('/api/info', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({url: urls[0]}) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Não foi possível consultar o vídeo.');
      document.querySelector('#thumbnail').src = data.thumbnail;
      document.querySelector('#title').textContent = data.title;
      document.querySelector('#author').textContent = data.author || '';
      quality.replaceChildren(...data.streams.map(s => {
        const option = document.createElement('option'); option.value = s.itag; option.textContent = `${s.label}${s.fps ? ` · ${s.fps} fps` : ''}`; return option;
      }));
      result.hidden = false;
    } catch (error) { say(error.message); }
    finally { busy(searchButton, false, 'Processar / Baixar Lote'); }
  }
});

downloadButton.addEventListener('click', async () => {
  const urls = input.value.split('\n').map(u => u.trim()).filter(u => u);
  const url = urls[0];
  if (!url) return;
  say('Preparando o download. Isso pode levar alguns minutos...', true);
  busy(downloadButton, true, 'Preparando...');
  try {
    await downloadUrl(url, quality.value);
    say('Download iniciado!', true);
  } catch (error) { say(error.message); }
  finally { busy(downloadButton, false, 'Baixar MP4'); }
});
