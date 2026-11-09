from django.db import models

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.models import Orderable, Page
from wagtail.snippets.models import register_snippet
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock


class BoutonBlock(blocks.StructBlock):
    titre = blocks.CharBlock(max_length=50, label="Texte du bouton")
    page = blocks.PageChooserBlock(required=False, label="Page du site")
    url_externe = blocks.URLBlock(required=False, label="ou lien externe")

    class Meta:
        icon = "link"
        label = "Bouton"


class GalerieBlock(blocks.ListBlock):
    class Meta:
        icon = "image"
        label = "Galerie d'images"


class GalerieItemBlock(blocks.StructBlock):
    image = ImageChooserBlock(label="Image")
    legende = blocks.CharBlock(required=False, max_length=100, label="Légende")
    bouton_titre = blocks.CharBlock(
        required=False, max_length=50, label="Texte du bouton",
        help_text="Laisse vide pour ne pas afficher de bouton.",
    )
    page = blocks.PageChooserBlock(required=False, label="Page du site")
    url_externe = blocks.URLBlock(required=False, label="ou lien externe")

    class Meta:
        icon = "image"
        label = "Image de la galerie"

class HomePage(Page):
    body = StreamField(
        [
            ("titre", blocks.CharBlock(form_classname="title", label="Titre de section")),
            ("texte", blocks.RichTextBlock(features=["bold", "italic", "link", "ol", "ul"])),
            ("image", ImageChooserBlock(label="Illustration")),
            ("galerie", GalerieBlock(ImageChooserBlock())),
            ("galerie_boutons", blocks.ListBlock(GalerieItemBlock(), label="Galerie avec boutons")),
            ("bouton", BoutonBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

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

@register_snippet
class Footer(ClusterableModel):
    nom = models.CharField(max_length=100, default="Footer principal")
    titre = models.CharField(
        max_length=100, blank=True,
        help_text="Titre affiché au centre du footer.",
    )
    texte = RichTextField(blank=True, features=["bold", "italic", "link"])
    email_contact = models.EmailField(
        blank=True, help_text="Devient un lien cliquable (mailto).",
    )
    adresse = models.TextField(
        blank=True, help_text="Une ligne par retour à la ligne.",
    )
    logo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text="Logo affiché à droite du footer.",
    )
    page_mentions_legales = models.ForeignKey(
        "wagtailcore.Page", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text="Page « Mention légale ».",
    )
    copyright = models.CharField(max_length=150, default="© Les petits crayons")

    panels = [
        FieldPanel("nom"),
        FieldPanel("titre"),
        FieldPanel("texte"),
        MultiFieldPanel(
            [FieldPanel("email_contact"), FieldPanel("adresse")],
            heading="Coordonnées",
        ),
        InlinePanel("reseaux", label="Réseau social"),
        FieldPanel("logo"),
        FieldPanel("page_mentions_legales"),
        FieldPanel("copyright"),
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

   