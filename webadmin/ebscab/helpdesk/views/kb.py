# -*- coding: utf-8 -*-

"""
Jutda Helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

views/kb.py - Public-facing knowledgebase views. The knowledgebase is a
              simple categorised question/answer system to show common
              resolutions to common problems.
"""

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from helpdesk.models import KBCategory, KBItem


def index(request):
    category_list = KBCategory.objects.all()
    # TODO: It'd be great to have a list of most popular items here.
    return render(request,
                  'helpdesk/kb_index.html',
                  {'categories': category_list})


def category(request, slug):
    category = get_object_or_404(KBCategory, slug__iexact=slug)
    items = category.kbitem_set.all()
    return render(request,
                  'helpdesk/kb_category.html',
                  {
                      'category': category,
                      'items': items
                  })


def item(request, item):
    item = get_object_or_404(KBItem, pk=item)
    return render(request,
                  'helpdesk/kb_item.html',
                  {'item': item})


def vote(request, item):
    item = get_object_or_404(KBItem, pk=item)
    vote = request.GET.get('vote', None)
    if vote in ('up', 'down'):
        item.votes += 1
        if vote == 'up':
            item.recommendations += 1
        item.save()

    return HttpResponseRedirect(item.get_absolute_url())
