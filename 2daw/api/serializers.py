from rest_framework import serializers
from .models import ProductoTercero

class MedicamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoTercero
        fields = '__all__'