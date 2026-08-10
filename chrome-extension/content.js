// Storage se API Key fetch karne ka helper
function getApiKey() {
    return new Promise((resolve) => {
        chrome.storage.local.get(['gemini_key'], (result) => {
            resolve(result.gemini_key || null);
        });
    });
}

// Human-like Typing Simulator
const getRandomDelay = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

async function typeHumanLike(element, text) {
    element.focus();
    
    // Non-textarea elements (div / p / span editable content)
    if (element.tagName.toLowerCase() !== 'textarea') {
        element.focus();
        document.execCommand('selectAll', false, null);
        document.execCommand('insertText', false, text);
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        return;
    }

    // Standard Textarea elements
    element.value = '';
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        element.dispatchEvent(new KeyboardEvent('keydown', { key: char, bubbles: true }));
        document.execCommand('insertText', false, char);
        element.dispatchEvent(new KeyboardEvent('keyup', { key: char, bubbles: true }));
        await new Promise(r => setTimeout(r, getRandomDelay(20, 60)));
    }
    element.dispatchEvent(new Event('input', { bubbles: true }));
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
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }]
            })
        });
        const data = await response.json();
        return data.candidates[0].content.parts[0].text.trim();
    } catch (e) {
        console.error("AI Error:", e);
        return "Loved this vibe! ✨🔥";
    }
}

// Smart Comment Box Finder Strategy
function findCommentBox() {
    const activeEl = document.activeElement;
    
    // Strategy 1: Agar user ne pehle se hi kisi typing area par click kar rakha hai
    if (activeEl && (
        activeEl.tagName === 'TEXTAREA' || 
        activeEl.getAttribute('contenteditable') === 'true' ||
        activeEl.tagName === 'P' || 
        activeEl.getAttribute('role') === 'textbox'
    )) {
        return activeEl;
    }

    // Strategy 2: Instagram Specific Input Selectors
    const selectors = [
        'textarea',
        'div[contenteditable="true"]',
        'p[contenteditable="true"]',
        '[aria-label*="Add a comment"]',
        '[aria-label*="comment"]',
        '[placeholder*="Add a comment"]',
        '[role="textbox"]'
    ];

    for (let selector of selectors) {
        const elements = document.querySelectorAll(selector);
        for (let el of elements) {
            // Visible aur clickable elements filter out karein
            if (el.offsetWidth > 0 && el.offsetHeight > 0) {
                return el;
            }
        }
    }
    return null;
}

// Key Shortcut Listener: Press Alt + C
document.addEventListener('keydown', async (e) => {
    if (e.altKey && (e.key === 'c' || e.key === 'C')) {
        e.preventDefault();
        
        const apiKey = await getApiKey();
        if (!apiKey) {
            alert("Pehle Extension Icon par click karke apni Gemini API Key Save karein!");
            return;
        }

        console.log("⚡ Auto-Comment Triggered...");

        const commentBox = findCommentBox();
        if (!commentBox) {
            alert("Comment box detect nahi hua. Kripya pehle comment input area par click karke typing cursor activate karein!");
            return;
        }

        // Caption extraction
        let caption = "";
        const spanElements = document.querySelectorAll('h1, span, p');
        for (let el of spanElements) {
            if (el.innerText && el.innerText.length > 25) {
                caption = el.innerText;
                break;
            }
        }

        console.log("Caption extracted:", caption);
        
        // Disable temporarily while typing
        const commentText = await generateComment(caption, apiKey);
        console.log("Generated Comment:", commentText);

        await typeHumanLike(commentBox, commentText);
        console.log("✅ Comment Typed Successfully!");
    }
});
