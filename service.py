from models.user import User

def get_user(id):
    u = User(id)
    return u.user

def add_user(u):
    return u.add_user()

def update_user(u):
    return u.update_user()

def delete_user(id):
    return User.delete_user(id)

def login_user(email, password):
    return User.login(email, password)

def get_users():
    return User.get_users()

def add_secret(id, secret):
    u = User(id)
    return u.add_secret(secret)
    
def remove_secret(id, secret):
    u = User(id)
    return u.remove_secret(secret)