import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views import generic
from catalog.models import Book, Author, BookInstance, Genre
from catalog.forms import RenewBookModelForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.urls import reverse, reverse_lazy



# Create your views here.
def index(request):
    """
    View function for the index of the catalog .../catalog
    """

    # Counts of main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books
    num_instances_availble = BookInstance.objects.filter(status__exact='a').count()

    # when using the count() method, all() is implied
    num_authors = Author.objects.count()

    # Challenge!!
    num_books_dead_in_name = Book.objects.filter(title__icontains='dead').count()
    num_books_dead_author  = Book.objects.filter(author__date_of_death__isnull=False).count()

    # Session!!
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_availble,
        'num_authors': num_authors,
        'num_books_dead_in_name': num_books_dead_in_name,
        'num_books_dead_author': num_books_dead_author,
        'num_visits': request.session['num_visits'],
    }

    # render the html template with data from the context variable
    return render(request, 'catalog/index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 1


class BookDetailView(generic.DetailView):
    model = Book


class AuthorDetailView(generic.DetailView):
    model = Author


class AuthorListView(generic.ListView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based list-view listing books on loan to (or participants employed by)
    current user
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance\
            .objects\
            .filter(borrower=self.request.user)\
            .filter(status__exact='o')\
            .order_by('due_back')


class LoanedBooksLibrarianListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_librarian_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.all().order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If it's a POST method, then process the form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Process the cleaned data and write it to the model
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # Redirect to the all-books view
            return HttpResponseRedirect(reverse('all-borrowed'))

    # if it's not a POST method, it must be a GET, which means something different
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


# Define generic CRUD views for Author model
class AuthorCreate(PermissionRequiredMixin, generic.edit.CreateView):
    permission_required = 'catalog.can_crud_authors'
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '2018-05-01'}


class AuthorUpdate(PermissionRequiredMixin, generic.edit.UpdateView):
    permission_required = 'catalog.can_crud_authors'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(PermissionRequiredMixin, generic.edit.DeleteView):
    permission_required = 'catalog.can_crud_authors'
    model = Author
    success_url = reverse_lazy('authors')


# Define the same generic CRUD views for books
class BookCreate(PermissionRequiredMixin, generic.edit.CreateView):
    permission_required = 'catalog.can_crud_authors'
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']


class BookUpdate(PermissionRequiredMixin, generic.edit.CreateView):
    permission_required = 'catalog.can_crud_authors'
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']


class BookDelete(PermissionRequiredMixin, generic.edit.CreateView):
    permission_required = 'catalog.can_crud_authors'
    model = Book
    success_url = reverse_lazy('books')


