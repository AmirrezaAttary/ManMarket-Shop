from rest_framework import serializers
from app.order.models import UserAddressModel

class UserAddressModelSerializers(serializers.ModelSerializer):

    absolute_url = serializers.SerializerMethodField()
    class Meta:
        model = UserAddressModel
        fields = '__all__'
        read_only_fields = ["user",]


    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("absolute_url", None)

        return rep
        
    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return f"{request.build_absolute_uri(obj.pk)}/"

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)