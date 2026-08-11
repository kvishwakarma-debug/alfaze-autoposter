console.log("Insta AI Assistant Loaded Successfully v2.0");

// Status Badge Notification
function showStatus(text, isError = false) {
    let badge = document.getElementById('insta-ai-badge');
    if (!badge) {
        badge = document.createElement('div');
        badge.id = 'insta-ai-badge';
        badge.style.cssText = 'position:fixed; bottom:20px; right:20px; padding:12px 18px; border-radius:8px; z-index:999999; font-family:sans-serif; font-size:14px; font-weight:bold; box-shadow:0 4px 12px rgba(0,0,0,0.2); transition:all 0.3s;';
        document.body.appendChild(badge);
    }
    badge.style.backgroundColor = isError ? '#DC2626' : '#059669';
    badge.style.color = '#FFFFFF';
    badge.innerText = text;
    badge.style.display = 'block';

    setTimeout(() => {
        if (badge) badge.style.display = 'none';
    }, 3500);
}

// Active Target Detector
function findTargetInput() {
    const el = document.activeElement;
    if (el && (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT' || el.isContentEditable || el.getAttribute('role') === 'textbox')) {
        return el;
    }
    return document.querySelector('textarea') || document.querySelector('div[contenteditable="true"]') || document.querySelector('div[role="textbox"]');
}

// Universal Text Injector
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

// Alt + C Listener
window.addEventListener('keydown', (e) => {
    if (e.altKey && (e.key === 'c' || e.key === 'C')) {
        e.preventDefault();
        e.stopPropagation();

        const input = findTargetInput();
        if (!input) {
            showStatus("⚠️ Pehle comment box me click karein!", true);
            return;
        }

        showStatus("⚡ Generating AI Comment...");

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
                    showStatus("❌ Refresh Instagram Tab (Context Reset)", true);
                    return;
                }
                if (response && response.success) {
                    writeText(input, response.comment);
                    showStatus("✅ Comment Generated!");
                } else if (response && response.error === "NO_KEY") {
                    showStatus("⚠️ Extension icon par click karke Key Save karein!", true);
                } else {
                    showStatus("❌ API Error! Gemini Key verify karein.", true);
                }
            }
        );
    }
}, true);
