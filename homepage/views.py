from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpRequest
from django.template import loader
from homepage.utils.generateImage.helpers import generate_image
from homepage.utils.parseImage.main import parseImage


def hello(request):
    template = loader.get_template("index.html")
    context = {
        "firstname": "Linus",
    }
    return HttpResponse(template.render(context))


def generateImage(request: HttpRequest):
    idea = request.GET.get("idea")
    template = loader.get_template("preview.html")
    generate_image("a screenshot of a " + idea, "homepage/static/idea.png")
    context = {
        "idea": idea,
    }
    return HttpResponse(template.render(context))


def parseWebsite(request: HttpRequest):
    # imageUrl: str, outputPath: str, resourcesPath: str)
    parseImage(
        "homepage/static/idea.png", "homepage/templates/output.html", "homepage/static"
    )
    return HttpResponse("Parsed website")


def showParsedWebsite(request: HttpRequest):
    template = loader.get_template("output.html")

    return HttpResponse(template.render())
