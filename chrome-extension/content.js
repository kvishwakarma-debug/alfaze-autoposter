// Storage se API Key fetch karne ka helper
function getApiKey() {
    return new Promise((resolve) => {
        chrome.storage.local.get(['gemini_key'], (result) => {
            resolve(result.gemini_key || null);
        });
    });
}

// Text insertion for Instagram Inputs
async function insertCommentText(element, text) {
    element.focus();

    if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
        element.value = text;
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        return;
    }

    // Instagram contenteditable elements (div/span/p)
    try {
        element.focus();
        document.execCommand('selectAll', false, null);
        document.execCommand('insertText', false, text);
        element.dispatchEvent(new Event('input', { bubbles: true }));
    } catch (e) {
        element.innerText = text;
        element.dispatchEvent(new Event('input', { bubbles: true }));
    }
}

// Gemini API Call
async function generateComment(captionText, apiKey) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
    const prompt = `Aap ek Instagram engagement expert hain. Niche di gayi reel caption ko padhein aur ek bahut hi pyara, positive, short aur aesthetic Hinglish comment likhein (1-2 lines with relevant emojis). No quotation marks.
    Caption: ${captionText || "General creative post"}`;

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
        });
        const data = await response.json();
        return data.candidates[0].content.parts[0].text.trim();
    } catch (e) {
        console.error("AI Error:", e);
        return "Loved this vibe! ✨🔥";
    }
}

// Multi-selector Instagram Input Finder
function findInstagramCommentInput() {
    // Priority 1: Currently focused element
    const active = document.activeElement;
    if (active && active !== document.body && (
        active.tagName === 'TEXTAREA' || 
        active.getAttribute('contenteditable') === 'true' ||
        active.getAttribute('role') === 'textbox'
    )) {
        return active;
    }

    // Priority 2: Instagram web elements
    const selectors = [
        'textarea',
        'div[contenteditable="true"]',
        'p[contenteditable="true"]',
        '[aria-label*="comment" i]',
        '[aria-label*="Comment" i]',
        '[placeholder*="comment" i]',
        '[role="textbox"]'
    ];

    for (let s of selectors) {
        const elements = document.querySelectorAll(s);
        for (let el of elements) {
            // Check if element is visible on screen
            if (el.offsetWidth > 0 || el.offsetHeight > 0 || el.getClientRects().length > 0) {
                return el;
            }
        }
    }
    return null;
}

// Shortcut Handler
document.addEventListener('keydown', async (e) => {
    if (e.altKey && (e.key === 'c' || e.key === 'C')) {
        e.preventDefault();

        const apiKey = await getApiKey();
        if (!apiKey) {
            console.warn("⚠️ Gemini API Key missing in Extension popup!");
            return;
        }

        const commentBox = findInstagramCommentInput();
        if (!commentBox) {
            console.warn("⚠️ Comment box not found on page yet.");
            return;
        }

        // Caption fetch
        let caption = "";
        const spanElements = document.querySelectorAll('h1, span, p');
        for (let el of spanElements) {
            if (el.innerText && el.innerText.length > 25) {
                caption = el.innerText;
                break;
            }
        }

        console.log("🚀 Generating comment...");
        const commentText = await generateComment(caption, apiKey);
        
        await insertCommentText(commentBox, commentText);
        console.log("✅ Comment inserted:", commentText);
    }
});
