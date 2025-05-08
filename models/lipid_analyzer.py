# models/lipid_analyzer.py
def analyze_lipid_profile(total_cholesterol, hdl, ldl, triglycerides):
    """
    Analyze lipid profile values and provide risk assessment
    Based on standard medical guidelines
    """
    # Risk classification based on values
    risk_level = "Low Risk"
    result = "Your lipid profile is within normal ranges."
    recommendations = []
    
    # Total Cholesterol analysis
    if total_cholesterol < 200:
        total_status = "Optimal"
    elif 200 <= total_cholesterol < 240:
        total_status = "Borderline High"
        risk_level = max(risk_level, "Moderate Risk")
        recommendations.append("Consider dietary changes to reduce total cholesterol.")
    else:  # >= 240
        total_status = "High"
        risk_level = "High Risk"
        recommendations.append("Consult with a healthcare provider about your high total cholesterol.")
    
    # HDL (Good) Cholesterol analysis
    if hdl >= 60:
        hdl_status = "Optimal (Protective)"
    elif 40 <= hdl < 60:
        hdl_status = "Normal"
    else:  # < 40
        hdl_status = "Low"
        risk_level = max(risk_level, "Moderate Risk")
        recommendations.append("Work on increasing your HDL through exercise and diet.")
    
    # LDL (Bad) Cholesterol analysis
    if ldl < 100:
        ldl_status = "Optimal"
    elif 100 <= ldl < 130:
        ldl_status = "Near Optimal"
    elif 130 <= ldl < 160:
        ldl_status = "Borderline High"
        risk_level = max(risk_level, "Moderate Risk")
        recommendations.append("Consider dietary changes to reduce LDL cholesterol.")
    elif 160 <= ldl < 190:
        ldl_status = "High"
        risk_level = "High Risk"
        recommendations.append("Consult with a healthcare provider about your high LDL cholesterol.")
    else:  # >= 190
        ldl_status = "Very High"
        risk_level = "Very High Risk"
        recommendations.append("Urgent: Consult with a healthcare provider about your very high LDL cholesterol.")
    
    # Triglycerides analysis
    if triglycerides < 150:
        trig_status = "Normal"
    elif 150 <= triglycerides < 200:
        trig_status = "Borderline High"
        risk_level = max(risk_level, "Moderate Risk")
        recommendations.append("Consider dietary changes to reduce triglycerides.")
    elif 200 <= triglycerides < 500:
        trig_status = "High"
        risk_level = "High Risk"
        recommendations.append("Consult with a healthcare provider about your high triglycerides.")
    else:  # >= 500
        trig_status = "Very High"
        risk_level = "Very High Risk"
        recommendations.append("Urgent: Consult with a healthcare provider about your very high triglycerides.")
    
    # If no specific recommendations were added, provide general advice
    if not recommendations and risk_level == "Low Risk":
        recommendations = [
            "Continue maintaining a healthy lifestyle with balanced diet and regular exercise.",
            "Get your lipid profile checked annually."
        ]
    elif not recommendations:
        recommendations = [
            "Increase physical activity.",
            "Follow a heart-healthy diet low in saturated fats.",
            "Consider discussing medication options with your doctor."
        ]
    
    # Compile detailed result
    detailed_result = f"""
    Analysis Results:
    - Total Cholesterol: {total_cholesterol} mg/dL ({total_status})
    - HDL Cholesterol: {hdl} mg/dL ({hdl_status})
    - LDL Cholesterol: {ldl} mg/dL ({ldl_status})
    - Triglycerides: {triglycerides} mg/dL ({trig_status})
    
    Overall Risk Assessment: {risk_level}
    """
    
    return detailed_result, risk_level, recommendations