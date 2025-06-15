import os
import random
import pandas as pd
from faker import Faker
from faker.providers import DynamicProvider
from dotenv import load_dotenv 
import json

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
            ['Christelijk', 'Islamitisch', 'Hindoeïstisch', 'Boeddhistisch', 'Joods', 'Atheïstisch', 'Anders', 'Geen'], # Added 'Geen'
            [30, 15, 5, 5, 2, 25, 8, 10]
        ),
        'housing_type': create_weighted_provider(
            ['Appartement', 'Rijtjeshuis', 'Vrijstaand', 'Twee-onder-een-kap', 'Studio', 'Woonboot'],
            [30, 40, 10, 10, 5, 5]
        ),
        'activity_level_provider': create_weighted_provider(
            ['Laag', 'Gemiddeld', 'Hoog'],
            [30, 50, 20]
        ),
        'response_latency_profile_provider': create_weighted_provider(
            ['Onmiddellijk', 'Korte vertraging', 'Lange vertraging', 'Variabel'],
            [30, 40, 15, 15]
        ),
        'emoji_usage_propensity_provider': create_weighted_provider(
            ['Geen', 'Laag', 'Gemiddeld', 'Hoog'],
            [20, 30, 30, 20]
        ),
        'mention_propensity_provider': create_weighted_provider(
            ['Laag', 'Gemiddeld', 'Hoog'],
            [50, 40, 10]
        ),
        'message_length_preference_provider': create_weighted_provider(
            ['Kort', 'Lang', 'Gemengd'],
            [40, 20, 40]
        ),
        'punctuation_habits_provider': create_weighted_provider(
            ['Correct', 'Schaars', 'Overmatig'],
            [50, 30, 20]
        ),
        'spelling_error_frequency_provider': create_weighted_provider(
            ['Geen', 'Laag', 'Gemiddeld', 'Hoog'],
            [40, 30, 20, 10]
        ),
        'grammar_correctness_provider': create_weighted_provider(
            ['Correct', 'Informeel', 'Slecht'],
            [50, 35, 15]
        ),
        'language_style_provider': create_weighted_provider(
            ['Formeel', 'Informeel', 'Straattaal', 'Vakjargon'],
            [20, 50, 15, 15]
        ),
        'emphasis_style_provider': create_weighted_provider(
            ['Geen', 'Soms HOOFDLETTERS', 'Veel uitroeptekens', 'Gemengd'],
            [50, 20, 20, 10]
        ),
        'message_chaining_preference_provider': create_weighted_provider(
            ['Eén lange boodschap', 'Meerdere korte boodschappen', 'Gemengd'],
            [30, 40, 30]
        ),
    }

    for provider_name, elements in providers.items():
        dynamic_provider = DynamicProvider(provider_name=provider_name, elements=elements)
        faker_instance.add_provider(dynamic_provider)
    
    age_provider = DynamicProvider(provider_name='age_provider', elements=list(range(18, 90)))
    faker_instance.add_provider(age_provider)

def get_employment_status(age):
    if age < 18: 
        return 'Niet van toepassing'
    if age < 25:
        return random.choices(
            ['Student', 'Fulltime', 'Parttime', 'Zelfstandig', 'Werkzoekend'],
            weights=[60, 15, 10, 5, 10]
        )[0]
    elif age < 67:
        return random.choices(
            ['Fulltime', 'Parttime', 'Zelfstandig', 'Werkzoekend'],
            weights=[50, 25, 15, 10]
        )[0]
    else:
        return random.choices(
            ['Gepensioneerd', 'Parttime', 'Vrijwilligerswerk'],
            weights=[80, 10, 10]
        )[0]

def get_marital_status(age):
    if age < 25:
        return random.choices(['Ongehuwd', 'Relatie'], weights=[85,15])[0]
    elif age < 35:
        return random.choices(
            ['Ongehuwd', 'Gehuwd', 'Samenwonend', 'Relatie'],
            weights=[40, 30, 20, 10]
        )[0]
    elif age < 50:
        return random.choices(
            ['Gehuwd', 'Gescheiden', 'Ongehuwd', 'Samenwonend', 'Weduwe/Weduwnaar'],
            weights=[55, 20, 10, 10, 5]
        )[0]
    else:
        return random.choices(
            ['Gehuwd', 'Gescheiden', 'Weduwe/Weduwnaar', 'Samenwonend', 'Ongehuwd'],
            weights=[45, 25, 20, 5, 5]
        )[0]

def get_health_status(age):
    if age < 40:
        return random.choices(
            ['Zeer goed', 'Goed', 'Redelijk', 'Matig', 'Slecht'],
            weights=[45, 35, 15, 3, 2]
        )[0]
    elif age < 65:
        return random.choices(
            ['Zeer goed', 'Goed', 'Redelijk', 'Matig', 'Slecht'],
            weights=[25, 40, 25, 7, 3]
        )[0]
    else:
        return random.choices(
            ['Goed', 'Redelijk', 'Matig', 'Slecht', 'Zeer slecht'],
            weights=[20, 35, 25, 15, 5]
        )[0]

def get_income_level(socio_economic_status, employment_status):
    if employment_status in ['Student', 'Werkzoekend']:
        return 'Laag'
    if socio_economic_status == 'Laag':
        return random.choices(['Laag', 'Beneden gemiddeld'], weights=[80, 20])[0]
    elif socio_economic_status == 'Gemiddeld':
        return random.choices(['Beneden gemiddeld', 'Gemiddeld', 'Boven gemiddeld'], weights=[20, 60, 20])[0]
    else: 
        return random.choices(['Boven gemiddeld', 'Hoog'], weights=[30, 70])[0]


def get_technology_proficiency(age):
    if age < 25:
        return random.choices(
            ['Beginner', 'Gemiddeld', 'Gevorderd', 'Expert'],
            weights=[5, 25, 45, 25]
        )[0]
    elif age < 50:
        return random.choices(
            ['Beginner', 'Gemiddeld', 'Gevorderd', 'Expert'],
            weights=[5, 20, 50, 25]
        )[0]
    elif age < 65:
        return random.choices(
            ['Beginner', 'Gemiddeld', 'Gevorderd'],
            weights=[20, 50, 30]
        )[0]
    else:
        return random.choices(
            ['Zeer beperkt', 'Beginner', 'Gemiddeld'],
            weights=[30, 45, 25]
        )[0]

def household_composition(age, marital_status, employment_status):
    if marital_status == 'Ongehuwd' or marital_status == 'Relatie':
        if age < 25:
            if employment_status == 'Student':
                return random.choices(['Bij ouders', 'Op kamers/Studio', 'Samenwonend (met partner/huisgenoten)'], weights=[40, 40, 20])[0]
            return random.choices(['Bij ouders', 'Alleenstaand', 'Samenwonend (met partner/huisgenoten)'], weights=[30, 40, 30])[0]
        elif age < 35:
            return random.choices(['Alleenstaand', 'Samenwonend (met partner)', 'Alleenstaande ouder'], weights=[50, 40, 10])[0]
        else:
            return random.choices(['Alleenstaand', 'Samenwonend (met partner)', 'Alleenstaande ouder', 'Woongroep'], weights=[60, 20, 15, 5])[0]
    elif marital_status == 'Gehuwd' or marital_status == 'Samenwonend':
        if age < 30:
            return random.choices(['Samenwonend zonder kinderen', 'Samenwonend met jonge kinderen'], weights=[60, 40])[0]
        elif age < 50:
            return random.choices(['Samenwonend met kinderen', 'Samenwonend zonder kinderen (kinderen uit huis/geen kinderen)'], weights=[70, 30])[0]
        else: # 50+
            return random.choices(['Samenwonend zonder inwonende kinderen', 'Samenwonend met volwassen kinderen'], weights=[85, 15])[0]
    elif marital_status == 'Gescheiden':
        if age < 40:
            return random.choices(['Alleenstaand', 'Alleenstaande ouder', 'Nieuwe partner, samengesteld gezin'], weights=[40, 45, 15])[0]
        else:
            return random.choices(['Alleenstaand', 'Alleenstaande ouder (oudere kinderen)', 'Nieuwe partner'], weights=[50, 30, 20])[0]
    elif marital_status == 'Weduwe/Weduwnaar':
        return random.choices(['Alleenstaand', 'Alleenstaand (kinderen uit huis)', 'Bij familie'], weights=[70, 20, 10])[0]
    return 'Onbekend' 

def get_typical_online_hours(age, employment_status):
    hours = { "weekdays": [], "weekends": [] }
    
    if employment_status == 'Student':
        hours["weekdays"] = random.choice([
            ["10:00-13:00", "17:00-20:00", "22:00-01:00"],
            ["13:00-16:00", "19:00-23:00"],
            ["09:00-12:00", "15:00-18:00", "21:00-00:00"]
        ])
    elif employment_status in ['Fulltime', 'Parttime', 'Zelfstandig']:
        hours["weekdays"] = random.choice([
            ["07:00-09:00", "12:00-13:00", "18:00-22:00"],
            ["19:00-23:00"],
            ["08:00-10:00", "17:00-21:00"]
        ])
    elif employment_status == 'Werkzoekend':
        hours["weekdays"] = random.choice([
            ["09:00-17:00"],
            ["10:00-14:00", "19:00-22:00"],
        ])
    elif employment_status == 'Gepensioneerd':
        hours["weekdays"] = random.choice([
            ["09:00-12:00", "14:00-17:00"],
            ["10:00-15:00", "19:00-21:00"],
            ["08:00-11:00", "13:00-16:00", "20:00-22:00"]
        ])
    else:
         hours["weekdays"] = ["19:00-22:00"]

    if age < 30:
        hours["weekends"] = random.choice([
            ["11:00-15:00", "19:00-02:00"],
            ["14:00-18:00", "20:00-00:00"],
            ["Gehele dag met onderbrekingen"]
        ])
    elif age < 65:
        hours["weekends"] = random.choice([
            ["10:00-13:00", "16:00-22:00"],
            ["09:00-12:00", "15:00-18:00", "20:00-23:00"],
            ["Sporadisch gedurende de dag"]
        ])
    else: # 65+
        hours["weekends"] = random.choice([
            ["09:00-12:00", "14:00-17:00", "19:00-21:00"],
            ["10:00-16:00"],
            ["Flexibel, meerdere korte periodes"]
        ])
    return hours  

def generate_people(faker_instance, num_people):
    """
    Genereert een DataFrame met nepprofielen.
    """
    people = []
    for _ in range(num_people):
        person = faker_instance.profile(fields=['name', 'sex', 'job', 'birthdate']) 
        
        age = faker_instance.age_provider()
        marital_status = get_marital_status(age)
        socio_economic_status = faker_instance.socio_economic_status()
        employment_status = get_employment_status(age)
        health_status = get_health_status(age)
        technology_proficiency = get_technology_proficiency(age)
        income = get_income_level(socio_economic_status, employment_status)
        household = household_composition(age, marital_status, employment_status)
        education = faker_instance.education_level()

        activity_level = faker_instance.activity_level_provider()
        typical_online_hours = get_typical_online_hours(age, employment_status) 
        
        base_latency = faker_instance.response_latency_profile_provider()
        if age > 60 or technology_proficiency in ['Zeer beperkt', 'Beginner']:
            latency_options = ['Korte vertraging', 'Lange vertraging', 'Variabel']
            if base_latency == 'Onmiddellijk': 
                 base_latency = random.choice(latency_options)
        response_latency_profile = base_latency

        base_emoji = faker_instance.emoji_usage_propensity_provider()
        if age > 50 or technology_proficiency in ['Zeer beperkt', 'Beginner']:
            emoji_options = ['Geen', 'Laag']
            if base_emoji in ['Gemiddeld', 'Hoog']:
                base_emoji = random.choice(emoji_options)
        elif age < 25 and technology_proficiency in ['Gevorderd', 'Expert']:
            emoji_options = ['Gemiddeld', 'Hoog']
            if base_emoji in ['Geen', 'Laag']:
                base_emoji = random.choice(emoji_options)
        emoji_usage_propensity = base_emoji

        mention_propensity = faker_instance.mention_propensity_provider()
        message_length_preference = faker_instance.message_length_preference_provider()

        base_punctuation = faker_instance.punctuation_habits_provider()
        base_spelling = faker_instance.spelling_error_frequency_provider()
        base_grammar = faker_instance.grammar_correctness_provider()

        if education in ['Basisonderwijs', 'VMBO']:
            if base_punctuation == 'Correct': base_punctuation = random.choice(['Schaars', 'Overmatig', 'Correct']) # less likely correct
            if base_spelling == 'Geen': base_spelling = random.choice(['Laag', 'Gemiddeld', 'Hoog'])
            if base_grammar == 'Correct': base_grammar = random.choice(['Informeel', 'Slecht'])
        elif education in ['HBO', 'WO']:
            if base_punctuation != 'Correct': base_punctuation = random.choices(['Correct', base_punctuation], weights=[70,30])[0]
            if base_spelling != 'Geen': base_spelling = random.choices(['Geen', base_spelling], weights=[70,30])[0]
            if base_grammar != 'Correct': base_grammar = random.choices(['Correct', base_grammar], weights=[80,20])[0]

        punctuation_habits = base_punctuation
        spelling_error_frequency = base_spelling
        grammar_correctness = base_grammar

        # Language style influenced by age/job
        base_language_style = faker_instance.language_style_provider()
        current_job = person.get('job', '').lower()
        if age > 55 or any(term in current_job for term in ['directeur', 'manager', 'advocaat', 'arts', 'professor']):
            if base_language_style == 'Straattaal': base_language_style = 'Informeel'
            elif base_language_style == 'Informeel' and random.random() < 0.3: base_language_style = 'Formeel'
        elif age < 25:
             if base_language_style == 'Formeel': base_language_style = 'Informeel'
             elif base_language_style == 'Informeel' and random.random() < 0.3: base_language_style = 'Straattaal'
        language_style = base_language_style
        
        emphasis_style = faker_instance.emphasis_style_provider()
        message_chaining_preference = faker_instance.message_chaining_preference_provider()

        person.update({
            'country_of_origin': faker_instance.country_of_origin(),
            'socio_economic_status': socio_economic_status,
            'household_composition': household,
            'political_orientation': faker_instance.political_orientation(),
            'education_level': education,
            'religion': faker_instance.religion(),
            'marital_status': marital_status,
            'employment_status': employment_status,
            'housing_type': faker_instance.housing_type(),
            'technology_proficiency': technology_proficiency,
            'health_status': health_status,
            'income_level': income, 
            'age': age,
            'activity_level': activity_level,
            'typical_online_hours': typical_online_hours,
            'response_latency_profile': response_latency_profile,
            'emoji_usage_propensity': emoji_usage_propensity,
            'mention_propensity': mention_propensity,
            'message_length_preference': message_length_preference,
            'punctuation_habits': punctuation_habits,
            'spelling_error_frequency': spelling_error_frequency,
            'grammar_correctness': grammar_correctness,
            'language_style': language_style,
            'emphasis_style': emphasis_style,
            'message_chaining_preference': message_chaining_preference,
        })
        people.append(person)
    df = pd.DataFrame(people)
    if 'typical_online_hours' in df.columns:
        df['typical_online_hours'] = df['typical_online_hours'].apply(json.dumps)
    return df

def main():
    faker_instance = Faker('nl_NL')
    Faker.seed(313) 
    random.seed(313) 
    
    GROUP_DATA_FOLDER = "data/groups" 
    GROUP_AMOUNT = 1000 
    MIN_PEOPLE = 10 
    MAX_PEOPLE = 35 
    
    os.makedirs(GROUP_DATA_FOLDER, exist_ok=True)
    
    people_per_group = [random.randint(MIN_PEOPLE, MAX_PEOPLE) for _ in range(GROUP_AMOUNT)]
    
    generate_dynamic_providers(faker_instance)
    
    for group_id, group_size in enumerate(people_per_group):
        people_df = generate_people(faker_instance, group_size)
        filepath = os.path.join(GROUP_DATA_FOLDER, f"group_{group_id+1}.csv")
        people_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"Generated {group_size} people and saved to {filepath}")

if __name__ == "__main__":
    main()