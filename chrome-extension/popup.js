document.addEventListener('DOMContentLoaded', () => {
    chrome.storage.local.get(['gemini_key'], (result) => {
        if (result.gemini_key) {
            document.getElementById('apiKey').value = result.gemini_key;
        }
    });

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
