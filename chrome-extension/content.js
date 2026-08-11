// Floating Notification Badge
function showStatusBadge(message, isError = false) {
    let badge = document.getElementById('insta-ai-status-badge');
    if (!badge) {
        badge = document.createElement('div');
        badge.id = 'insta-ai-status-badge';
        badge.style.position = 'fixed';
        badge.style.bottom = '20px';
        badge.style.right = '20px';
        badge.style.padding = '10px 16px';
        badge.style.borderRadius = '8px';
        badge.style.zIndex = '999999';
        badge.style.fontFamily = 'sans-serif';
        badge.style.fontSize = '13px';
        badge.style.fontWeight = 'bold';
        badge.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        document.body.appendChild(badge);
    }
    badge.style.backgroundColor = isError ? '#EF4444' : '#10B981';
    badge.style.color = '#FFFFFF';
    badge.innerText = message;
    badge.style.display = 'block';

    setTimeout(() => {
        if (badge) badge.style.display = 'none';
    }, 3500);
}

// Text Injection in active element
function injectComment(target, text) {
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

// Keydown Listener (Alt + C)
window.addEventListener('keydown', (e) => {
    if (e.altKey && (e.key === 'c' || e.key === 'C')) {
        e.preventDefault();

        const activeEl = document.activeElement;
        
        if (!activeEl || activeEl === document.body || activeEl.tagName === 'HTML') {
            showStatusBadge("⚠️ Pehle Comment box par click karein!", true);
            return;
        }

        showStatusBadge("⚡ Generating AI Comment...");

        // Caption extract karein
        let caption = "";
        const spanElements = document.querySelectorAll('h1, span, p');
        for (let el of spanElements) {
            if (el.innerText && el.innerText.length > 20) {
                caption = el.innerText;
                break;
            }
        }

        // Background script se communication
        chrome.runtime.sendMessage(
            { action: "GENERATE_COMMENT", caption: caption },
            (response) => {
                if (chrome.runtime.lastError) {
                    showStatusBadge("❌ Extension Context Error! Tab refresh karein.", true);
                    return;
                }

                if (response && response.success) {
                    injectComment(activeEl, response.comment);
                    showStatusBadge("✅ Comment Typed Successfully!");
                } else if (response && response.error === "NO_KEY") {
                    showStatusBadge("⚠️ Extension Icon par click karke Key save karein!", true);
                } else {
                    showStatusBadge("❌ API Error! Gemini Key check karein.", true);
                }
            }
        );
    }
}, true);
