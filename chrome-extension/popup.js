document.addEventListener('DOMContentLoaded', () => {
    // Saved key load karein
    chrome.storage.local.get(['gemini_key'], (result) => {
        if (result.gemini_key) {
            document.getElementById('apiKey').value = result.gemini_key;
        }
    });

    // Save key button logic
    document.getElementById('saveBtn').addEventListener('click', () => {
        const key = document.getElementById('apiKey').value.trim();
        if (key) {
            chrome.storage.local.set({ gemini_key: key }, () => {
                const status = document.getElementById('status');
                status.innerText = "Key Saved Successfully! ✅";
                setTimeout(() => { status.innerText = ""; }, 2500);
            });
        }
    });
});

// Content Script ke request par Storage se key dena
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "GET_GEMINI_KEY") {
        chrome.storage.local.get(['gemini_key'], (result) => {
            sendResponse({ apiKey: result.gemini_key || null });
        });
        return true; // Async response ke liye
    }
});
