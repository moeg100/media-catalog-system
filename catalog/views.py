from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import MediaItem
from .forms import MediaItemForm

class MediaListView(ListView):
    model = MediaItem
    template_name = 'catalog/media_list.html'
    context_object_name = 'media_items'

class MediaDetailView(DetailView):
    model = MediaItem
    template_name = 'catalog/media_detail.html'
    context_object_name = 'media'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

class MediaCreateView(CreateView):
    model = MediaItem
    form_class = MediaItemForm
    template_name = 'catalog/media_form.html'

class MediaUpdateView(UpdateView):
    model = MediaItem
    form_class = MediaItemForm
    template_name = 'catalog/media_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

class MediaDeleteView(DeleteView):
    model = MediaItem
    template_name = 'catalog/media_confirm_delete.html'
    success_url = reverse_lazy('catalog:media_list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
