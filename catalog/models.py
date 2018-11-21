from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date

# Create your models here.
class Genre(models.Model):
    """
    Model representing book genre (one book to many genres relationship)
    object records are book / genre pairs
    """

    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science fiction')

    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Model representing book information (i.e. each published book in the library, not each physical book)
    """

    title = models.CharField(max_length=200)

    # ForeignKey(Author) allows each author to have many books, but each book to have only one author
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(max_length=1000, help_text="Enter a brief description")
    isbn = models.CharField(
        'ISBN',
        max_length=13,
        help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>'
    )

    # ManyToMany allows each book to have many associated genres, and each genre to have many associated books
    genre = models.ManyToManyField(
        Genre,
        help_text='Select a genre for this book'
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    # CUSTOM METHODS

    def display_genre(self):
        """
        display genre returns a list of the first 3 genres associated with the book as a single, comma-separated string
        """
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = "Genre"

    def get_available_count(self):
        """
        count available copies of the book
        """
        self.bookinstance_set.filter(status__exact='a').count()


class BookInstance(models.Model):
    """
    Each record in the book instance model represents one physical copy of a given published book
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    language = models.CharField(max_length=200, default='English')
    due_back = models.DateField(null=True, blank=True)

    # Borrower added as foreignkey to user
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # add an is_overdue property definition using the @property decorator
    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    LOAN_STATUS =(
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    STATUS_DICT = {
        'm': 'text-danger',
        'o': 'text-warning',
        'a': 'text-success',
        'r': 'text-warning'
    }

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book availability'
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"), )

    def get_status_text_style(self):
        return self.STATUS_DICT[self.status]

    def __str__(self):
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    """
    Represents each author of a book in the catalog
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        permissions = (("can_crud_authors", "Create, Update, Delete Author records"), )

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'

