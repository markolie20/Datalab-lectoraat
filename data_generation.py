"""
Script om groepen personen te genereren met Faker en op te slaan als CSV-bestanden.
"""

import os
import random
import pandas as pd
from faker import Faker
from faker.providers import DynamicProvider
from dotenv import load_dotenv

def create_weighted_provider(elements, weights):
    """
    Creëert een lijst waarin elk element wordt herhaald op basis van de bijbehorende gewicht.
    Dit maakt het mogelijk een gewogen keuze te simuleren.
    """
    weighted_elements = []
    for element, weight in zip(elements, weights):
        weighted_elements.extend([element] * weight)
    return weighted_elements

def generate_dynamic_providers(faker_instance):
    """
    Voegt dynamische providers toe aan de Faker-instantie voor verschillende attributen.
    """
    providers = {
        'country_of_origin': create_weighted_provider(
            ['Nederlands', 'Turks', 'Marokkaans', 'Surinaams', 'Antilliaans', 'Indonesisch', 'Duits', 'Pools', 'Chinees', 'Indiaas', 'Afghaans', 'Irakees', 'Somalisch', 'Syrisch', 'Eritrees', 'Roemeens', 'Bulgaars', 'Italiaans', 'Spaans', 'Portugees'],
            [40, 10, 10, 8, 5, 5, 5, 5, 7, 5, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2]
        ),
        'socio_economic_status': create_weighted_provider(
            ['Laag', 'Gemiddeld', 'Hoog'],
            [50, 30, 20]
        ),
        'household_composition': create_weighted_provider(
            ['Alleenstaand', 'Alleenstaand met kinderen', 'Samenwonend', 'Samenwonend met kinderen'],
            [25, 15, 30, 30]
        ),
        'political_orientation': ['Links', 'Midden', 'Rechts'],
        'education_level': create_weighted_provider(
            ['Basisonderwijs', 'VMBO', 'HAVO', 'VWO', 'MBO', 'HBO', 'WO'],
            [5, 20, 15, 10, 25, 15, 10]
        ),
        'religion': create_weighted_provider(
            ['Christelijk', 'Islamitisch', 'Hindoeïstisch', 'Boeddhistisch', 'Joods', 'Atheïstisch', 'Anders'],
            [35, 20, 5, 5, 5, 15, 10, 5]
        ),
        'marital_status': create_weighted_provider(
            ['Ongehuwd', 'Gehuwd', 'Gescheiden', 'Weduwe/Weduwnaar'],
            [50, 30, 15, 5]
        ),
        'employment_status': create_weighted_provider(
            ['Werkloos', 'Parttime', 'Fulltime', 'Zelfstandig', 'Student', 'Gepensioneerd'],
            [10, 20, 40, 10, 10, 10]
        ),
        'housing_type': create_weighted_provider(
            ['Appartement', 'Rijtjeshuis', 'Vrijstaand', 'Twee-onder-een-kap', 'Studio', 'Woonboot'],
            [30, 40, 10, 10, 5, 5]
        ),
        'technology_proficiency': create_weighted_provider(
            ['Digibeet', 'Beginner', 'Intermediate', 'Advanced', 'Expert'],
            [10, 30, 30, 20, 10]
        ),
    }

    for provider_name, elements in providers.items():
        dynamic_provider = DynamicProvider(provider_name=provider_name, elements=elements)
        faker_instance.add_provider(dynamic_provider)
    
    age_provider = DynamicProvider(provider_name='age_provider', elements=list(range(18, 100)))
    faker_instance.add_provider(age_provider)

def generate_people(faker_instance, num_people):
    """
    Genereert een DataFrame met nepprofielen.
    Elk profiel bevat een standaard set velden uit Faker's profile() en wordt uitgebreid
    met extra, dynamisch gegenereerde attributen.
    """
    people = []
    for _ in range(num_people):
        # Basisprofiel met een aantal velden
        person = faker_instance.profile(fields=['name', 'sex', 'job'])
        # Toevoegen van extra attributen via de dynamische providers
        person.update({
            'country_of_origin': faker_instance.country_of_origin(),
            'socio_economic_status': faker_instance.socio_economic_status(),
            'household_composition': faker_instance.household_composition(),
            'political_orientation': faker_instance.political_orientation(),
            'education_level': faker_instance.education_level(),
            'religion': faker_instance.religion(),
            'marital_status': faker_instance.marital_status(),
            'employment_status': faker_instance.employment_status(),
            'housing_type': faker_instance.housing_type(),
            'technology_proficiency': faker_instance.technology_proficiency(),
            'age': faker_instance.age_provider(),
        })
        people.append(person)
    return pd.DataFrame(people)

def main():
    # Initialisatie en setup
    faker_instance = Faker('nl_NL')
    Faker.seed(313)
    random.seed(313)
    
    GROUP_DATA_FOLDER = "data/groups"
    GROUP_AMOUNT = 1000
    MIN_PEOPLE = 10
    MAX_PEOPLE = 35
    
    # Zorg dat de outputmap bestaat
    os.makedirs(GROUP_DATA_FOLDER, exist_ok=True)
    
    # Bepaal per groep het aantal personen
    people_per_group = [random.randint(MIN_PEOPLE, MAX_PEOPLE) for _ in range(GROUP_AMOUNT)]
    
    # Voeg dynamische providers toe aan de Faker-instantie
    generate_dynamic_providers(faker_instance)
    
    # Genereer groepen en sla ze op als CSV-bestand
    for group_id, group_size in enumerate(people_per_group):
        people_df = generate_people(faker_instance, group_size)
        filepath = os.path.join(GROUP_DATA_FOLDER, f"group_{group_id+1}.csv")
        people_df.to_csv(filepath, index=False)
        print(f"Generated {group_size} people and saved to group_{group_id+1}.csv")

if __name__ == "__main__":
    main()
