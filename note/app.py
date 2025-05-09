from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def extract_medical_info(text):
    """Extract medical information using simple pattern matching"""
    try:
        # Initialize extracted information structure
        extracted_info = {
            "name": None,
            "age": None,
            "symptoms": [],
            "family_history": []
        }
        
        # Extract age using regex pattern
        age_pattern = r'\b(\d+)[\s-]*(years?|yrs?|y\.o\.?|year old)\b'
        age_match = re.search(age_pattern, text, re.IGNORECASE)
        if age_match:
            extracted_info["age"] = age_match.group(1) + " years"
        
        # Common symptoms to look for (a small dictionary of common symptoms)
        common_symptoms = [
            "fever", "headache", "pain", "cough", "cold", "nausea", 
            "vomiting", "dizziness", "fatigue", "tired", "sore throat",
            "cannot sleep", "insomnia", "ache", "hurt", "rash"
        ]
        
        # Look for symptoms
        for symptom in common_symptoms:
            if symptom in text.lower():
                extracted_info["symptoms"].append(symptom)
        
        # Look for family history
        if "family" in text.lower() and "history" in text.lower():
            family_history_pattern = r'family history.{1,50}'
            family_match = re.search(family_history_pattern, text, re.IGNORECASE)
            if family_match:
                extracted_info["family_history"].append(family_match.group(0))
        
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