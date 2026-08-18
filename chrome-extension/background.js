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
    
    const prompt = `Aap ek Instagram engagement expert hain. Post caption ke aadhar par ek short, aesthetic, friendly Hinglish comment generate karein (1-2 lines with emojis). Rules: Sirf final comment text return karein, koi quote ya extra explanation mat dein.\n\nCaption: ${captionText || "Nice post"}`;

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }]
        })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error?.message || `API Error: ${response.status}`);
    }

    const data = await response.json();

    // Extracting text safely from candidate response
    const candidate = data.candidates?.[0];
    const textPart = candidate?.content?.parts?.find(p => p.text)?.text;

    if (textPart) {
        return textPart.trim();
    }

    throw new Error("Valid text output nahi mila API se.");
}
