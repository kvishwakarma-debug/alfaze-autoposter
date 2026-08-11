// Safe API Key fetch helper with fallback
function getApiKey() {
    return new Promise((resolve) => {
        try {
            if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
                chrome.storage.local.get(['gemini_key'], (result) => {
                    resolve(result ? result.gemini_key : null);
                });
            } else {
                console.warn("Chrome storage API not ready yet.");
                resolve(null);
            }
        } catch (e) {
            console.error("Storage Access Error:", e);
            resolve(null);
        }
    });
}
