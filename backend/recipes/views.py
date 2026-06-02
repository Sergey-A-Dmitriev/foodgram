from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView

from recipes.models import Recipe
from recipes.utils import decode_id


class ShortLinkRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        recipe_id = decode_id(kwargs['short_code'])

        recipe = get_object_or_404(
            Recipe,
            pk=recipe_id)

        return f'/api/recipes/{recipe.id}/'
