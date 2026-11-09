from django.db import models

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.snippets.models import register_snippet

class HomePage(Page):

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["header"] = Header.objects.first()
        context["footer"] = Footer.objects.first()
        return context

@register_snippet
class Header(ClusterableModel):
    nom = models.CharField(
        max_length=100, default="Header principal",
        help_text="Nom interne, visible uniquement dans l'administration.",
    )
    logo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    texte_logo = models.CharField(max_length=100, blank=True)

    panels = [
        FieldPanel("nom"),
        MultiFieldPanel(
            [FieldPanel("logo"), FieldPanel("texte_logo")], heading="Logo"
        ),
        InlinePanel("liens", label="Lien de navigation"),
    ]

    def __str__(self):
        return self.nom


class HeaderLien(Orderable):
    header = ParentalKey(Header, on_delete=models.CASCADE, related_name="liens")
    titre = models.CharField(max_length=50)
    page = models.ForeignKey(
        "wagtailcore.Page", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text="Choisis une page du site...",
    )
    url_externe = models.URLField(blank=True, help_text="...ou une URL externe.")

    panels = [FieldPanel("titre"), FieldPanel("page"), FieldPanel("url_externe")]

    @property
    def url(self):
        return self.page.url if self.page else self.url_externe


# ---------- FOOTER ----------

@register_snippet
class Footer(ClusterableModel):
    nom = models.CharField(max_length=100, default="Footer principal")
    texte = RichTextField(blank=True, features=["bold", "italic", "link"])
    email_contact = models.EmailField(blank=True)
    page_mentions_legales = models.ForeignKey(
        "wagtailcore.Page", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text="Page « Mention légale ».",
    )
    copyright = models.CharField(max_length=150, default="© Les petits crayons")

    panels = [
        FieldPanel("nom"),
        FieldPanel("texte"),
        FieldPanel("email_contact"),
        FieldPanel("page_mentions_legales"),
        FieldPanel("copyright"),
        InlinePanel("reseaux", label="Réseau social"),
    ]

    def __str__(self):
        return self.nom
class FooterReseauSocial(Orderable):
    footer = ParentalKey(Footer, on_delete=models.CASCADE, related_name="reseaux")
    nom = models.CharField(max_length=50, help_text="Ex : Instagram, Facebook...")
    url = models.URLField()
    icone = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )

    panels = [FieldPanel("nom"), FieldPanel("url"), FieldPanel("icone")]

   