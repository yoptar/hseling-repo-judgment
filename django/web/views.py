from urllib.parse import urlencode

from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
import requests

front = "http://back:3000"
# front = 'http://localhost:3000'


def update_page_num(params: dict, page_num: int):
    params = params.copy()
    params['page_num'] = page_num
    return '?' + urlencode(params)


# @csrf_exempt
def search(req: HttpRequest):
    regions = requests.get(f'{front}/regions/').json()

    selected_region = req.GET.get('region') or '%'
    judge = req.GET.get('judge', '')
    article = req.GET.get('article', '')
    year = req.GET.get('year') or '%'
    page_num = req.GET.get('page_num', 1)

    params = {
        'region': selected_region,
        'judge': judge,
        'year': year,
        'article': article,
        'page_num': page_num
    }

    data = requests.get(f'{front}/documents/', params=params).json()
    documents = data['documents']

    page_num = data['page_num']
    max_page = data['pages']

    pages = [(i, None if i == page_num else update_page_num(params, i)) for i in range(1, max_page+1)]
    if page_num < max_page - 4:
        pages = pages[:page_num+2] + [('...', None), pages[-1]]
    if page_num > 4:
        pages = [pages[0], ('...', None)] + pages[page_num-3:]

    return render(req, 'search.html', {'regions': regions, 'selected_region': selected_region, 'judge': judge,
                                       'year': year, 'article': article, 'documents': documents, 'pages': pages})


def doc(req: HttpRequest, doc_id: int):
    data = requests.get(f'{front}/documents/{doc_id}').json()
    meta = {i: data["metadata"][i] for i in ["article", "region", "court", "date", "number", "judge", "accused"]
            if i in data["metadata"]}
    if isinstance(meta['accused'], list):
        meta['accused'] = ', '.join(meta['accused'])
    pars = {i: data["parsed"][i] for i in ["fabula", "meditation", "prove", "witness"] if i in data["parsed"]}
    download_link = f'http://localhost:3000/documents/{doc_id}/download'

    return render(req, 'lawdoc.html', {"pars": pars, "url": data["url"], "meta": meta,
                                       "header": data["header"], "download_link": download_link})
