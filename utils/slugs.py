import random
import string
from django.utils.text import slugify

def random_letters(k=5) :
    return  ''.join(random.choices(string.ascii_letters + string.digits,k=k))

def new_slugify(text) :
    return slugify(text) + random_letters(5)
