from rest_framework import serializers
from app.shop.models import WishlistProductModel

class WishlistProductModelSerializers(serializers.ModelSerializer):
    
    absolute_url = serializers.SerializerMethodField()
    class Meta:
        model = WishlistProductModel
        fields = '__all__'


    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("absolute_url", None)

        return rep
        
    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return f"{request.build_absolute_uri(obj.pk)}/"