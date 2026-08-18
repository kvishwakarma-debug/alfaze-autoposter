console.log("Insta AI Script Injected & Ready");

function showStatus(text, isError = false) {
    let badge = document.getElementById('insta-ai-badge');
    if (!badge) {
        badge = document.createElement('div');
        badge.id = 'insta-ai-badge';
        badge.style.cssText = 'position:fixed; bottom:20px; right:20px; padding:12px 18px; border-radius:8px; z-index:99999999; font-family:sans-serif; font-size:13px; font-weight:bold; box-shadow:0 4px 12px rgba(0,0,0,0.3); transition:all 0.3s;';
        document.body.appendChild(badge);
    }
    badge.style.backgroundColor = isError ? '#DC2626' : '#059669';
    badge.style.color = '#FFFFFF';
    badge.innerText = text;
    badge.style.display = 'block';

    setTimeout(() => { if (badge) badge.style.display = 'none'; }, 4000);
}

function findTargetInput() {
    const active = document.activeElement;
    if (active && (active.tagName === 'TEXTAREA' || active.tagName === 'INPUT' || active.isContentEditable || active.getAttribute('role') === 'textbox')) {
        return active;
    }
    return document.querySelector('textarea') || 
           document.querySelector('div[contenteditable="true"]') || 
           document.querySelector('div[role="textbox"]');
}

function writeText(target, text) {
    target.focus();
    if (target.tagName === 'TEXTAREA' || target.tagName === 'INPUT') {
        const start = target.selectionStart || 0;
        const end = target.selectionEnd || 0;
        target.value = target.value.substring(0, start) + text + target.value.substring(end);
        target.dispatchEvent(new Event('input', { bubbles: true }));
        target.dispatchEvent(new Event('change', { bubbles: true }));
        return;
    }
    try {
        document.execCommand('insertText', false, text);
    } catch (e) {
        target.innerText = text;
    }
    target.dispatchEvent(new Event('input', { bubbles: true }));
}

function generateCommentAction() {
    const input = findTargetInput();
    if (!input) {
        showStatus("⚠️ Pehle kisi comment box par click karein!", true);
        return;
    }

    showStatus("⚡ AI Comment Generate ho raha hai...");

    let caption = "";
    const elements = document.querySelectorAll('h1, span, p');
    for (let el of elements) {
        if (el.innerText && el.innerText.length > 20) {
            caption = el.innerText;
            break;
        }
    }

    chrome.runtime.sendMessage(
        { action: "GENERATE_COMMENT", caption: caption },
        (response) => {
            if (chrome.runtime.lastError) {
                showStatus("❌ Extension reload hua. Tab Refresh karein!", true);
                return;
            }
            if (response && response.success) {
                writeText(input, response.comment);
                showStatus("✅ AI Comment Inserted!");
            } else if (response && response.error === "NO_KEY") {
                showStatus("⚠️ Extension Icon par click karke Key Save karein!", true);
            } else {
                showStatus(`❌ Error: ${response?.error || "Failed"}`, true);
            }
        }
    );
}

function ensureButtonExists() {
    if (document.getElementById('insta-ai-btn')) return;

    const btn = document.createElement('button');
    btn.id = 'insta-ai-btn';
    btn.innerHTML = '✨ AI Comment';
    btn.style.cssText = `
        position: fixed !important;
        bottom: 80px !important;
        right: 25px !important;
        z-index: 2147483647 !important;
        padding: 12px 20px !important;
        background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 25px !important;
        font-family: sans-serif !important;
        font-weight: bold !important;
        font-size: 14px !important;
        cursor: pointer !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
        display: block !important;
    `;

    btn.onclick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        generateCommentAction();
    };

    (document.body || document.documentElement).appendChild(btn);
}

setInterval(ensureButtonExists, 1000);
