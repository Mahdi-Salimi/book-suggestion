from django.db import connection
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from werkzeug.security import generate_password_hash


from .serializers import BookSerializer
from .validators import validate_rating

def get_user(username):
    with connection.cursor() as cursor:
        cursor.execute("Select id from users where username=%s",[username])
        row = cursor.fetchone()
    return row[0]

class BookListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_id = get_user(request.user.username)
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT books.id, books.title, books.author, books.genre, reviews.rating AS user_rating "
                            "FROM books "
                            "LEFT JOIN reviews ON books.id = reviews.book_id AND reviews.user_id = %s;"
                            ,[user_id])
            rows = cursor.fetchall()
        data = [{'id': row[0], 'title': row[1], 'author': row[2], 'genre': row[3], 'rating': row[4]} for row in rows]
        serializer = BookSerializer(data, many=True)
        return Response(serializer.data)

    
class BookGenreView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = get_user(request.user.username)
        genre = request.GET.get('genre')
        if genre:
            genre = genre.strip()
        print(genre)
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT books.id, books.title, books.author, books.genre, reviews.rating AS user_rating "
                            "FROM books "
                            "LEFT JOIN reviews ON books.id = reviews.book_id AND reviews.user_id = %s "
                            "WHERE books.genre = %s;"
                            ,[user_id, genre])
            rows = cursor.fetchall()
        data = [{'id': row[0], 'title': row[1], 'author': row[2], 'genre': row[3], 'rating': row[4]} for row in rows]
        serializer = BookSerializer(data, many=True)
        return Response(serializer.data)
        

class BookDetailView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, pk):
        user_id = get_user(request.user.username)
        with connection.cursor() as cursor:
            cursor.execute("SELECT books.id, books.title, books.author, books.genre, reviews.rating AS user_rating "
                            "FROM books "
                            "LEFT JOIN reviews ON books.id = reviews.book_id AND reviews.user_id = %s "
                            "WHERE books.id = %s", [user_id, pk])
            row = cursor.fetchone()
        book = {'id': row[0], 'title': row[1], 'author': row[2], 'genre': row[3], 'rating': row[4]}
        if book:
            serializer = BookSerializer(book)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)


 
class BookReviewUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user_id = get_user(request.user.username)
        new_rating = request.data.get('rating')
        
        if new_rating is None:
            return Response({'error': 'Rating is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_rating = int(new_rating)
            validate_rating(new_rating)
        except (ValidationError, ValueError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM reviews WHERE book_id = %s AND user_id = %s", [pk, user_id]
            )
            review = cursor.fetchone()
            
            if review:
                cursor.execute(
                    "UPDATE reviews SET rating = %s WHERE book_id = %s AND user_id = %s",
                    [new_rating, pk, user_id]
                )
            else:
                cursor.execute(
                    "INSERT INTO reviews (book_id, user_id, rating) VALUES (%s, %s, %s)",
                    [pk, user_id, new_rating]
                )
        
        response = BookDetailView.get(self, request, pk)
        return response

class BookReviewDelete(APIView):
    def delete(self, request, pk):
        user_id = get_user(request.user.username)
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM reviews WHERE book_id = %s AND user_id = %s", [pk, user_id]
            )
        
        return Response({'message': 'Rating deleted'}, status=status.HTTP_204_NO_CONTENT)
    
'''
this api will suggest books in genres which user likes the most
calculates average rating of each genre and suggests in order of average ratings which are more than 3
'''

class BookSuggestionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_id = get_user(request.user.username)
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE user_id = %s", [user_id])
            review_count = cursor.fetchone()[0]

            if review_count == 0:
                return Response({"message": "there is not enough data about you"}, status=status.HTTP_200_OK)
            
            query = """
                WITH user_rated_genre_avg AS (
                    SELECT books.genre, AVG(reviews.rating) AS avg_rating
                    FROM reviews
                    INNER JOIN books ON reviews.book_id = books.id
                    WHERE reviews.user_id = %s
                    GROUP BY books.genre
                    HAVING AVG(reviews.rating) > 3
                )
                SELECT books.id, books.title, books.author, books.genre, user_rated_genre_avg.avg_rating
                FROM books
                INNER JOIN user_rated_genre_avg ON books.genre = user_rated_genre_avg.genre
                LEFT JOIN reviews ON books.id = reviews.book_id AND reviews.user_id = %s
                WHERE reviews.rating IS NULL
                Order BY user_rated_genre_avg.avg_rating Desc, books.genre DESC;
            """
            cursor.execute(query, [user_id, user_id])
            rows = cursor.fetchall()

        data = [{'id': row[0], 'title': row[1], 'author': row[2], 'genre': row[3], 'avg_genre': row[4]} for row in rows]
        serializer = BookSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        


