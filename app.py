# Health Companion Flask Application
# Directory Structure:
# - app.py (main Flask application)
# - models/ (ML models)
#   - symptom_checker.py
#   - lipid_analyzer.py 
# - static/ (CSS, JS, images)
# - templates/ (HTML templates)
# - requirements.txt

from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
from models.symptom_checker import predict_disease
from models.lipid_analyzer import analyze_lipid_profile

app = Flask(__name__)

# Load ML models

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/symptom_checker')
def symptom_checker():
    # List of symptoms for checkboxes
    symptoms = [
        'Fever', 'Cough', 'Fatigue', 'Difficulty Breathing', 'Headache',
        'Sore Throat', 'Body Aches', 'Runny Nose', 'Nausea', 'Diarrhea',
        'Chest Pain', 'Abdominal Pain', 'Dizziness', 'Rash', 'Loss of Taste/Smell',
        'Joint Pain', 'Swelling', 'Chills', 'Vomiting', 'Confusion'
    ]
    return render_template('symptom_checker.html', symptoms=symptoms)

@app.route('/predict_disease', methods=['POST'])
def predict_disease_route():
    if request.method == 'POST':
        selected_symptoms = request.form.getlist('symptoms')
        
        # Get prediction from model
        prediction, confidence = predict_disease(selected_symptoms)
        
        return render_template('prediction_result.html', 
                              prediction=prediction, 
                              confidence=confidence,
                              symptoms=selected_symptoms)

@app.route('/lipid_profile')
def lipid_profile():
    return render_template('lipid_profile.html')

@app.route('/analyze_lipid', methods=['POST'])
def analyze_lipid():
    if request.method == 'POST':
        total_cholesterol = float(request.form.get('total_cholesterol', 0))
        hdl_cholesterol = float(request.form.get('hdl_cholesterol', 0))
        ldl_cholesterol = float(request.form.get('ldl_cholesterol', 0))
        triglycerides = float(request.form.get('triglycerides', 0))
        
        # Get analysis from model
        result, risk_level, recommendations = analyze_lipid_profile(
            total_cholesterol, hdl_cholesterol, ldl_cholesterol, triglycerides
        )
        
        return render_template('lipid_result.html',
                              result=result,
                              risk_level=risk_level,
                              recommendations=recommendations,
                              total_cholesterol=total_cholesterol,
                              hdl_cholesterol=hdl_cholesterol,
                              ldl_cholesterol=ldl_cholesterol,
                              triglycerides=triglycerides)

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/get_chatbot_response', methods=['POST'])
def get_chatbot_response():
    user_message = request.form.get('user_message', '')
    
    # Simple rule-based responses for demonstration
    responses = {
        'fever': 'If you have a fever, rest and drink plenty of fluids. If it\'s high or persists, seek medical attention.',
        'headache': 'For headaches, ensure you\'re hydrated and try over-the-counter pain relievers. If severe or persistent, consult a doctor.',
        'cough': 'For a cough, stay hydrated and use honey (if not allergic). See a doctor if it persists more than a week.',
        'diet': 'A balanced diet includes a variety of fruits, vegetables, whole grains, lean proteins, and healthy fats.',
        'exercise': 'Aim for at least 150 minutes of moderate aerobic activity or 75 minutes of vigorous aerobic activity weekly.',
        'sleep': 'Getting 7-9 hours of quality sleep per night supports physical and mental health.',
        'cholesterol': 'Maintain healthy cholesterol with diet, exercise, and sometimes medication. Regular testing is important.',
        'blood pressure': 'Keep blood pressure healthy with diet, exercise, limited salt intake, and stress management.',
        'diabetes': 'Manage diabetes through diet, exercise, medication as prescribed, and regular monitoring.',
        'stress': 'Manage stress through exercise, mindfulness, adequate sleep, and seeking support when needed.'
    }
    
    # Default response
    response = "I'm your health assistant. How can I help you today? You can ask me about symptoms, diet, exercise, sleep, or common health conditions."
    
    # Check if any keywords match
    for keyword, resp in responses.items():
        if keyword in user_message.lower():
            response = resp
            break
            
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)