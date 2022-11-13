from django.urls import path
from api_server import views

urlpatterns = [
    path('', views.check, name='check'),
    path('equation_solve', views.equation_solve, name='equation_solve'),
    path('equation_solve/', views.equation_solve, name='equation_solve'),
]
