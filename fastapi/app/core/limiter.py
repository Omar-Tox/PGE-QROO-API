from slowapi import Limiter
from slowapi.util import get_remote_address

# Instancia global del limitador
limiter = Limiter(key_func=get_remote_address)