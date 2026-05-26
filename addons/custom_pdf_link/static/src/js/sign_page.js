function initCanvas(id) {
    var c = document.getElementById(id);
    if (!c) return null;
    var ratio = Math.max(window.devicePixelRatio || 1, 1);
    c.width = c.offsetWidth * ratio;
    c.height = 200 * ratio;
    c.getContext('2d').scale(ratio, ratio);
    return new SignaturePad(c);
}

var signaturePad = initCanvas('signCanvas');
var aclaracionPad = null;

function clearFirma() { if (signaturePad) signaturePad.clear(); }
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
            aclaracionPad = initCanvas('aclaracionCanvas');
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
