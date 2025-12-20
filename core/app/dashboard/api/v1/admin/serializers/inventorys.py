from rest_framework import serializers
from app.shop.models import ProductColorInventory, Color

class InventoryColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"

        
class InventorySerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()
    color = InventoryColorSerializer(read_only=True)  # به جای فقط id، کل اطلاعات رنگ رو میاره
    class Meta:
        model = ProductColorInventory
        fields = [
            "id",
            "product",
            "color",
            "stock",
            "price",
            "final_price",
            "discount_percent",
            "updated_date",
            "absolute_url",
            
        ]
        read_only_fields = ("id", "discount_percent")
        
    
    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("absolute_url", None)
        return rep    
    
    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return f"{request.build_absolute_uri(obj.pk)}/"