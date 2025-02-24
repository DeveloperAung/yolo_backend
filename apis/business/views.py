from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Business, Carousel, BankInfo, PaymentBankInfo
from .serializers import BusinessSerializer, CarouselSerializer, BankInfoSerializer, PaymentBankInfoSerializer


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.filter(is_active=True)
    serializer_class = BusinessSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Business.objects.filter(is_active=True)

    def get_object(self):
        business = Business.objects.filter(is_active=True).first()
        if not business:
            raise NotFound({"status": "error", "message": "No active business found"})
        return business

    def retrieve(self, request, *args, **kwargs):
        try:
            business = self.get_object()
            serializer = self.get_serializer(business)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print('error', e)
            return Response({"status": "fail", "data": e})

    def partial_update(self, request, *args, **kwargs):
        business = Business.objects.filter(is_active=True).first()
        if not business:
            return Response({"status": "error", "message": "No active business found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(business, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Business info updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "message": "Failed to update business info",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CarouselViewSet(viewsets.ModelViewSet):
    queryset = Carousel.objects.filter(is_active=True)
    serializer_class = CarouselSerializer
    parser_classes = [MultiPartParser, FormParser]  # Allow handling file uploads

    def get_permissions(self):
        """
        Set permissions dynamically:
        - Allow anyone to view the carousel list (GET request).
        - Require authentication for create, update, and delete actions.
        """
        if self.action == 'list':  # Allow unrestricted access to listing
            return [AllowAny()]
        return [IsAuthenticatedOrReadOnly()]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        print('create')
        # Check if an image file is provided
        image = request.FILES.get('image')
        if image:
            data['image'] = image  # Assign file to model field

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save(is_active=True)
            print('successful', status.HTTP_201_CREATED)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print('un successful', status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def deactivate(self, request, pk=None):
        """PATCH request to update only is_active to False"""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({'message': 'Carousel deactivated successfully'}, status=status.HTTP_200_OK)
    # def partial_update(self, request, *args, **kwargs):
    #     print('partial update 1')
    #     instance = self.get_object()
    #     data = {'is_active': False}  # Only update is_active to False
    #     serializer = self.get_serializer(instance, data=data, partial=True)
    #
    #     print('partial update')
    #     if serializer.is_valid():
    #         serializer.save()
    #         print('partial update re', serializer.data)
    #         return Response(serializer.data)
    #     print('errr', serializer.errors)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BankInfoViewSet(viewsets.ModelViewSet):
    queryset = BankInfo.objects.all()
    serializer_class = BankInfoSerializer
    permission_classes = [IsAuthenticated]


class PaymentBankInfoViewSet(ModelViewSet):
    queryset = PaymentBankInfo.objects.filter(is_active=True)
    serializer_class = PaymentBankInfoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Payment bank info created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Payment bank info updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"message": "Payment bank info deactivated successfully"}, status=status.HTTP_200_OK)
