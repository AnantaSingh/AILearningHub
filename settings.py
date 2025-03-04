INSTALLED_APPS = [
    # ... existing apps ...
    'accounts',
]

# Add these at the end of the file
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login' 