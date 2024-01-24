from datetime import datetime

def get_isotime():
    return datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
