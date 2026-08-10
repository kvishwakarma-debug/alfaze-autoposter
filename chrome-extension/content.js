// Storage se API Key lene ke liye helper function
function getApiKey() {
    return new Promise((resolve) => {
        chrome.storage.local.get(['gemini_key'], (result) => {
            resolve(result.gemini_key || null);
        });
    });
}

// Human Typing Simulator
const getRandomDelay = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

async function typeHumanLike(element, text) {
    element.focus();
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        element.dispatchEvent(new KeyboardEvent('keydown', { key: char, bubbles: true }));
        document.execCommand('insertText', false, char);
        element.dispatchEvent(new KeyboardEvent('keyup', { key: char, bubbles: true }));
        await new Promise(r => setTimeout(r, getRandomDelay(40, 120)));
    }
}

// Gemini API Call (Using 1.5 Flash Model)
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

// Key Shortcut Listener: Press Alt + C
document.addEventListener('keydown', async (e) => {
    if (e.altKey && (e.key === 'c' || e.key === 'C')) {
        const apiKey = await getApiKey();
        
        if (!apiKey) {
            alert("Pehle Extension Icon par click karke apni Gemini API Key Save karein!");
            return;
        }

        console.log("⚡ Auto-Comment Triggered...");

        // Caption read karein
        let caption = "";
        const spanElements = document.querySelectorAll('h1, span');
        for (let el of spanElements) {
            if (el.innerText && el.innerText.length > 20) {
                caption = el.innerText;
                break;
            }
        }

        // Comment box dhoondein
        const commentBox = document.querySelector('textarea');
        if (!commentBox) {
            alert("Comment box nahi mila! Pehle comment icon par click karein.");
            return;
        }

        const commentText = await generateComment(caption, apiKey);
        await typeHumanLike(commentBox, commentText);
        console.log("✅ Comment Drafted:", commentText);
    }
});
