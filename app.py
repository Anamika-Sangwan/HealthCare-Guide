from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
import re
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

def analyze_lipid_profile(total_cholesterol, hdl_cholesterol, ldl_cholesterol, triglycerides):
    """Analyze lipid profile and provide recommendations based on medical guidelines."""
    # Calculate risk based on standard medical guidelines
    result = ""
    risk_level = "Low"
    recommendations = []
    
    # Total Cholesterol Assessment
    if total_cholesterol < 200:
        result += "Total Cholesterol: Desirable "
    elif 200 <= total_cholesterol < 240:
        result += "Total Cholesterol: Borderline high "
        risk_level = max(risk_level, "Moderate")
        recommendations.append("Consider reducing saturated fat intake")
    else:
        result += "Total Cholesterol: High "
        risk_level = "High"
        recommendations.append("Reduce saturated fat intake and consider consulting a doctor")
    
    # HDL Cholesterol Assessment (Higher is better)
    if hdl_cholesterol >= 60:
        result += "HDL Cholesterol: Optimal "
    elif 40 <= hdl_cholesterol < 60:
        result += "HDL Cholesterol: Normal "
    else:
        result += "HDL Cholesterol: Low "
        risk_level = max(risk_level, "Moderate")
        recommendations.append("Increase physical activity and consider omega-3 supplements")
    
    # LDL Cholesterol Assessment
    if ldl_cholesterol < 100:
        result += "LDL Cholesterol: Optimal "
    elif 100 <= ldl_cholesterol < 130:
        result += "LDL Cholesterol: Near optimal "
    elif 130 <= ldl_cholesterol < 160:
        result += "LDL Cholesterol: Borderline high "
        risk_level = max(risk_level, "Moderate")
        recommendations.append("Reduce consumption of trans fats and increase fiber intake")
    elif 160 <= ldl_cholesterol < 190:
        result += "LDL Cholesterol: High "
        risk_level = "High"
        recommendations.append("Reduce saturated fat intake and increase soluble fiber")
    else:
        result += "LDL Cholesterol: Very high "
        risk_level = "Very High"
        recommendations.append("Consult a doctor immediately for potential medication")
    
    # Triglycerides Assessment
    if triglycerides < 150:
        result += "Triglycerides: Normal "
    elif 150 <= triglycerides < 200:
        result += "Triglycerides: Borderline high "
        risk_level = max(risk_level, "Moderate")
        recommendations.append("Limit sugar and alcohol consumption")
    elif 200 <= triglycerides < 500:
        result += "Triglycerides: High "
        risk_level = "High"
        recommendations.append("Reduce carbohydrate intake and increase omega-3 fatty acids")
    else:
        result += "Triglycerides: Very high "
        risk_level = "Very High"
        recommendations.append("Consult a doctor immediately as this may indicate metabolic syndrome")
    
    # Add general recommendations
    if not recommendations:
        recommendations.append("Maintain a healthy diet and regular exercise")
    
    if risk_level in ["High", "Very High"]:
        recommendations.append("Schedule an appointment with a healthcare provider for a comprehensive evaluation")
    
    return result, risk_level, recommendations

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
    """Extract medical information using Gemini AI"""
    try:
        # Initialize model
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
        except Exception:
            model = genai.GenerativeModel('gemini-1.0-pro')
        
        # Structured prompt for extracting medical information
        prompt = f"""Extract the following medical information from the given text in a structured JSON format:
        1. Name (if mentioned)
        2. Age (if mentioned)
        3. Symptoms
        4. Family History
        5. Possible Diseases (based on symptoms)

        Instructions:
        - Extract only if clearly mentioned
        - Be concise
        - If no information found for a field, keep it as an empty list or null
        - Prioritize medical relevance

        Text: "{text}"

        Output Format:
        {{
            "name": "string or null",
            "age": "string or null",
            "symptoms": ["symptom1", "symptom2", ...],
            "family_history": ["condition1", "condition2", ...],
            "possible_diseases": ["disease1", "disease2", ...]
        }}
        """
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Try to parse the response as JSON
        import json
        
        # Remove any markdown code block formatting
        response_text = response.text.replace('```json', '').replace('```', '').strip()
        
        # Try parsing the JSON
        try:
            extracted_info = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback to manual parsing if JSON is malformed
            extracted_info = {
                "name": None,
                "age": None,
                "symptoms": [],
                "family_history": [],
                "possible_diseases": []
            }
            
            # Basic fallback extraction using regex
            name_match = re.search(r'my name is (\w+)', text, re.IGNORECASE)
            if name_match:
                extracted_info["name"] = name_match.group(1)
            
            age_match = re.search(r'\b(\d{1,3})[\s-]*(years?|yrs?|y\.o\.?|year old)\b', text, re.IGNORECASE)
            if age_match:
                extracted_info["age"] = re.search(r'\d+', age_match.group(0)).group(0) + " years"
        
        # Ensure lists don't contain duplicates and clean up
        if "symptoms" in extracted_info:
            extracted_info["symptoms"] = list(dict.fromkeys(extracted_info["symptoms"]))
        if "family_history" in extracted_info:
            extracted_info["family_history"] = list(dict.fromkeys(extracted_info["family_history"]))
        if "possible_diseases" in extracted_info:
            extracted_info["possible_diseases"] = list(dict.fromkeys(extracted_info["possible_diseases"]))
        
        return extracted_info
    except Exception as e:
        print(f"Error extracting medical info: {str(e)}")
        return {
            "name": None,
            "age": None,
            "symptoms": [],
            "family_history": [],
            "possible_diseases": []
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