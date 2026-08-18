console.log("Insta AI Script Injected & Ready v11.0");

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

    setTimeout(() => { if (badge) badge.style.display = 'none'; }, 3500);
}

// Scrapes currently active Reel / Post caption dynamically
function getActiveReelCaption() {
    // Check open Reel modal or current visible viewport caption
    const activeDialog = document.querySelector('div[role="dialog"]');
    const container = activeDialog || document;

    // Direct Caption H1 / Spans
    const h1 = container.querySelector('h1');
    if (h1 && h1.innerText && h1.innerText.length > 5) {
        return h1.innerText;
    }

    const spans = container.querySelectorAll('span[dir="auto"]');
    for (let span of spans) {
        const txt = span.innerText ? span.innerText.trim() : '';
        const isAudio = txt.includes('Audio') || txt.includes('♫') || txt.includes('Original');
        if (txt.length > 15 && !isAudio) {
            return txt;
        }
    }

    return "Aesthetic reel or post";
}

function generateCommentAction() {
    showStatus("⚡ AI Comment Generating...");

    const caption = getActiveReelCaption();

    chrome.runtime.sendMessage(
        { action: "GENERATE_COMMENT", caption: caption },
        async (response) => {
            if (chrome.runtime.lastError) {
                showStatus("❌ Tab Refresh Karein!", true);
                return;
            }
            if (response && response.success) {
                try {
                    await navigator.clipboard.writeText(response.comment);
                    showStatus(`✅ Copied: "${response.comment}" (Ctrl+V Paste)`);
                } catch (err) {
                    showStatus(`✅ Generated: ${response.comment}`);
                }
            } else if (response && response.error === "NO_KEY") {
                showStatus("⚠️ Extension Icon se Key Save karein!", true);
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

window.addEventListener('keydown', (e) => {
    if (e.altKey && (e.key === 'c' || e.key === 'C')) {
        e.preventDefault();
        generateCommentAction();
    }
}, true);
