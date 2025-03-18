function saveToDb(button) {
    const card = button.closest('.resource-card');
    
    // Basic required data
    const resourceData = {
        url: card.dataset.url,
        title: card.dataset.title,
        description: card.dataset.description,
        source: card.dataset.source || 'GITHUB'
    };

    console.log("Sending data:", resourceData);  // Debug log

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/api/resources/save/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(resourceData),
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response:", data);  // Debug log
        if (data.status === 'success') {
            showAlert('success', 'Resource saved successfully!');
            button.classList.toggle('btn-success');
            button.classList.toggle('btn-danger');
            button.innerHTML = button.classList.contains('btn-success') ? 'Save to DB' : 'Remove from DB';
        } else {
            throw new Error(data.message || 'Failed to save resource');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'Failed to save resource: ' + error.message);
    });
} 