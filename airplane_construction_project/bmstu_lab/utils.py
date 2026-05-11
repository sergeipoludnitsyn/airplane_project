from django.contrib.auth.models import User

class SingletonUser:
    """Синглтон для получения фиксированного пользователя-создателя"""
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._init_user()
        return cls._instance
    
    def _init_user(self):
        self.user, _ = User.objects.get_or_create(
            username='api_creator',
            defaults={
                'email': 'creator@example.com',
                'is_active': True
            }
        )
        if _:
            self.user.set_password('creator123')
            self.user.save()
    
    def get_user(self):
        return self.user

def get_current_creator():
    """Функция для получения текущего создателя (константа)"""
    return SingletonUser().get_user()