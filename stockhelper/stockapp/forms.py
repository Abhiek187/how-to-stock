from django import forms

class ScreenerForm(forms.Form):
    # Constants
    COUNTRIES = [
        ("AI", "Anguilla"),
        ("AR", "Argentina"),
        ("AU", "Australia"),
        ("AT", "Austria"),
        ("AZ", "Azerbaijan"),
        ("BS", "Bahamas"),
        ("BD", "Bangladesh"),
        ("BB", "Barbados"),
        ("BE", "Belgium"),
        ("BM", "Bermuda"),
        ("BR", "Brazil"),
        ("BG", "Bulgaria"),
        ("KH", "Cambodia"),
        ("CA", "Canada"),
        ("KY", "Cayman Islands"),
        ("CL", "Chile"),
        ("CN", "China"),
        ("CO", "Colombia"),
        ("CK", "Cook Islands"),
        ("CR", "Costa Rica"),
        ("CI", "Côte d'Ivoire"),
        ("CW", "Curaçao"),
        ("CY", "Cyprus"),
        ("CZ", "Czech Republic"),
        ("DK", "Denmark"),
        ("DO", "Dominican Republic"),
        ("FK", "Falkland Islands"),
        ("FI", "Finland"),
        ("FO", "Faroe Islands"),
        ("FR", "France"),
        ("GA", "Gabon"),
        ("GE", "Georgia"),
        ("DE", "Germany"),
        ("GI", "Gibraltar"),
        ("GR", "Greece"),
        ("GG", "Guernsey"),
        ("HK", "Hong Kong"),
        ("HU", "Hungary"),
        ("IS", "Iceland"),
        ("IN", "India"),
        ("ID", "Indonesia"),
        ("IE", "Ireland"),
        ("IM", "Isle of Man"),
        ("IL", "Israel"),
        ("IT", "Italy"),
        ("JP", "Japan"),
        ("JE", "Jersey"),
        ("JO", "Jordan"),
        ("LI", "Liechtenstein"),
        ("LT", "Lithuania"),
        ("LU", "Luxembourg"),
        ("MO", "Macao"),
        ("MY", "Malaysia"),
        ("MT", "Malta"),
        ("MU", "Mauritius"),
        ("MX", "Mexico"),
        ("MC", "Monaco"),
        ("MN", "Mongolia"),
        ("MA", "Morocco"),
        ("NL", "Netherlands"),
        ("NZ", "New Zealand"),
        ("NG", "Nigeria"),
        ("NO", "Norway"),
        ("PA", "Panama"),
        ("PG", "Papua New Guinea"),
        ("PE", "Peru"),
        ("PH", "Philippines"),
        ("PL", "Poland"),
        ("PT", "Portugal"),
        ("PR", "Puerto Rico"),
        ("RU", "Russia"),
        ("SN", "Senegal"),
        ("SG", "Singapore"),
        ("SK", "Slovakia"),
        ("SB", "Solomon Islands"),
        ("ZA", "South Africa"),
        ("KR", "South Korea"),
        ("ES", "Spain"),
        ("SE", "Sweden"),
        ("CH", "Switzerland"),
        ("TW", "Taiwan"),
        ("TH", "Thailand"),
        ("TG", "Togo"),
        ("TR", "Turkey"),
        ("TC", "Turks and Caicos Islands"),
        ("UA", "Ukraine"),
        ("AE", "United Arab Emirates"),
        ("GB", "United Kingdom"),
        ("US", "United States"),
        ("UY", "Uruguay"),
        ("VN", "Vietnam"),
        ("VG", "Virgin Islands (U.K.)"),
        ("VI", "Virgin Islands (U.S.)"),
        ("ZM", "Zambia")
    ]

    RELATIONS = [
        # (A, B) will have the same value
        ("<",) * 2,
        (">",) * 2
    ]

    SECTORS = [
        ("Basic Materials",) * 2,
        ("Communication Services",) * 2,
        ("Conglomerates",) * 2,
        ("Consumer Cyclical",) * 2,
        ("Consumer Defensive",) * 2,
        ("Energy",) * 2,
        ("Financial",) * 2,
        ("Financial Services",) * 2,
        ("Healthcare",) * 2,
        ("Industrial Goods",) * 2,
        ("Industrials",) * 2,
        ("Real Estate",) * 2,
        ("Services",) * 2,
        ("Technology",) * 2,
        ("Utilities",) * 2
    ]

    # Fields (widgets specify the classes to put in)
    country = forms.ChoiceField(label="Country", choices=COUNTRIES, widget=forms.Select(
        attrs={"class": "country-select col form-select"}
    ))
    # Put the two fields on the same lines
    price_relation = forms.ChoiceField(choices=RELATIONS, widget=forms.Select(
        attrs={"class": "price-relation-select col form-select me-3"}
    ))
    price_value = forms.DecimalField(min_value=0, decimal_places=2, widget=forms.NumberInput(
        attrs={"class": "price-num-input col form-control"}
    ))
    sector = forms.ChoiceField(label="Sector", choices=SECTORS, widget=forms.Select(
        attrs={"class": "sector-select col form-select"}
    ))
