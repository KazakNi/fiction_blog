from django.core.paginator import Paginator


def pages_per_page(request, objects, amount_per_page):
    paginator = Paginator(objects, amount_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
