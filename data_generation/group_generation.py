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
            [70, 10, 10, 8, 5, 5, 5, 5, 7, 5, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2]
        ),
        'socio_economic_status': create_weighted_provider(
            ['Laag', 'Gemiddeld', 'Hoog'],
            [50, 30, 20]
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
        'housing_type': create_weighted_provider(
            ['Appartement', 'Rijtjeshuis', 'Vrijstaand', 'Twee-onder-een-kap', 'Studio', 'Woonboot'],
            [30, 40, 10, 10, 5, 5]
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
        age = faker_instance.age_provider()
        marital_status = get_marital_status(age)
        socio_economic_status = faker_instance.socio_economic_status()
        employment_status = get_employment_status(age)
        health_status = get_health_status(age)
        technology_proficiency = get_technology_proficiency(age)
        income = get_income(socio_economic_status)
        household = household_composition(age, marital_status)

        person.update({
            'country_of_origin': faker_instance.country_of_origin(),
            'socio_economic_status': socio_economic_status,
            'household_composition': household,
            'political_orientation': faker_instance.political_orientation(),
            'education_level': faker_instance.education_level(),
            'religion': faker_instance.religion(),
            'marital_status': marital_status,
            'employment_status': employment_status,
            'housing_type': faker_instance.housing_type(),
            'technology_proficiency': technology_proficiency,
            'health_status': health_status,
            'income': income,
            'age': age,
        })
        people.append(person)
    return pd.DataFrame(people)

def generate_person(faker_instance):
    # Generate core attributes (e.g., age, name, sex, job)
    base_profile = faker_instance.profile(fields=['name', 'sex'])
    age = faker_instance.age_provider()
    base_profile['age'] = age
    return base_profile

import random

def get_employment_status(age):
    if age < 25:
        # Most under 25 are likely students.
        return random.choices(
            ['Student', 'Fulltime', 'Zelfstandig'], 
            weights=[80, 10, 2])
    elif age < 65:
        # Working age: mix between full-time, part-time, and self-employed.
        return random.choices(
            ['Parttime', 'Fulltime', 'Zelfstandig'], 
            weights=[20, 50, 30]
        )[0]
    else:
        # Older than 65 might be retired.
        return random.choices(
            ['Gepensioneerd', 'Parttime'], 
            weights=[70, 30]
        )[0]

def get_marital_status(age):
    if age < 25:
        return 'Ongehuwd'
    elif age < 35:
        return random.choices(
            ['Ongehuwd', 'Gehuwd'], 
            weights=[70, 30]
        )[0]
    elif age < 50:
        return random.choices(
            ['Gehuwd', 'Gescheiden', 'Ongehuwd'], 
            weights=[60, 20, 20]
        )[0]
    else:
        return random.choices(
            ['Gehuwd', 'Gescheiden', 'Weduwe/Weduwnaar'], 
            weights=[50, 30, 20]
        )[0]

def get_health_status(age):
    if age < 40:
        return random.choices(
            ['Zeer goed', 'Goed', 'Redelijk', 'Slecht'], 
            weights=[50, 30, 15, 5]
        )[0]
    elif age < 65:
        return random.choices(
            ['Zeer goed', 'Goed', 'Redelijk', 'Slecht'], 
            weights=[30, 40, 20, 10]
        )[0]
    else:
        return random.choices(
            ['Zeer goed', 'Goed', 'Redelijk', 'Slecht'], 
            weights=[10, 20, 30, 40]
        )[0]

def get_income(socio_economic_status):
    if socio_economic_status == 'Laag':
        return random.choices(
            ['Laag', 'Gemiddeld'], 
            weights=[70, 30]
        )[0]
    elif socio_economic_status == 'Gemiddeld':
        return random.choices(
            ['Gemiddeld', 'Hoog'], 
            weights=[60, 40]
        )[0]
    else:
        return 'Hoog'

def get_technology_proficiency(age):
    if age < 25:
        return random.choices(
            ['Beginner', 'Intermediate', 'Advanced', 'Expert'], 
            weights=[10, 30, 40, 20]
        )[0]
    elif age < 50:
        return random.choices(
            ['Beginner', 'Intermediate', 'Advanced', 'Expert'], 
            weights=[5, 20, 50, 25]
        )[0]
    else:
        return random.choices(
            ['Beginner', 'Intermediate', 'Advanced'], 
            weights=[10, 40, 50]
        )[0]

def household_composition(age, marital_status):
    if marital_status == 'Ongehuwd':
        if age < 25:
            return random.choices(
                ['Bij ouders', 'Alleenstaand', 'Samenwonend'], 
                weights=[60, 30, 20]
            )[0]
        elif age < 35:
            return random.choices(
                ['Alleenstaand', 'Samenwonend', 'Alleenstaand met kinderen'], 
                weights=[50, 10, 20]
            )[0]
        elif age < 50:
            return random.choices(
                ['Samenwonend', 'Alleenstaand', 'Samenwonend met kinderen'], 
                weights=[10, 70, 5]
            )[0]
        else:
            return random.choices(
                ['Samenwonend', 'Weduwe/Weduwnaar'], 
                weights=[70, 30]
            )[0]

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
