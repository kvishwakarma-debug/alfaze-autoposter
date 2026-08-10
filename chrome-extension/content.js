// Storage se API Key fetch karne ka helper
function getApiKey() {
    return new Promise((resolve) => {
        chrome.storage.local.get(['gemini_key'], (result) => {
            resolve(result.gemini_key || null);
        });
    });
}

// Visual Indicator Banner
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

    // Standard input/textarea
    if (target.tagName === 'TEXTAREA' || target.tagName === 'INPUT') {
        const start = target.selectionStart || 0;
        const end = target.selectionEnd || 0;
        target.value = target.value.substring(0, start) + text + target.value.substring(end);
        target.dispatchEvent(new Event('input', { bubbles: true }));
        target.dispatchEvent(new Event('change', { bubbles: true }));
        return;
    }

    // React/Contenteditable div/paragraph inputs
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

// Capture Keyboard Shortcut Event Early
window.addEventListener('keydown', async (e) => {
    if (e.altKey && (e.key === 'c' || e.key === 'C')) {
        e.preventDefault();
        e.stopPropagation();

        const apiKey = await getApiKey();
        if (!apiKey) {
            showStatusBadge("⚠️ Pehle Extension Popup mein Gemini Key Save karein!", true);
            return;
        }

        const activeEl = document.activeElement;
        
        // Ensure user is focused on a valid typing input
        if (!activeEl || activeEl === document.body) {
            showStatusBadge("⚠️ Pehle Comment box par click karein!", true);
            return;
        }

        showStatusBadge("⚡ Generating AI Comment...");

        // Extract Caption
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
            showStatusBadge("❌ Error generating comment. Key check karein!", true);
        }
    }
}, true); // Event Capture mode enabled
