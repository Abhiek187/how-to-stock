from django import forms

class ScreenerForm(forms.Form):
    # Constants
    REGIONS = [
        ("Argentina",) * 2, # (A, B) will have the same value
        ("Australia",) * 2,
        ("Austria",) * 2,
        ("Belgium",) * 2,
        ("Brazil",) * 2,
        ("Canada",) * 2,
        ("China",) * 2,
        ("Denmark",) * 2,
        ("Estonia",) * 2,
        ("Finland",) * 2,
        ("France",) * 2,
        ("Germany",) * 2,
        ("Greece",) * 2,
        ("Hong Kong",) * 2,
        ("Iceland",) * 2,
        ("India",) * 2,
        ("Indonesia",) * 2,
        ("Ireland",) * 2,
        ("Israel",) * 2,
        ("Italy",) * 2,
        ("Latvia",) * 2,
        ("Lithuania",) * 2,
        ("Malaysia",) * 2,
        ("Mexico",) * 2,
        ("Netherlands",) * 2,
        ("New Zealand",) * 2,
        ("Norway",) * 2,
        ("Portugal",) * 2,
        ("Qatar",) * 2,
        ("Russia",) * 2,
        ("Singapore",) * 2,
        ("South Korea",) * 2,
        ("Spain",) * 2,
        ("Sweden",) * 2,
        ("Switzerland",) * 2,
        ("Taiwan",) * 2,
        ("Thailand",) * 2,
        ("Turkey",) * 2,
        ("United Kingdom",) * 2,
        ("USA",) * 2,
        ("Venezuela",) * 2
    ]

    RELATIONS = [
        ("=",) * 2,
        ("<",) * 2,
        (">",) * 2
    ]

    SECTORS = [
        ("Advertising",) * 2,
        ("Agricultural",) * 2,
        ("Air",) * 2,
        ("Auto",) * 2,
        ("Bank",) * 2,
        ("Broadcasting",) * 2,
        ("Business",) * 2,
        ("Communication",) * 2,
        ("Computer",) * 2,
        ("Defense",) * 2,
        ("Diversified",) * 2,
        ("Drug",) * 2,
        ("Education",) * 2,
        ("Electric",) * 2,
        ("Farm",) * 2,
        ("Food",) * 2,
        ("Foreign",) * 2,
        ("Gaming",) * 2,
        ("General",) * 2,
        ("Health",) * 2,
        ("Home",) * 2,
        ("Industrial",) * 2,
        ("Information",) * 2,
        ("Insurance",) * 2,
        ("Internet",) * 2,
        ("Investment",) * 2,
        ("Management",) * 2,
        ("Marketing",) * 2,
        ("Medical",) * 2,
        ("Movie",) * 2,
        ("Music",) * 2,
        ("Oil",) * 2,
        ("Property",) * 2,
        ("Publishing",) * 2,
        ("Security",) * 2,
        ("Semiconductor",) * 2,
        ("Services",) * 2,
        ("Software",) * 2,
        ("Specialty",) * 2,
        ("Sporting",) * 2,
        ("Textile",) * 2
    ]

    # Fields (widgets specify the classes to put in)
    region = forms.ChoiceField(label="Region", choices=REGIONS, widget=forms.Select(attrs={"class": "region-select col form-select"}))
    # Put the two fields on the same lines
    price_relation = forms.ChoiceField(choices=RELATIONS, widget=forms.Select(attrs={"class": "price-relation-select col form-select me-3"}))
    price_value = forms.DecimalField(min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={"class": "price-num-input col form-control"}))
    sector = forms.ChoiceField(label="Sector", choices=SECTORS, widget=forms.Select(attrs={"class": "sector-select col form-select"}))
