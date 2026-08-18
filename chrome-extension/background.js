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
        return true;
    }
});

async function callGeminiAPI(captionText, apiKey) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;
    
    // Random Seed for unique commentary every time
    const randomId = Math.floor(Math.random() * 10000);
    const prompt = `Act as a Gen-Z Instagram user. Write ONE short, aesthetic Hinglish comment (max 8-10 words, 1 emoji) for this caption. Make it unique and different every time [ID:${randomId}]. Do not wrap in quotes.\nCaption: ${captionText || "Cool post"}`;

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: {
                temperature: 0.95, // High creative randomness
                maxOutputTokens: 40 // Super fast execution (Limits generation time to ~2sec)
            }
        })
    });

    if (!response.ok) {
        // Fallback to fast standard endpoint if needed
        const fallbackUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
        const fallbackResponse = await fetch(fallbackUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }],
                generationConfig: { temperature: 0.9, maxOutputTokens: 40 }
            })
        });

        if (!fallbackResponse.ok) {
            throw new Error("API Request Failed");
        }

        const fallbackData = await fallbackResponse.json();
        return fallbackData.candidates[0].content.parts[0].text.trim();
    }

    const data = await response.json();
    return data.candidates[0].content.parts[0].text.trim();
}
