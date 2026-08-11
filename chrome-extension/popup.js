document.addEventListener('DOMContentLoaded', () => {
  const apiKeyInput = document.getElementById('apiKey');
  const saveKeyBtn = document.getElementById('saveKey');
  const generateBtn = document.getElementById('generateBtn');
  const captionInput = document.getElementById('caption');
  const statusDiv = document.getElementById('status');

  // Load saved key
  chrome.storage.local.get(["geminiApiKey"], (res) => {
    if (res.geminiApiKey) {
      apiKeyInput.value = res.geminiApiKey;
      statusDiv.style.color = "green";
      statusDiv.innerText = "Key Loaded! Ready to use.";
    }
  });

  saveKeyBtn.addEventListener('click', () => {
    const key = apiKeyInput.value.trim();
    if (!key) return;
    chrome.storage.local.set({ geminiApiKey: key }, () => {
      statusDiv.style.color = "green";
      statusDiv.innerText = "Key Saved Successfully!";
    });
  });

  generateBtn.addEventListener('click', async () => {
    const key = apiKeyInput.value.trim();
    if (!key) {
      statusDiv.style.color = "red";
      statusDiv.innerText = "Pehle API Key daal kar save karein!";
      return;
    }

    statusDiv.style.color = "blue";
    statusDiv.innerText = "Generating AI comment...";

    const promptText = `Generate a single short, catchy, natural human comment (under 12 words) for an Instagram post with caption: "${captionInput.value || 'Awesome post'}". Use appropriate emojis. Return ONLY the comment text.`;

    try {
      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${key}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ contents: [{ parts: [{ text: promptText }] }] })
        }
      );

      const data = await response.json();
      if (data.candidates && data.candidates[0]?.content?.parts[0]?.text) {
        const comment = data.candidates[0].content.parts[0].text.trim();
        
        // Copy to clipboard
        await navigator.clipboard.writeText(comment);
        
        statusDiv.style.color = "green";
        statusDiv.innerHTML = `✅ Copied to Clipboard!<br><b>"${comment}"</b><br>Ab Instagram comment box me Ctrl+V paste karein!`;
      } else {
        statusDiv.style.color = "red";
        statusDiv.innerText = "Error: " + (data.error?.message || "Invalid Key or API Limit");
      }
    } catch (err) {
      statusDiv.style.color = "red";
      statusDiv.innerText = "Fetch Error: " + err.message;
    }
  });
});
