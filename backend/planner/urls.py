from django.urls import path
from planner.views import health_check, route_plan


urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("route-plan/", route_plan, name="route-plan"),
]
