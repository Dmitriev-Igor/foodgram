from django.test import TestCase

class RecipeAPITestCase(APITestCase):
    def test_create_recipe_unauthorized(self):
        response = self.client.post('/api/recipes/', data={...})
        self.assertEqual(response.status_code, 401)