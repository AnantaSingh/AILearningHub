function bookmarkResource(resourceData) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/bookmarks/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: new URLSearchParams(resourceData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'created') {
            alert('Resource bookmarked successfully!');
        } else {
            alert('Resource already bookmarked!');
        }
    })
    .catch(error => console.error('Error:', error));
}

function toggleBookmark(btn) {
    const isBookmarked = btn.classList.contains('btn-primary');
    const data = {
        url: btn.dataset.url,
        title: btn.dataset.title,
        description: btn.dataset.description,
        resource_type: btn.dataset.type,
        source: btn.dataset.source
    };

    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    fetch('/bookmarks/toggle/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        // Toggle button state
        if (!isBookmarked) {
            btn.classList.remove('btn-outline-primary');
            btn.classList.add('btn-primary');
            btn.innerHTML = '🔖 Bookmarked';
        } else {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline-primary');
            btn.innerHTML = '🔖 Bookmark';
        }
        console.log('Bookmark status:', result.status);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error saving bookmark');
    });
} 