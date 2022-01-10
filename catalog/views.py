import datetime

from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from catalog.form import RenewBookForm
from .models import Book, Author, BookInstance


class LoanedBooksByUserListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact="o")
            .order_by("due_back")
        )


class allBooksByUserListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = "catalog/bookinstance_list_all_user.html"
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.order_by(
            "due_back"
        )


@login_required
def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()
    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1
    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_visits": num_visits,
    }
    # Render the HTML template index.html with the data in the context variable
    return render(request, "index.html", context=context)


class BookListView(LoginRequiredMixin, generic.ListView):
    login_url = "/accounts/login/"
    model = Book
    paginate_by = 2


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    login_url = "/accounts/login/"
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    login_url = "/accounts/login/"
    model = Author


@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    # If this is a POST request then process the Form data
    if request.method == "POST":
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)
        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse("all-borrowed"))
    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={"renewal_date": proposed_renewal_date})
    context = {
        "form": form,
        "book_instance": book_instance,
    }
    return render(request, "catalog/book_renew_librarian.html", context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death':'12/10/2016'}
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(LoginRequiredMixin, UpdateView):
    model = Author
    fields = '__all__'

class AuthorDelete(LoginRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(LoginRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookUpdate(LoginRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'

class BookDelete(LoginRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')