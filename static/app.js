const form = document.querySelector('#url-form');
const input = document.querySelector('#url');
const result = document.querySelector('#result');
const quality = document.querySelector('#quality');
const message = document.querySelector('#message');
const searchButton = document.querySelector('#search-button');
const downloadButton = document.querySelector('#download-button');

function say(text, ok = false) { message.textContent = text; message.className = `message${ok ? ' ok' : ''}`; }
function busy(button, state, text) { button.disabled = state; if (text) button.textContent = text; }

form.addEventListener('submit', async (event) => {
  event.preventDefault(); result.hidden = true; say('');
  busy(searchButton, true, 'Buscando...');
  try {
    const response = await fetch('/api/info', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({url: input.value.trim()}) });
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
  finally { busy(searchButton, false, 'Buscar'); }
});

downloadButton.addEventListener('click', async () => {
  say('Preparando o download. Isso pode levar alguns minutos...', true);
  busy(downloadButton, true, 'Preparando...');
  try {
    const response = await fetch('/api/download', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({url: input.value.trim(), itag: quality.value}) });
    if (!response.ok) { const data = await response.json(); throw new Error(data.error || 'Falha ao baixar.'); }
    const blob = await response.blob();
    const disposition = response.headers.get('content-disposition') || '';
    const name = /filename="?([^";]+)"?/i.exec(disposition)?.[1] || 'video.mp4';
    const link = Object.assign(document.createElement('a'), {href: URL.createObjectURL(blob), download: name});
    link.click(); URL.revokeObjectURL(link.href); say('Download iniciado!', true);
  } catch (error) { say(error.message); }
  finally { busy(downloadButton, false, 'Baixar MP4'); }
});
