from groq import Groq

# Obtenez votre clé API gratuite sur https://console.groq.com/keys
# Créez un compte gratuit et générez une clé API.

API_KEY = "API_KEY"  # Remplacez par votre clé

# Initialisez le client
client = Groq(api_key=API_KEY)

def poser_question(question):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Répondez de manière concise et directe, sans phrase seulement la réponse, si tu dois compléter la réponse donne seulement la réponse, évite toute les ponctuations, toutes les réponses doivent être en français et ecrit tout les chiffres en digit"
            },
            {
                "role": "user",
                "content": question,
            }
        ],
        model="openai/gpt-oss-120b",
        max_tokens=500,
    )
    return chat_completion.choices[0].message.content.strip()  # Supprime les espaces inutiles

if __name__ == "__main__":
    print(poser_question(input("Question: ")))