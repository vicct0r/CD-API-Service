from django.test import TestCase
import requests

class TestCD(TestCase):
    url_base_cd = "http://192.168.1.83:8000/cd/v1/"

    def test_post_product(self):
        data = {
            "name": "orange_pi",
            "quantity": 12,
            "price": 20.00
        }

        response = requests.post(url=f"{self.url_base_cd}product/register/", data=data, timeout=5)
        assert response.status_code == 201

    def test_get_product_detail(self):
        response = requests.get(url=f"{self.url_base_cd}info/raspberry/")
        assert response.json()['name'] == "orange_pi" and requests.json()['quantity'] == 12

    def test_request_cd(self):
        response = requests.get(url=f"{self.url_base_cd}product/request/orange_pi/13/")
        assert response.json()['available'] == False and response.status_code == 200

    def test_sell_endpoint(self):
        response = requests.post(url=f"{self.url_base_cd}product/sell/orange_pi/10/", timeout=5)
        assert response.status_code == 200