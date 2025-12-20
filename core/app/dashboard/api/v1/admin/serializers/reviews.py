from rest_framework import serializers
from app.review.models import ReviewModel

class ReviewSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()
    class Meta:
        model = ReviewModel
        fields = [
            "user",
            "product",
            "description",
            "rate",
            "status",
            "created_date",
            "updated_date",
            "absolute_url"
        ]
    read_only_fields = ["user", "product", "rate","description"]

    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("absolute_url", None)
        else:
            rep.pop("description", None)
            

        return rep

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return f"{request.build_absolute_uri(obj.pk)}/"