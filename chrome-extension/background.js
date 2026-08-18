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
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key=${apiKey}`;
    
    const randomId = Math.floor(Math.random() * 10000);
    const prompt = `Act as a Gen-Z Instagram user. Write ONE short, aesthetic Hinglish comment (max 8-10 words, 1 emoji) for this caption. Make it unique [ID:${randomId}]. Return ONLY the comment text without quotes.\nCaption: ${captionText || "Cool post"}`;

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: {
                temperature: 0.95,
                maxOutputTokens: 45 // Super fast response within 1-2 seconds
            }
        })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error?.message || `API Error (${response.status})`);
    }

    const data = await response.json();
    return data.candidates[0].content.parts[0].text.trim();
}
