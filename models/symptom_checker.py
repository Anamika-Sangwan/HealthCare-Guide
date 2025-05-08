# models/symptom_checker.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


# Dictionary mapping symptoms to diseases (simplified for demo)
symptom_disease_map = {
    'Fever': ['Common Cold', 'Flu', 'COVID-19', 'Malaria'],
    'Cough': ['Common Cold', 'Flu', 'COVID-19', 'Bronchitis'],
    'Fatigue': ['Common Cold', 'Flu', 'COVID-19', 'Anemia', 'Depression'],
    'Difficulty Breathing': ['Asthma', 'COVID-19', 'Pneumonia', 'Anxiety'],
    'Headache': ['Migraine', 'Tension Headache', 'Sinusitis', 'Flu'],
    'Sore Throat': ['Common Cold', 'Flu', 'Strep Throat'],
    'Body Aches': ['Flu', 'COVID-19', 'Fibromyalgia'],
    'Runny Nose': ['Common Cold', 'Flu', 'Allergies'],
    'Nausea': ['Food Poisoning', 'Migraine', 'Gastritis', 'Pregnancy'],
    'Diarrhea': ['Food Poisoning', 'Gastroenteritis', 'IBS'],
    'Chest Pain': ['Heart Attack', 'Angina', 'Acid Reflux', 'Anxiety'],
    'Abdominal Pain': ['Appendicitis', 'Gallstones', 'IBS', 'Food Poisoning'],
    'Dizziness': ['Vertigo', 'Anemia', 'Low Blood Pressure', 'Anxiety'],
    'Rash': ['Allergic Reaction', 'Eczema', 'Psoriasis', 'Chickenpox'],
    'Loss of Taste/Smell': ['COVID-19', 'Common Cold', 'Sinusitis'],
    'Joint Pain': ['Arthritis', 'Gout', 'Lupus', 'Lyme Disease'],
    'Swelling': ['Edema', 'Allergic Reaction', 'Injury', 'Infection'],
    'Chills': ['Flu', 'COVID-19', 'Malaria', 'Infection'],
    'Vomiting': ['Food Poisoning', 'Gastroenteritis', 'Migraine', 'Pregnancy'],
    'Confusion': ['Concussion', 'Stroke', 'Infection', 'Low Blood Sugar']
}

# Common symptom combinations for specific diseases
disease_profiles = {
    'Common Cold': ['Fever', 'Cough', 'Runny Nose', 'Sore Throat'],
    'Flu': ['Fever', 'Cough', 'Body Aches', 'Fatigue', 'Headache', 'Chills'],
    'COVID-19': ['Fever', 'Cough', 'Fatigue', 'Difficulty Breathing', 'Loss of Taste/Smell'],
    'Migraine': ['Headache', 'Nausea', 'Sensitivity to Light', 'Vomiting'],
    'Food Poisoning': ['Nausea', 'Vomiting', 'Diarrhea', 'Abdominal Pain'],
    'Allergic Reaction': ['Rash', 'Swelling', 'Difficulty Breathing', 'Runny Nose'],
    'Anxiety': ['Chest Pain', 'Difficulty Breathing', 'Dizziness', 'Confusion'],
    'Gastroenteritis': ['Nausea', 'Vomiting', 'Diarrhea', 'Abdominal Pain', 'Fever']
}

def predict_disease(symptoms):
    """
    Simple algorithm to predict disease based on symptoms
    In a real application, this would use a trained ML model
    """
    if not symptoms:
        return "No symptoms selected", 0
    
    # Count occurrence of each disease in the symptoms
    disease_counts = {}
    for symptom in symptoms:
        if symptom in symptom_disease_map:
            for disease in symptom_disease_map[symptom]:
                if disease in disease_counts:
                    disease_counts[disease] += 1
                else:
                    disease_counts[disease] = 1
    
    # Find diseases with highest symptom match
    if not disease_counts:
        return "Unknown condition", 0
    
    # Sort by count
    sorted_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)
    top_disease = sorted_diseases[0][0]
    
    # Calculate confidence based on symptom match percentage
    # Compare with ideal symptom profile when available
    if top_disease in disease_profiles:
        ideal_symptoms = disease_profiles[top_disease]
        matched = len(set(symptoms).intersection(set(ideal_symptoms)))
        confidence = min(100, int((matched / len(ideal_symptoms)) * 100))
    else:
        # Simple confidence based on number of symptoms matching
        confidence = min(90, sorted_diseases[0][1] * 15)
    
    # Add disclaimer
    disclaimer = "This is not a medical diagnosis. Please consult a healthcare professional."
    
    return top_disease, confidence

