// Background Worker: Messages listen karega
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "GENERATE_COMMENT") {
        // Storage se safe Key fetching
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
        return true; // Asynchronous response ke liye mandatory hai
    }
});

// Gemini API Fetch Function
async function callGeminiAPI(captionText, apiKey) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
    const prompt = `Aap ek Instagram engagement expert hain. Niche di gayi reel caption ko padhein aur ek bahut hi pyara, positive, short aur aesthetic Hinglish comment likhein (1-2 lines with relevant emojis). No quotation marks.\nCaption: ${captionText || "General creative post"}`;

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }]
        })
    });

    if (!response.ok) {
        throw new Error("API Request Failed");
    }

    const data = await response.json();
    return data.candidates[0].content.parts[0].text.trim();
}
