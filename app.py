from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
from models.symptom_checker import predict_disease
from models.lipid_analyzer import analyze_lipid_profile
import google.generativeai as genai
import re

# Configure API Key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "AIzaSyBdVIKupl8M2pIun55RE-ZhOKcqG_1k-Ko"))

app = Flask(__name__)

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
    
    # Define system prompt (the behavior of the chatbot)
    system_prompt = (
        "You are a helpful, friendly health assistant chatbot who gives assurance and strength to users. "
        "You provide general health information and advice, such as tips for managing common symptoms, improving wellness, maintaining a healthy lifestyle, and addressing mental health concerns. You can prescribe basic medicines. "
        "If a user asks for medical advice or symptoms that may require professional diagnosis, always recommend they consult a healthcare provider. "
        "Be empathetic, clear, and concise in your responses."
        "\n\nIMPORTANT FORMATTING INSTRUCTIONS: Format your responses using structured HTML. Use:"
        "\n- <p> tags for paragraphs"
        "\n- <b> or <strong> tags for emphasis"
        "\n- <ul> and <li> tags for lists of items"
        "\n- <h4> tags for small headings within your response"
        "\nWhen listing multiple items like symptoms or tips, ALWAYS use <ul> and <li> tags."
    )
    
    try:
        # Create a model instance - use a more reliable model or fallback to a less resource-intensive one
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
        except Exception:
            # If the 1.5 model has quota issues, fallback to 1.0
            model = genai.GenerativeModel('gemini-1.0-pro')
        
        # Combine prompts to reduce API calls
        combined_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nPlease format your response with proper HTML."
        
        # Generate content directly
        response = model.generate_content(combined_prompt)
        
        # Get the response text
        chatbot_reply = response.text
        
        # Process the response to ensure it contains HTML formatting
        # First, check if the model wrapped the response in code blocks
        import re
        chatbot_reply = re.sub(r'```html|```', '', chatbot_reply)
        
        # If there are no HTML tags, add basic formatting
        if '<p>' not in chatbot_reply and '<li>' not in chatbot_reply:
            # Split into paragraphs
            paragraphs = chatbot_reply.split('\n\n')
            formatted_reply = ""
            
            for para in paragraphs:
                if not para.strip():
                    continue
                    
                # Check if this paragraph is a list (starts with * or -)
                if re.search(r'^\s*[\*\-]', para, re.MULTILINE):
                    # Convert to HTML list
                    items = re.split(r'\s*[\*\-]\s+', para)
                    formatted_reply += '<ul>'
                    for item in items:
                        if item.strip():
                            formatted_reply += f'<li>{item.strip()}</li>'
                    formatted_reply += '</ul>'
                else:
                    # Regular paragraph
                    formatted_reply += f'<p>{para}</p>'
            
            chatbot_reply = formatted_reply if formatted_reply else f'<p>{chatbot_reply}</p>'
        
        # Format keywords like "Rest", "Hydration" with bold
        keywords = ['Rest', 'Hydration', 'Diet', 'Exercise', 'Sleep', 'Water', 'Medication']
        for keyword in keywords:
            chatbot_reply = re.sub(fr'\b{keyword}\b', f'<b>{keyword}</b>', chatbot_reply)
            
        return jsonify({'response': chatbot_reply, 'isHtml': True})
    except Exception as e:
        error_msg = str(e)
        # Give a more user-friendly error for quota issues
        if "429" in error_msg or "quota" in error_msg.lower():
            return jsonify({
                'response': '<p>I\'m currently experiencing high demand. Please try again in a few minutes.</p>',
                'isHtml': True
            })
        return jsonify({
            'response': f"<p>Sorry, I couldn't process that right now. Please try again later.</p>",
            'isHtml': True
        })
    
@app.route('/note')
def index():
    return render_template('note.html')

def extract_medical_info(text):
    """Extract medical information using improved pattern matching"""
    try:
        # Initialize extracted information structure
        extracted_info = {
            "name": None,
            "age": None,
            "symptoms": [],
            "family_history": []
        }
        
        # Try to extract name (this is a simple implementation, might need refinement)
        name_patterns = [
            r'my name is (\w+)',
            r'i\'m (\w+)',
            r'call me (\w+)'
        ]
        for pattern in name_patterns:
            name_match = re.search(pattern, text, re.IGNORECASE)
            if name_match:
                extracted_info["name"] = name_match.group(1)
                break
        
        # Extract age using more flexible regex pattern
        age_patterns = [
            r'\b(\d{1,3})[\s-]*(years?|yrs?|y\.o\.?|year old)\b',
            r'\b(I am|I\'m)\s+(\d{1,3})\s*(years? old)\b'
        ]
        for pattern in age_patterns:
            age_match = re.search(pattern, text, re.IGNORECASE)
            if age_match:
                # Extract the numeric part
                extracted_info["age"] = re.search(r'\d+', age_match.group(0)).group(0) + " years"
                break
        
        # Expanded list of common symptoms
        common_symptoms = [
            "fever", "headache", "pain", "cough", "cold", "nausea", 
            "vomiting", "dizziness", "fatigue", "tired", "sore throat",
            "cannot sleep", "insomnia", "ache", "hurt", "rash", 
            "chest pain", "stomach ache", "migraine", "allergies", 
            "breathing difficulty", "congestion"
        ]
        
        # Look for symptoms (more robust matching)
        for symptom in common_symptoms:
            # Use word boundaries to prevent partial word matches
            symptom_pattern = fr'\b{re.escape(symptom)}\b'
            if re.search(symptom_pattern, text, re.IGNORECASE):
                # Avoid duplicate symptoms
                if symptom not in extracted_info["symptoms"]:
                    extracted_info["symptoms"].append(symptom)
        
        # Look for family history with more context
        family_history_patterns = [
            r'family history of (\w+)',
            r'my (mother|father|brother|sister|grandfather|grandmother) had',
            r'family medical history'
        ]
        for pattern in family_history_patterns:
            family_match = re.findall(pattern, text, re.IGNORECASE)
            if family_match:
                extracted_info["family_history"].extend(family_match)
        
        # Remove duplicates from lists
        extracted_info["symptoms"] = list(dict.fromkeys(extracted_info["symptoms"]))
        extracted_info["family_history"] = list(dict.fromkeys(extracted_info["family_history"]))
        
        return extracted_info
    except Exception as e:
        print(f"Error extracting medical info: {str(e)}")
        return {
            "name": None,
            "age": None,
            "symptoms": [],
            "family_history": []
        }

def get_all_notes():
    """Read all notes from the file"""
    try:
        with open('notes.txt', 'r') as f:
            content = f.read()
            notes = content.split('---\n')
            return [note.strip() for note in notes if note.strip()]
    except FileNotFoundError:
        return []

@app.route('/get_notes', methods=['GET'])
def fetch_notes():
    notes = get_all_notes()
    processed_notes = []
    
    for note in notes:
        summary = extract_medical_info(note)
        processed_notes.append({
            "original": note,
            "summary": summary
        })
    
    return jsonify(processed_notes)

@app.route('/save_note', methods=['POST'])
def save_note():
    data = request.get_json()
    note = data['note']
    
    with open('notes.txt', 'a') as f:
        f.write(note + '\n---\n')  # separates notes with dashes
    
    # Process the note for medical information
    summary = extract_medical_info(note)
    
    return jsonify({
        'status': 'success',
        'original': note,
        'summary': summary
    })

if __name__ == '__main__':
    app.run(debug=True)