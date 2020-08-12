import re
import random as rn
import markdown2

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from . import util



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, name):   
    entry = util.get_entry(name)
    print(repr(entry))
    context = {"entry": util.convertMd(entry), "req": name}
    return render(request, "encyclopedia/entry.html", context)

## markdown2.markdown(entry)

def search(request):
    query = request.GET["q"]
    entries = util.list_entries()
    results = []
    for entry in entries:
        if query == entry:
            return HttpResponseRedirect(reverse("entry", args=(entry,))) 
        if re.search(query, entry, re.IGNORECASE):
            results.append(entry) 

    context = {"results": results, "query": query}
    return render(request, "encyclopedia/search.html", context)

def add(request):
    context = {"errMsg": False}
    if request.method == "POST":
        title = request.POST["title"]
        entries = util.list_entries()
        if title in entries:
            context = {"errMsg": True}
            return render(request, "encyclopedia/add.html", context)
        content = request.POST["content"]
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse("entry", args=(title,)))
    else:
        return render(request, "encyclopedia/add.html", context)

def edit(request, name):
    if request.method == "POST":
        title = name
        content = request.POST["content"]
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse("entry", args=(title,)))
    context = {"name": name, "content": util.get_entry(name)}
    return render(request, "encyclopedia/edit.html", context)

def random(request):
    entries = util.list_entries()
    print(rn.choice(entries))
    entry = rn.choice(entries)
    return HttpResponseRedirect(reverse("entry", args=(entry,)))


