from matrix.amazon import alert
from matrix.models import User 
user = User.objects.first()
alert.render(user)