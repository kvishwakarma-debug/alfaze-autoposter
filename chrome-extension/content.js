// Helper to get API Key from Storage
function getApiKey() {
    return new Promise((resolve) => {
        chrome.storage.local.get(['gemini_key'], (result) => {
            resolve(result.gemini_key || null);
        });
    });
}

// Typing simulator for both Input / Textarea and Custom Divs
async function typeText(element, text) {
    element.focus();

    // Strategy 1: Regular Form Controls (textarea / input)
    if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
        element.value = text;
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        return;
    }

    // Strategy 2: Contenteditable Divs / Custom Editors (Instagram Web Default)
    try {
        // Clear existing text if any
        document.execCommand('selectAll', false, null);
        document.execCommand('delete', false, null);

        // Insert new text
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

// Universal Input Finder
function getTargetElement() {
    // 1. Direct active element check (Jiss jagah cursor blink kar raha hai)
    const active = document.activeElement;
    if (active && active !== document.body && active.tagName !== 'HTML') {
        return active;
    }

    // 2. Query all editable inputs on page
    const selectors = [
        'form textarea',
        'form div[contenteditable="true"]',
        'div[contenteditable="true"]',
        'textarea',
        '[role="textbox"]'
    ];

    for (let s of selectors) {
        const el = document.querySelector(s);
        if (el) return el;
    }

    return null;
}

// Keyboard listener
document.addEventListener('keydown', async (e) => {
    if (e.altKey && (e.key === 'c' || e.key === 'C')) {
        e.preventDefault();

        const apiKey = await getApiKey();
        if (!apiKey) {
            alert("Pehle Extension Icon par click karke Gemini API Key Save karein!");
            return;
        }

        const targetEl = getTargetElement();
        if (!targetEl) {
            alert("Comment box pe pehle ek baar mouse se click kar lein taaki cursor active ho jaye!");
            return;
        }

        // Caption fetch logic
        let caption = "";
        const spanElements = document.querySelectorAll('h1, span, p');
        for (let el of spanElements) {
            if (el.innerText && el.innerText.length > 25) {
                caption = el.innerText;
                break;
            }
        }

        console.log("Generating comment...");
        const commentText = await generateComment(caption, apiKey);
        
        await typeText(targetEl, commentText);
        console.log("✅ Comment inserted successfully!");
    }
});
