console.log("Insta AI Script Injected & Ready v8.0");

let lastFocusedInput = null;

// Track active focus or clicks across all elements
document.addEventListener('focusin', (e) => {
    if (isCommentInput(e.target)) lastFocusedInput = e.target;
}, true);

document.addEventListener('click', (e) => {
    if (isCommentInput(e.target)) lastFocusedInput = e.target;
}, true);

function isCommentInput(el) {
    if (!el) return false;
    const tag = el.tagName ? el.tagName.toUpperCase() : '';
    const role = el.getAttribute ? el.getAttribute('role') : '';
    const contentEditable = el.isContentEditable || el.getAttribute('contenteditable') === 'true';
    
    return tag === 'TEXTAREA' || tag === 'INPUT' || contentEditable || role === 'textbox';
}

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
    // 1. Check last focused element
    if (lastFocusedInput && document.body.contains(lastFocusedInput)) {
        return lastFocusedInput;
    }

    // 2. Check current activeElement
    const active = document.activeElement;
    if (isCommentInput(active)) return active;

    // 3. Search for Instagram's modern comment input elements
    const selectors = [
        'form textarea',
        'textarea[aria-label*="comment"]',
        'textarea[aria-label*="Comment"]',
        'textarea[placeholder*="comment"]',
        'textarea[placeholder*="Comment"]',
        'div[role="textbox"]',
        'div[contenteditable="true"]',
        'p[dir="ltr"]',
        'textarea'
    ];

    for (let selector of selectors) {
        const found = document.querySelector(selector);
        if (found) return found;
    }

    return null;
}

function writeText(target, text) {
    target.focus();

    // Standard Inputs / Textareas
    if (target.tagName === 'TEXTAREA' || target.tagName === 'INPUT') {
        const start = target.selectionStart || 0;
        const end = target.selectionEnd || 0;
        target.value = target.value.substring(0, start) + text + target.value.substring(end);
        
        // Dispatch React/DOM events
        target.dispatchEvent(new Event('input', { bubbles: true }));
        target.dispatchEvent(new Event('change', { bubbles: true }));
        return;
    }

    // Div ContentEditable / Paragraphs (New Instagram UI)
    try {
        document.execCommand('insertText', false, text);
    } catch (e) {
        target.innerText = text;
    }
    target.dispatchEvent(new Event('input', { bubbles: true }));
    target.dispatchEvent(new Event('change', { bubbles: true }));
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

    // Prevent button click from taking focus away
    btn.addEventListener('mousedown', (e) => {
        e.preventDefault();
    });

    btn.onclick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        generateCommentAction();
    };

    (document.body || document.documentElement).appendChild(btn);
}

setInterval(ensureButtonExists, 1000);

// Global Shortcut: Alt + C
window.addEventListener('keydown', (e) => {
    if (e.altKey && (e.key === 'c' || e.key === 'C')) {
        e.preventDefault();
        generateCommentAction();
    }
}, true);
