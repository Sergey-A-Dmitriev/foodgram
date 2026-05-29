from django.urls import include, path
from rest_framework.routers import DefaultRouter, Route

from api.views.recipes import IngredientViewSet, RecipeViewSet, TagViewSet
from api.views.users import UserViewSet


class UsersRouter(DefaultRouter):

    def get_routes(self, viewset):
        routes = super().get_routes(viewset)
        filtered = []
        for route in routes:
            if (
                route.detail
                and route.url == r'^{prefix}/{lookup}{trailing_slash}$'
            ):
                mapping = {
                    key: value
                    for key, value in route.mapping.items()
                    if key not in ('put', 'patch', 'delete')}
                route = Route(
                    url=route.url,
                    mapping=mapping,
                    name=route.name,
                    detail=route.detail,
                    initkwargs=route.initkwargs,)
            filtered.append(route)
        return filtered


users_router = UsersRouter()
users_router.register('users', UserViewSet, basename='users')

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


def filter_djoser_urls(url_patterns, unwanted_urls):
    return [
        p for p in url_patterns
        if not any(unwanted in str(p.pattern) for unwanted in unwanted_urls)]


unwanted_routes = [
    "set_email/",
    "reset_email_confirm/",
    "activation/",
    "reset_password/",
    "reset_password_confirm/"]

filtered_user_urls = filter_djoser_urls(
    users_router.urls,
    unwanted_routes)

urlpatterns = [
    path('', include(filtered_user_urls)),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))]
