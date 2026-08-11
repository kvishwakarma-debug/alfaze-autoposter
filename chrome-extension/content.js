// Safe Message Passing Helper (No Direct Storage Read)
function getApiKey() {
    return new Promise((resolve) => {
        try {
            if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.sendMessage) {
                chrome.runtime.sendMessage({ action: "GET_GEMINI_KEY" }, (response) => {
                    if (chrome.runtime.lastError) {
                        console.warn("Runtime message error:", chrome.runtime.lastError.message);
                        resolve(null);
                    } else {
                        resolve(response ? response.apiKey : null);
                    }
                });
            } else {
                resolve(null);
            }
        } catch (e) {
            console.error("Message Error:", e);
            resolve(null);
        }
    });
}

// Status Indicator Banner
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
    }, 3000);
}

// Robust Text Injection Function
function injectTextIntoElement(target, text) {
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

// Gemini API Request
async function generateComment(captionText, apiKey) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
    const prompt = `Aap ek Instagram engagement expert hain. Niche di gayi reel caption ko padhein aur ek bahut hi pyara, positive, short aur aesthetic Hinglish comment likhein (1-2 lines with relevant emojis). No quotation marks.\nCaption: ${captionText || "General creative post"}`;

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }

    const data = await response.json();
    return data.candidates[0].content.parts[0].text.trim();
}

// Shortcut Keyboard Listener
window.addEventListener('keydown', async (e) => {
    if (e.altKey && (e.key === 'c' || e.key === 'C')) {
        e.preventDefault();
        e.stopPropagation();

        const activeEl = document.activeElement;
        
        if (!activeEl || activeEl === document.body) {
            showStatusBadge("⚠️ Pehle Comment box par click karein!", true);
            return;
        }

        showStatusBadge("⚡ Generating AI Comment...");

        const apiKey = await getApiKey();
        if (!apiKey) {
            showStatusBadge("⚠️ Key nahi mili! Popup khol kar Save Key button press karein.", true);
            return;
        }

        // Caption fetch
        let caption = "";
        const spanElements = document.querySelectorAll('h1, span, p');
        for (let el of spanElements) {
            if (el.innerText && el.innerText.length > 20) {
                caption = el.innerText;
                break;
            }
        }

        try {
            const commentText = await generateComment(caption, apiKey);
            injectTextIntoElement(activeEl, commentText);
            showStatusBadge("✅ Comment Inserted!");
        } catch (err) {
            console.error(err);
            showStatusBadge("❌ API Error! Check Gemini Key.", true);
        }
    }
}, true);
