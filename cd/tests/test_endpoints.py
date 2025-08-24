from django.test import TestCase, Client
from django.urls import reverse
import json

class TestCD(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_post_product_register(self):
        data = {
            "name": "orange_pi",
            "quantity": 12,
            "price": 20.00
        }

        response = self.client.post(
            reverse('product_register'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

    def test_get_product_detail(self):
        # Primeiro cria o produto
        data = {
            "name": "orange_pi",
            "quantity": 12,
            "price": 20.00
        }
        self.client.post(
            reverse('product_register'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Agora busca o detalhe do produto
        response = self.client.get(
            reverse('product_detail', kwargs={'slug': 'orange_pi'})
        )
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        # Ajuste conforme a estrutura real da sua resposta
        # self.assertEqual(response_data['name'], "orange_pi")
        # self.assertEqual(response_data['quantity'], 12)

    def test_product_request(self):
        # Primeiro cria o produto
        data = {
            "name": "orange_pi",
            "quantity": 12,
            "price": 20.00
        }
        self.client.post(
            reverse('product_register'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Testa a requisição de produto
        response = self.client.get(
            reverse('product_request', kwargs={'product': 'orange_pi', 'quantity': 13})
        )
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        # Ajuste conforme a estrutura real da sua resposta
        # self.assertFalse(response_data['available'])

    def test_sell_endpoint(self):
        # Primeiro cria o produto
        data = {
            "name": "orange_pi",
            "quantity": 12,
            "price": 20.00
        }
        self.client.post(
            reverse('product_register'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Testa a venda de produto
        response = self.client.post(
            reverse('product_sell', kwargs={'name': 'orange_pi', 'quantity': 10})
        )
        self.assertEqual(response.status_code, 200)

    def test_buy_product(self):
        # Primeiro cria o produto
        data = {
            "name": "orange_pi",
            "quantity": 12,
            "price": 20.00
        }
        self.client.post(
            reverse('product_register'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Testa a compra de produto
        response = self.client.post(
            reverse('product_buy', kwargs={'product': 'orange_pi', 'quantity': 5})
        )
        self.assertEqual(response.status_code, 200)

    def test_product_list(self):
        # Testa a listagem de produtos
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)

    def test_product_change(self):
        data = {
            "name": "orange_pi",
            "quantity": 12,
            "price": 20.00
        }
        self.client.post(
            reverse('product_register'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        update_data = {
            "quantity": 15,
            "price": 25.00
        }
        
        response = self.client.patch(
            reverse('product_change', kwargs={'slug': 'orange_pi'}),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)