from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
from models.symptom_checker import predict_disease
from models.lipid_analyzer import analyze_lipid_profile
import google.generativeai as genai

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

if __name__ == '__main__':
    app.run(debug=True)