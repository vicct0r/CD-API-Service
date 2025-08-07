from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ProductSerializer
from .models import Product


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
                "status": "success",
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
    def post(self, request, *args, **kwargs):
        name = kwargs.get('name')
        quantity = kwargs.get('quantity')

        if not name and not quantity:
            return Response({
                "status": "error",
                "message": "This operation requires: product name, product quantity"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Product.objects.select_for_update(), slug=name)

        if product.quantity < quantity:
            return Response({
                "status": "error",
                "message": f"Not enought unities of {product.name} on the Distribution Center."
            }, status=status.HTTP_412_PRECONDITION_FAILED)
        
        try:
            with transaction.atomic():
                product.quantity -= quantity
                product.save()
                return Response({
                    "status": "success",
                    "message": f"Sold: {quantity} {product.name}'s"
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"{str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BuyProductAPIView(APIView):
    def post(self, request, *args, **kwargs):
        product = kwargs.get('product')
        quantity = kwargs.get('quantity')

        if not product and not quantity:
            return Response({
                "status": "error",
                "message": "Missing information: product name or quantity"
            }, status=status.HTTP_424_FAILED_DEPENDENCY)
        
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
    def get(self, request, *args, **kwargs):
        slug = kwargs.get('product')
        quantity = kwargs.get('quantity')

        if not slug and not quantity:
            return Response({
                "status": "error",
                "message": "Provide the product and quantity for the service!"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Product, slug=slug)

        if product.quantity < quantity:
            return Response(status=status.HTTP_409_CONFLICT)
        else:
            return Response({
                "status": "success",
                "available": product.is_active,
                "quantity": product.quantity,
                "price": product.price,
                "requested quantity": quantity,
                "total_price": product.price * quantity
            }, status=status.HTTP_200_OK)
