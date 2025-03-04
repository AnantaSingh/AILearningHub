# Add 'accounts' to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'accounts',
]

# Authentication settings
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'home' 