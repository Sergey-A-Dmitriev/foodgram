from api.filters import IngredientSearchFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers.recipes import (IngredientSerializer,
                                     RecipeReadSerializer,
                                     RecipeWriteSerializer, TagSerializer)
from api.serializers.users import ShortRecipeSerializer
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet


class TagViewSet(ReadOnlyModelViewSet):
    """ViewSet для чтения тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """ViewSet для чтения ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name', 'name')


class RecipeViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin,
                    UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """ViewSet для рецептов."""

    queryset = Recipe.objects.all().distinct()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadOnly]

    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от метода."""
        if self.action in ('list', 'retrive'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def add_recipe(self, model, request, pk):
        """Для исключения повторного добавления в избранное и покупки."""
        recipe = self.get_object()
        if model.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            return Response(
                {'errors': 'Уже добавлено'},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(
            user=request.user,
            recipe=recipe)

        serializer = ShortRecipeSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def remove_recipe(self, model, request, pk):
        """Для удаления рецепта из избранного и покупок."""
        recipe = self.get_object()
        obj = model.objects.filter(
            user=request.user,
            recipe=recipe)
        if not obj.exists():
            return Response(
                {'errors': 'Рецепт не найден'},
                status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Для добавления и удаления рецепта в/из избранное."""
        if request.method == 'POST':
            return self.add_recipe(Favorite, request, pk)
        return self.remove_recipe(Favorite, request, pk)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Для добавления и удаления рецепта в/из покупки."""
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, pk)
        return self.remove_recipe(ShoppingCart, request, pk)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Для получения списка покупок."""
        recipes = Recipe.objects.filter(
            shopping_carts__user=request.user)
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount'))
        lines = []
        lines.append('Список покупок\nРецепты:\n')
        for recipe in recipes:
            lines.append(f'- {recipe.name}')
        lines.append('\nИнгредиенты:\n')
        for ingredient in ingredients:
            lines.append(
                f"{ingredient['ingredient__name']} - "
                f"{ingredient['total_amount']} "
                f"({ingredient['ingredient__measurement_unit']})")
        content = '\n'.join(lines)
        response = HttpResponse(
            content,
            content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_cart.txt"'
        return response

    @action(
        detail=True,
        methods=['get'])
    def get_link(self, request, pk=None):
        """Для получения ссылки на рецепт."""
        recipe = self.get_object()
        short_link = (f'/recipes/{recipe.id}/')
        return Response({
            'short-link': short_link})
