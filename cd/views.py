from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from .serializers import ProductSerializer, ProductRequestSerializer
from .models import Product
import requests


class ProductsRegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save()
            return Response({
                "status": "success",
                "message": f"Added {product.quantity} unities of {product.name}'s to the CD."
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": "error",
                "message": f"Something went wrong: {serializer.errors}"
            }, status=status.HTTP_400_BAD_REQUEST)


class ProductChangeAPIView(APIView):
    def patch(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        product = get_object_or_404(Product, slug=slug)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": f"{product.name} has been updated, check on the link: {product.get_absolute_url()}"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": f"Something went wrong: {serializer.errors}"
            }, status=status.HTTP_400_BAD_REQUEST)


class ProductsListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        if slug:
            products = Product.objects.filter(slug=slug)
        else:
            products = Product.objects.all()

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class SellProductAPIView(APIView):
    """
    API view to handle selling products from the inventory.
    Expects 'name' (product slug) and 'quantity' as parameters in the URL or request.
    If stock is insufficient, attempts to restock from the HUB before completing the sale.
    """
    def post(self, request, *args, **kwargs):
        name = kwargs.get('name')
        quantity = int(kwargs.get('quantity'))

        if not name or quantity is None:
            return Response({
                "status": "error",
                "message": "This operation requires: product name, product quantity"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Product, slug=name)

        if product.quantity < quantity:
            hub_endpoint = settings.HUB_IP
            quantity_required = quantity - product.quantity
            
            try:
                data = {
                    "product": product,
                    "quantity": quantity_required
                }

                response = requests.post(url=f"{hub_endpoint}cd/request/", data=data, timeout=5)
                response.raise_for_status()
                try:
                    hub_data = response.json()
                except ValueError:
                    hub_data = None
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": "Could not establish connection with the HUB.",
                    "error_msg": str(e)
                }, status=status.HTTP_424_FAILED_DEPENDENCY)

            if response.status_code != 200 or hub_data is None:
                return Response({
                    "status": "error",
                    "message": "Something went wrong! HUB returned an unexpected response."
                }, status=status.HTTP_424_FAILED_DEPENDENCY)

            # Refresh product from DB to check if it has been restocked
            product.refresh_from_db()
            if product.quantity < quantity:
                return Response({
                    "status": "error",
                    "message": f"Not enough {product.name} in stock after restock attempt."
                }, status=status.HTTP_409_CONFLICT)

        try:
            with transaction.atomic():
                product.quantity -= quantity
                product.save()
                return Response({
                    "status": "success",
                    "message": f"Sold {quantity} units of {product.name}"
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"{str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BuyProductAPIView(APIView):
    def post(self, request, *args, **kwargs):
        product = kwargs.get('product')
        quantity = int(kwargs.get('quantity'))

        if not product or quantity is None:
            return Response({
                "status": "error",
                "message": "Missing information: product name or quantity"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product, created = Product.objects.get_or_create(slug=product)

        if created:
            newprod = Product.objects.create(
                name=product,
                price=0,
                quantity=quantity
            )
            newprod.save()

            return Response({
                "status": "success",
                "message": f"New product added to database: {newprod.name}",
                "action": "created"
            }, status=status.HTTP_201_CREATED)
        else:
            try:
                with transaction.atomic():
                    product.quantity += quantity
                    product.save()
                    return Response({
                        "status": "success",
                        "message": f"bought {quantity} of {product.slug}",
                        "action": "restock"
                    }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": f"Something went wrong! {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
            return Response({
                "status": "success",
                "message": f"Bought {quantity} of {product.name}'s",
                "action": "restocked"
            }, status=status.HTTP_200_OK)


class ProductRequestAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ProductRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        product = get_object_or_404(Product, slug=data['product'])

        if product.quantity < data['quantity']:
            enought_products = False
        else:
            enought_products = True
        
        return Response({
            "status": "success",
            "product": product.name,
            "quantity": product.quantity,
            "price": product.price,
            "available": enought_products
        }, status=status.HTTP_200_OK)