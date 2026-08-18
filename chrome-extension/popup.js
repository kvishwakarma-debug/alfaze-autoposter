document.addEventListener('DOMContentLoaded', () => {
  const apiKeyInput = document.getElementById('apiKey');
  const saveBtn = document.getElementById('saveKey');
  const statusDiv = document.getElementById('status');

  // Load existing key matching background.js storage key name 'gemini_key'
  chrome.storage.local.get(['gemini_key'], (result) => {
    if (result.gemini_key) {
      apiKeyInput.value = result.gemini_key;
    }
  });

  // Save key click action
  saveBtn.addEventListener('click', () => {
    const key = apiKeyInput.value.trim();
    if (key) {
      chrome.storage.local.set({ gemini_key: key }, () => {
        statusDiv.style.color = '#059669';
        statusDiv.innerText = '✅ API Key Saved!';
        setTimeout(() => { statusDiv.innerText = ''; }, 3000);
      });
    } else {
      statusDiv.style.color = '#DC2626';
      statusDiv.innerText = '⚠️ Please enter a key!';
    }
  });
});
