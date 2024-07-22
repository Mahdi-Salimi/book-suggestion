from rest_framework import serializers

class BookSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    author = serializers.CharField(max_length=255)
    genre = serializers.CharField(max_length=255)
    rating = serializers.FloatField(required=False)
    avg_genre = serializers.FloatField(required=False)
