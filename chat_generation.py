import pandas as pd
import ollama
import os

MODEL = 'gemma3:4b'
GROUP_FOLDER = "data/groups"

def bio_agent(name, sex, age, job, country_of_origin, socio_economic_status, household_composition,
              political_orientation, education_level, religion, marital_status, employment_status,
              housing_type, technology_proficiency, income, health, social_interaction, dutch_reading_and_writing_skills):
    """
    Genereert een biografie voor een persoon met behulp van de opgegeven attributen.
    """
    if sex == 'M':
        gender = 'Man'
    elif sex == 'F':
        gender = 'Vrouw'
    else:
        gender = 'Non-binair'
        
    bio = (f"Je bent een AI-model dat zich volledig inleeft in de rol van {name}, een {age}-jarige {gender} uit {country_of_origin}. "
           f"Je persoonlijkheid, meningen en overtuigingen zijn volledig afgestemd op iemand met de volgende eigenschappen: "
           f"Je werkt als {job} en hebt een {socio_economic_status} sociaal-economische status. "
           f"Je gezinssamenstelling is {household_composition}. Politiek gezien ben je {political_orientation} en je opleidingsniveau is {education_level}. "
           f"Je bent {religion}, {marital_status}, en je werkstatus is {employment_status}. "
           f"Je woont in een {housing_type} en je niveau van technologische vaardigheid is {technology_proficiency}. "
           f"Je inkomen is {income}, je gezondheid is {health}, je sociale interactie is {social_interaction}, "
           f"en je Nederlandse lees- en schrijfvaardigheden zijn {dutch_reading_and_writing_skills}. "
           f"Je antwoorden kunnen soms meningen bevatten die niet volledig kloppen of gebaseerd zijn op onvolledige kennis. "
           f"Je kunt dingen zeggen die voortkomen uit emoties in plaats van logica, en je denkt soms dingen te begrijpen die je niet volledig begrijpt. "
           f"Bij het beantwoorden van vragen moet je redeneren, schrijven en reageren zoals iemand met deze achtergrond en eigenschappen zou doen, "
           f"met alle nuances en onvolkomenheden die daarbij horen."
           f"Je chat als een normaal persoon, je schrijft dingen alsof je een Whatsapp-bericht schrijft, soms met spelfouten en grammaticale fouten."
           f"Soms gebruik je kleine zinnen, soms lange zinnen, soms gebruik je maar 1 woord en soms leg je je mening helemaal uit. ")
    return bio

def question_person(bio, question):
    """
    Stelt een vraag aan een persoon met behulp van hun biografie als systeemprompt.
    """
    response = ollama.generate(model=MODEL, system=bio, prompt=question)
    return response['response']

# Voorbeeldgebruik
person_bio = bio_agent(
    name="Jan", sex="M", age=35, job="KFC-medewerker", country_of_origin="Nederland",
    socio_economic_status="gemiddeld", household_composition="alleenstaand",
    political_orientation="progressief", education_level="VMBO",
    religion="agnostisch", marital_status="single", employment_status="voltijd",
    housing_type="appartement", technology_proficiency="gemiddeld",
    income="modaal", health="goed", social_interaction="gemiddeld",
    dutch_reading_and_writing_skills="goed"
)

question = "hey"
            
answer = question_person(person_bio, question)
print(answer)