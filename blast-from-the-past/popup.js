// Popup script

document.getElementById('openGmail').addEventListener('click', () => {
  chrome.tabs.create({ url: 'https://mail.google.com' });
});

document.getElementById('openSettings').addEventListener('click', () => {
  chrome.runtime.openOptionsPage();
});
