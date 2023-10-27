import uuid

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Service, Visitor


def index(request):
    return render(
        request,
        "communication/index.html",
        {"is_authenticated": request.user.is_authenticated},
    )


# @api_view(["GET"])
# def get_example(request):
#     return Response(
#         {
#             "message": "Hello world!",
#         }
#     )


# @api_view(["POST"])
# def post_example(request):
#     return Response(
#         {
#             "message": "I got your data",
#             "data": request.data,
#         }
#     )
