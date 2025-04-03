from faker import Faker
from faker.providers import DynamicProvider
import random
from dotenv import load_dotenv
import os
import json
import pandas as pd

faker = Faker('nl_NL')
Faker.seed(313)
random.seed(313)

GROUP_DATA_FOLDER = "data/groups"
GROUP_AMOUNT = 1000
MIN_PEOPLE = 10
MAX_PEOPLE = 35

people_per_group = [random.randint(MIN_PEOPLE, MAX_PEOPLE) for _ in range(GROUP_AMOUNT)]
os.makedirs(GROUP_DATA_FOLDER, exist_ok=True)

country_of_origin_provider = ['Nederlands', 'Turks', 'Marokkaans', 'Surinaams', 'Antilliaans', 'Indonesisch', 'Duits', 'Pools', 'Chinees', 'Indiaas', 'Moluks', 'Arabisch', 'Engels', 'Frans', 'Somalisch', 'Syrisch', 'Irakees', 'Afghaan', 'Irakees', 'Syrisch']
socio_economic_status_provider = ['Laag', 'Gemiddeld', 'Hoog']
Household_composition_provider = ['Alleenstaand', 'Alleenstaand met kinderen', 'Samenwonend', 'Samenwonend met kinderen']
political_orientation_provider = ['Links', 'Midden', 'Rechts']
education_level_provider = ['Basisonderwijs', 'VMBO', 'HAVO', 'VWO', 'MBO', 'HBO', 'WO']
religion_provider = ['Christelijk', 'Islamitisch', 'Hindoeïstisch', 'Boeddhistisch', 'Joods', 'Geen religie', 'Anders']
marital_status_provider = ['Ongehuwd', 'Gehuwd', 'Gescheiden', 'Weduwe/Weduwnaar']
employment_status_provider = ['Werkloos', 'Parttime', 'Fulltime', 'Zelfstandig', 'Student', 'Gepensioneerd']
housing_type_provider = ['Appartement', 'Rijtjeshuis', 'Vrijstaand', 'Twee-onder-een-kap', 'Studio', 'Woonboot']
technology_proficiency_provider = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
other_difficulties_provider = ['Geen', 'Visuele beperking', 'Auditieve beperking', 'Motorische beperking', 'Psychische beperking']

def create_weighted_provider(elements, weights):
    weighted_elements = []
    for element, weight in zip(elements, weights):
        weighted_elements.extend([element] * weight)
    return weighted_elements

# Weighted providers for various attributes
country_of_origin_provider = create_weighted_provider(
    ['Nederlands', 'Turks', 'Marokkaans', 'Surinaams', 'Antilliaans', 'Indonesisch', 'Duits', 'Pools', 'Chinees', 'Indiaas'],
    [40, 10, 10, 8, 5, 5, 5, 5, 7, 5]  # Example weights
)

socio_economic_status_provider = create_weighted_provider(
    ['Laag', 'Gemiddeld', 'Hoog'],
    [50, 30, 20]  # Example weights
)

Household_composition_provider = create_weighted_provider(
    ['Alleenstaand', 'Alleenstaand met kinderen', 'Samenwonend', 'Samenwonend met kinderen'],
    [25, 15, 30, 30]  # Example weights
)

political_orientation_provider = create_weighted_provider(
    ['Links', 'Midden', 'Rechts'],
    [30, 50, 20]  # Example weights
)

education_level_provider = create_weighted_provider(
    ['Basisonderwijs', 'VMBO', 'HAVO', 'VWO', 'MBO', 'HBO', 'WO'],
    [5, 20, 15, 10, 25, 15, 10]  # Example weights
)

religion_provider = create_weighted_provider(
    ['Christelijk', 'Islamitisch', 'Hindoeïstisch', 'Boeddhistisch', 'Joods', 'Geen religie', 'Anders'],
    [40, 20, 5, 5, 5, 20, 5]  # Example weights
)

marital_status_provider = create_weighted_provider(
    ['Ongehuwd', 'Gehuwd', 'Gescheiden', 'Weduwe/Weduwnaar'],
    [50, 30, 15, 5]  # Example weights
)

employment_status_provider = create_weighted_provider(
    ['Werkloos', 'Parttime', 'Fulltime', 'Zelfstandig', 'Student', 'Gepensioneerd'],
    [10, 20, 40, 10, 10, 10]  # Example weights
)

housing_type_provider = create_weighted_provider(
    ['Appartement', 'Rijtjeshuis', 'Vrijstaand', 'Twee-onder-een-kap', 'Studio', 'Woonboot'],
    [30, 40, 10, 10, 5, 5]  # Example weights
)

technology_proficiency_provider = create_weighted_provider(
    ['Beginner', 'Intermediate', 'Advanced', 'Expert'],
    [40, 30, 20, 10]  # Example weights
)

other_difficulties_provider = create_weighted_provider(
    ['Geen', 'Visuele beperking', 'Auditieve beperking', 'Motorische beperking', 'Psychische beperking'],
    [70, 10, 5, 5, 10]  # Example weights
)

# Example: Adjusting the distribution for socio_economic_status
socio_economic_status_provider = create_weighted_provider(
    ['Laag', 'Gemiddeld', 'Hoog'],
    [50, 30, 20]  # 50% Laag, 30% Gemiddeld, 20% Hoog
)

def generate_dynamic_provider(**kwargs):
    for name, elements in kwargs.items():
        provider = DynamicProvider(provider_name=name, elements=elements)
        faker.add_provider(provider)

generate_dynamic_provider(
    country_of_origin=country_of_origin_provider,
    socio_economic_status=socio_economic_status_provider,
    household_composition=Household_composition_provider,
    political_orientation=political_orientation_provider,
    education_level=education_level_provider,
    religion=religion_provider,
    marital_status=marital_status_provider,
    employment_status=employment_status_provider,
    housing_type=housing_type_provider,
    technology_proficiency=technology_proficiency_provider
)



def generate_people(num_people):
    people = []
    for _ in range(num_people):
        person = faker.profile(fields=['name', 'sex', 'birthdate', 'job'])
        person.update({
            'country_of_origin': faker.country_of_origin(),
            'socio_economic_status': faker.socio_economic_status(),
            'household_composition': faker.household_composition(),
            'political_orientation': faker.political_orientation(),
            'education_level': faker.education_level(),
            'religion': faker.religion(),
            'marital_status': faker.marital_status(),
            'employment_status': faker.employment_status(),
            'housing_type': faker.housing_type(),
            'technology_proficiency': faker.technology_proficiency(),
        })
        people.append(person)
    people_df = pd.DataFrame(people)
    return people_df

for id, group_size in enumerate(people_per_group):
    people_df = generate_people(group_size)
    filepath = os.path.join(GROUP_DATA_FOLDER, f"group_{id}.csv")
    people_df.to_csv(filepath, index=False)
    print(f"Generated {group_size} people and saved to group_{id}.json")
