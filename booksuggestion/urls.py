from django.urls import path
from .views import BookListView, BookDetailView, BookGenreView, BookReviewDelete, BookReviewUpdate, BookSuggestionView

urlpatterns = [
    path('books/list/', BookListView.as_view(), name='book-list'),
    path('books/', BookGenreView.as_view(), name='book-genre'),
    path('book/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/update/<int:pk>/', BookReviewUpdate.as_view(), name='book-review-update'),
    path('books/delete/<int:pk>/', BookReviewDelete.as_view(), name='book-review-delete'),
    path('books/suggestion/', BookSuggestionView.as_view(), name='book-suggestion-genre'),
]
