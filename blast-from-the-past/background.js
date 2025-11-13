// Background service worker for Gmail API integration

const GMAIL_API_BASE = 'https://www.googleapis.com/gmail/v1/users/me';
const ONE_YEAR_MS = 365 * 24 * 60 * 60 * 1000;

// OAuth token management
let cachedToken = null;

async function getAuthToken() {
  if (cachedToken) {
    return cachedToken;
  }

  return new Promise((resolve, reject) => {
    chrome.identity.getAuthToken({ interactive: true }, (token) => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
      } else {
        cachedToken = token;
        resolve(token);
      }
    });
  });
}

// Fetch emails from more than 1 year ago
async function fetchOldEmails(maxResults = 50) {
  try {
    const token = await getAuthToken();
    const oneYearAgo = new Date(Date.now() - ONE_YEAR_MS);
    const formattedDate = oneYearAgo.toISOString().split('T')[0].replace(/-/g, '/');

    // Query for emails older than 1 year, exclude spam and trash
    const query = `before:${formattedDate} -in:spam -in:trash`;

    const response = await fetch(
      `${GMAIL_API_BASE}/messages?q=${encodeURIComponent(query)}&maxResults=${maxResults}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Gmail API error: ${response.status}`);
    }

    const data = await response.json();
    return data.messages || [];
  } catch (error) {
    console.error('Error fetching old emails:', error);
    throw error;
  }
}

// Fetch full email details
async function getEmailDetails(messageId) {
  try {
    const token = await getAuthToken();

    const response = await fetch(
      `${GMAIL_API_BASE}/messages/${messageId}?format=full`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Gmail API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching email details:', error);
    throw error;
  }
}

// Parse email data
function parseEmail(emailData) {
  const headers = emailData.payload.headers;
  const getHeader = (name) => {
    const header = headers.find(h => h.name.toLowerCase() === name.toLowerCase());
    return header ? header.value : '';
  };

  const subject = getHeader('Subject');
  const from = getHeader('From');
  const to = getHeader('To');
  const date = getHeader('Date');
  const cc = getHeader('Cc');

  // Extract body
  let body = '';
  if (emailData.payload.body.data) {
    body = atob(emailData.payload.body.data.replace(/-/g, '+').replace(/_/g, '/'));
  } else if (emailData.payload.parts) {
    const textPart = emailData.payload.parts.find(part => part.mimeType === 'text/plain');
    if (textPart && textPart.body.data) {
      body = atob(textPart.body.data.replace(/-/g, '+').replace(/_/g, '/'));
    } else {
      const htmlPart = emailData.payload.parts.find(part => part.mimeType === 'text/html');
      if (htmlPart && htmlPart.body.data) {
        const html = atob(htmlPart.body.data.replace(/-/g, '+').replace(/_/g, '/'));
        // Strip HTML tags
        body = html.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ');
      }
    }
  }

  // Extract participant names
  const extractNames = (headerValue) => {
    if (!headerValue) return [];
    const matches = headerValue.match(/(?:"([^"]+)"|([^<\s]+))\s*(?:<([^>]+)>)?/g);
    if (!matches) return [];
    return matches.map(m => {
      const nameMatch = m.match(/"([^"]+)"/);
      if (nameMatch) return nameMatch[1];
      const emailMatch = m.match(/<([^>]+)>/);
      if (emailMatch) {
        const email = emailMatch[1];
        const name = m.replace(/<[^>]+>/, '').trim();
        return name || email.split('@')[0];
      }
      return m.split('@')[0];
    }).filter(Boolean);
  };

  const participants = [
    ...extractNames(from),
    ...extractNames(to),
    ...extractNames(cc)
  ].filter((name, index, self) => self.indexOf(name) === index);

  return {
    id: emailData.id,
    subject,
    from,
    to,
    date,
    body: body.trim(),
    participants,
    threadId: emailData.threadId
  };
}

// Message handler
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getRandomOldEmail') {
    (async () => {
      try {
        // Fetch list of old emails
        const messages = await fetchOldEmails();

        if (messages.length === 0) {
          sendResponse({ error: 'No old emails found' });
          return;
        }

        // Pick a random email
        const randomMessage = messages[Math.floor(Math.random() * messages.length)];

        // Fetch full details
        const emailData = await getEmailDetails(randomMessage.id);
        const parsedEmail = parseEmail(emailData);

        sendResponse({ email: parsedEmail });
      } catch (error) {
        sendResponse({ error: error.message });
      }
    })();
    return true; // Will respond asynchronously
  }

  if (request.action === 'signOut') {
    if (cachedToken) {
      chrome.identity.removeCachedAuthToken({ token: cachedToken }, () => {
        cachedToken = null;
        sendResponse({ success: true });
      });
    } else {
      sendResponse({ success: true });
    }
    return true;
  }
});
