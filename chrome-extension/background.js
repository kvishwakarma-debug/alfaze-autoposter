chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "GENERATE_COMMENT") {
        chrome.storage.local.get(['gemini_key'], async (result) => {
            const apiKey = result.gemini_key;
            if (!apiKey) {
                sendResponse({ success: false, error: "NO_KEY" });
                return;
            }

            try {
                const comment = await callGeminiAPI(request.caption, apiKey);
                sendResponse({ success: true, comment: comment });
            } catch (err) {
                sendResponse({ success: false, error: err.message });
            }
        });
        return true; // Asynchronous channel open rakhne ke liye
    }
});

async function callGeminiAPI(captionText, apiKey) {
    // Gemini 2.5 Flash / 2.0 Flash Endpoint (Updated Version)
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;
    
    const prompt = `Aap ek Instagram engagement expert hain. Niche di gayi caption ko padhein aur ek pyara, short aur aesthetic Hinglish comment likhein (1-2 lines with emojis). Return ONLY the comment text without quotes.\nCaption: ${captionText || "General post"}`;

    let response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }]
        })
    });

    // Fallback model if 2.5-flash endpoint varies
    if (!response.ok) {
        const fallbackUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
        response = await fetch(fallbackUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }]
            })
        });
    }

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error?.message || "API Request Failed");
    }

    const data = await response.json();
    return data.candidates[0].content.parts[0].text.trim();
}
