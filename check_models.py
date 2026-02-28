import google.generativeai as genai

# Your API key
genai.configure(api_key="AIzaSyCAm99jBO38ZiWPMl1og2pNJkQLdIfnL9o")

print("=" * 60)
print("AVAILABLE GEMINI MODELS")
print("=" * 60)

models = genai.list_models()
for model in models:
    print(f"\n📌 Model: {model.name}")
    print(f"   Methods: {model.supported_generation_methods}")