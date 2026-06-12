from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Отключает проверку CSRF для API запросов (для тестирования через Insomnia)"""
    
    def enforce_csrf(self, request):
        return  # Пустой метод — проверка CSRF не выполняется