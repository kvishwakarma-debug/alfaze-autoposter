document.addEventListener('DOMContentLoaded', () => {
    // Save hui key load karein
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
