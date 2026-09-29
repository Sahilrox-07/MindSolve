from services.gemini_service import generate_ai_response

response = generate_ai_response(
    problem="I cannot focus while studying."
)

if response:
    print("Gemini response:\n")
    print(response)

else:
    print("Gemini did not return a response.")