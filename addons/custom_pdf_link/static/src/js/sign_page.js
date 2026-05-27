// PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

function renderPDF(url) {
    var container = document.getElementById('pdfContainer');
    container.innerHTML = '<p style="padding:16px;color:#888;">Cargando PDF...</p>';

    pdfjsLib.getDocument(url).promise.then(function(pdf) {
        container.innerHTML = '';
        for (var i = 1; i <= pdf.numPages; i++) {
            (function(pageNum) {
                pdf.getPage(pageNum).then(function(page) {
                    var dpr = window.devicePixelRatio || 1;
                    var scale = (container.offsetWidth / page.getViewport({ scale: 1 }).width) * dpr;
                    var viewport = page.getViewport({ scale: scale });
                    var canvas = document.createElement('canvas');
                    canvas.width = viewport.width;
                    canvas.height = viewport.height;
                    canvas.style.display = 'block';
                    canvas.style.width = '100%';
                    canvas.style.marginBottom = '2px';
                    container.appendChild(canvas);
                    page.render({ canvasContext: canvas.getContext('2d'), viewport: viewport });
                });
            })(i);
        }
    }).catch(function(err) {
        container.innerHTML = '<p style="padding:16px;color:red;">Error al cargar el PDF.</p>';
        console.error(err);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    if (window.PDF_URL) {
        renderPDF(window.location.origin + window.PDF_URL);
    }
});

// --- Canvas / SignaturePad ---

var signaturePad = null;
var aclaracionPad = null;

// Sets canvas internal resolution to match its CSS size × devicePixelRatio,
// fixing coordinate drift on Retina/High-DPI screens and after rotation.
function resizeCanvas(canvas, pad) {
    if (!canvas || canvas.offsetWidth === 0) return;

    var dataURL = (pad && !pad.isEmpty()) ? pad.toDataURL() : null;

    var ratio = window.devicePixelRatio || 1;
    canvas.width  = canvas.offsetWidth  * ratio;
    canvas.height = canvas.offsetHeight * ratio;
    canvas.getContext('2d').scale(ratio, ratio);

    if (pad) {
        pad.clear();
        if (dataURL) {
            pad.fromDataURL(dataURL, { ratio: 1 });
        }
    }
}

function initCanvas(id) {
    var canvas = document.getElementById(id);
    if (!canvas) return null;

    var pad = new SignaturePad(canvas, {
        backgroundColor: 'rgba(0,0,0,0)',
        penColor: 'rgb(0,0,0)',
        minWidth: 1.5,
        maxWidth: 3.5
    });

    resizeCanvas(canvas, pad);
    return pad;
}

function debounce(fn, ms) {
    var timer;
    return function() { clearTimeout(timer); timer = setTimeout(fn, ms); };
}

function handleResize() {
    resizeCanvas(document.getElementById('signCanvas'), signaturePad);
    resizeCanvas(document.getElementById('aclaracionCanvas'), aclaracionPad);
}

window.addEventListener('resize', debounce(handleResize, 150));
// orientationchange fires before the layout reflows; wait for it to settle
window.addEventListener('orientationchange', function() {
    setTimeout(handleResize, 300);
});

signaturePad = initCanvas('signCanvas');

function clearFirma()     { if (signaturePad)  signaturePad.clear(); }
function clearAclaracion() { if (aclaracionPad) aclaracionPad.clear(); }

function submitSignature() {
    if (!signaturePad || signaturePad.isEmpty()) {
        alert('Por favor dibujá tu firma antes de confirmar.');
        return;
    }
    var btn = document.getElementById('btnSubmit');
    btn.disabled = true;
    btn.textContent = 'Enviando...';

    fetch('/sign/document/' + window.SIGN_TOKEN + '/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: { signature: signaturePad.toDataURL('image/png') } })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.result && data.result.next_step === 'aclaracion') {
            document.getElementById('firmaCard').style.display = 'none';
            document.getElementById('aclaracionCard').style.display = 'block';
            // Use rAF so the browser reflows the newly-visible canvas before we read offsetWidth
            requestAnimationFrame(function() {
                aclaracionPad = initCanvas('aclaracionCanvas');
            });
        } else {
            alert('Error: ' + (data.result ? data.result.error : 'Error desconocido'));
            btn.disabled = false;
            btn.textContent = 'Confirmar firma';
        }
    })
    .catch(function() {
        alert('Error de conexión. Intentá nuevamente.');
        btn.disabled = false;
        btn.textContent = 'Confirmar firma';
    });
}

function submitAclaracion() {
    if (!aclaracionPad || aclaracionPad.isEmpty()) {
        alert('Por favor dibujá tu aclaración antes de confirmar.');
        return;
    }
    var btn = document.getElementById('btnAclaracion');
    btn.disabled = true;
    btn.textContent = 'Enviando...';

    fetch('/sign/document/' + window.SIGN_TOKEN + '/aclaracion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: { aclaracion: aclaracionPad.toDataURL('image/png') } })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.result && data.result.success) {
            document.getElementById('aclaracionCard').style.display = 'none';
            document.getElementById('successBox').style.display = 'block';
        } else {
            alert('Error: ' + (data.result ? data.result.error : 'Error desconocido'));
            btn.disabled = false;
            btn.textContent = 'Confirmar aclaración';
        }
    })
    .catch(function() {
        alert('Error de conexión. Intentá nuevamente.');
        btn.disabled = false;
        btn.textContent = 'Confirmar aclaración';
    });
}
