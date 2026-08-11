// Background Worker: Messages listen karega
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "GENERATE_COMMENT") {
        chrome.storage.local.get(['gemini_key'], async (result) => {
            const apiKey = result.gemini_key ? result.gemini_key.trim() : null;
            
            if (!apiKey) {
                sendResponse({ success: false, error: "NO_KEY" });
                return;
            }

            try {
                const comment = await callGeminiAPI(request.caption, apiKey);
                sendResponse({ success: true, comment: comment });
            } catch (err) {
                console.error("Gemini Fetch Error Details:", err);
                sendResponse({ success: false, error: err.message || "API_FAILED" });
            }
        });
        return true;
    }
});

async function callGeminiAPI(captionText, apiKey) {
    // Model updated to gemini-2.5-flash
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;
    
    const prompt = `Aap ek Instagram engagement expert hain. Niche di gayi reel caption ko padhein aur ek bahut hi pyara, positive, short aur aesthetic Hinglish comment likhein (1-2 lines with relevant emojis). Direct comment response dein without quotation marks.\nCaption: ${captionText || "General creative post"}`;

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            contents: [{
                parts: [{ text: prompt }]
            }]
        })
    });

    if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        const message = errJson.error?.message || `HTTP ${response.status}`;
        throw new Error(message);
    }

    const data = await response.json();
    return data.candidates[0].content.parts[0].text.trim();
}
