// Universelle Form-Handler Funktion
async function submitDynamicForm(formElement, formType) {
  const formData = new FormData(formElement);
  const data = {};
  
  // FormData zu JSON konvertieren
  for (let [key, value] of formData.entries()) {
      data[key] = value;
  }
  
  const submitBtn = formElement.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;
  
  submitBtn.disabled = true;
  submitBtn.textContent = 'Wird gesendet...';
  
  // Vorherige Nachrichten entfernen
  removeFormMessage(formElement);
  
  try {
      const response = await fetch(`https://api.linus.kuepper.nrw/api/form/${formType}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
      });
      
      const result = await response.json();
      
      if (response.ok) {
          // Erfolgsnachricht anzeigen
          showFormMessage(formElement, 'success', 
              'Die Anmeldung wurde gespeichert und wird bearbeitet. Sollten Sie nach 2 Tagen keine Bestätigung erhalten, wenden Sie sich per E-Mail an uns.');
          formElement.reset();
      } else {
          throw new Error(result.error || 'Unbekannter Fehler');
      }
  } catch (error) {
      showFormMessage(formElement, 'error', `Fehler: ${error.message}`);
  } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
  }
}

// Hilfsfunktion: Nachricht unter dem Submit-Button anzeigen
function showFormMessage(formElement, type, message) {
    // Vorherige Nachricht entfernen
    removeFormMessage(formElement);
    
    // Neue Nachricht erstellen
    const messageDiv = document.createElement('div');
    messageDiv.className = `form-message ${type}`;
    messageDiv.textContent = message;
    messageDiv.id = 'form-message';
    
    // Nach dem Submit-Button einfügen
    const submitBtn = formElement.querySelector('button[type="submit"]');
    submitBtn.parentNode.insertBefore(messageDiv, submitBtn.nextSibling);
    
    // Optional: Nach 10 Sekunden automatisch ausblenden
    setTimeout(() => {
        removeFormMessage(formElement);
    }, 10000);
}

// Hilfsfunktion: Nachricht entfernen
function removeFormMessage(formElement) {
    const existingMessage = formElement.querySelector('#form-message');
    if (existingMessage) {
        existingMessage.remove();
    }
}

function showMessage(type, text) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${type}`;
  messageDiv.textContent = text;
  
  // Message styling per CSS
  document.body.appendChild(messageDiv);
  
  setTimeout(() => {
      messageDiv.remove();
  }, 5000);
}

// Event Listeners für alle Formulare
document.addEventListener('DOMContentLoaded', function() {
  // Anmeldeformular
  const anmeldeForm = document.getElementById('anmelde-form');
  if (anmeldeForm) {
      anmeldeForm.addEventListener('submit', (e) => {
          e.preventDefault();
          submitDynamicForm(anmeldeForm, 'anmeldung');
      });
  }
  
  // Kontaktformular
  const kontaktForm = document.getElementById('kontakt-form');
  if (kontaktForm) {
      kontaktForm.addEventListener('submit', (e) => {
          e.preventDefault();
          submitDynamicForm(kontaktForm, 'kontakt');
      });
  }
  
  // Newsletter-Formular
  const newsletterForm = document.getElementById('newsletter-form');
  if (newsletterForm) {
      newsletterForm.addEventListener('submit', (e) => {
          e.preventDefault();
          submitDynamicForm(newsletterForm, 'newsletter');
      });
  }

  // Newsletter-Formular
  const sommercampForm = document.getElementById('sommercamp-form');
  if (sommercampForm) {
    sommercampForm.addEventListener('submit', (e) => {
          e.preventDefault();
          submitDynamicForm(sommercampForm, 'sommercamp');
      });
  }

    // probetraining
    const probetrainingForm = document.getElementById('probetraining-form');
    if (probetrainingForm) {
      probetrainingForm.addEventListener('submit', (e) => {
            e.preventDefault();
            submitDynamicForm(probetrainingForm, 'probetraining');
        });
    }

    // Probemonat
    const probemonatForm = document.getElementById('probemonat-form');
    if (probemonatForm) {
      probemonatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            submitDynamicForm(probemonatForm, 'probemonat');
        });
    }
});