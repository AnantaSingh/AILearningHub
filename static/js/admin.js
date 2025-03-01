function saveToDb(btn) {
    const isAlreadySaved = btn.classList.contains('btn-success');
    const data = {
        url: btn.dataset.url,
        title: btn.dataset.title,
        description: btn.dataset.description,
        source: btn.dataset.source,
        metadata: JSON.parse(btn.dataset.metadata)
    };

    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    fetch('/api/resources/save/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(result => {
        if (result.status === 'success') {
            if (!isAlreadySaved) {
                btn.classList.remove('btn-outline-success');
                btn.classList.add('btn-success');
                btn.innerHTML = '<i class="fas fa-check"></i> Saved to DB';
            } else {
                btn.classList.remove('btn-success');
                btn.classList.add('btn-outline-success');
                btn.innerHTML = '<i class="fas fa-database"></i> Save to DB';
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (error.message.includes('403')) {
            alert('You must be an admin to save to database');
        } else {
            alert('Error saving to database');
        }
    });
} 