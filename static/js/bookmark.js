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