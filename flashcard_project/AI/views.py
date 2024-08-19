import os
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decouple import config
import google.generativeai as genai
from .models import ChatHistory, Message
from .forms import ChatHistoryForm, MessageForm

genai.configure(api_key=config('API_KEY'))

@csrf_exempt
def generate_content_view(request, agent_name):
   
    agent = get_object_or_404(Agent, name__iexact=agent_name, creator=request.user)

    if ChatHistory.objects.filter(agent=agent).exists():
        chat_history = get_object_or_404(ChatHistory, agent=agent)
        chat_history_messages = chat_history.messages.all()
        history = []
        for message in chat_history_messages:
            history.append(
                {"role": "user", 
                "parts": f"{message.user_message}"}
                )
            history.append(
                {"role": "model",
                "parts": f"{message.bot_message}"}
            )
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=agent.instructions)
        chat = model.start_chat(history=history)
    else:
        chat_history_title = f"{request.user}_{agent_name}_history"
        chat_history = ChatHistory.objects.create(agent=agent, title=chat_history_title)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=agent.instructions)
        chat = model.start_chat()

    directory_path = f"media/uploads/agents/{agent.id}/"
    
    files = os.listdir(directory_path)
    
    if not files:
        return JsonResponse({"error": "No files found in the directory"}, status=400)
    
    file_path = os.path.join(directory_path, files[0])
    
    knowledge_base_file = genai.upload_file(path=file_path, display_name=f"Agent '{agent.name}' Knowledge Base PDF") 

    if request.method == "POST":
        user_message = request.POST.get('message')
        if not user_message:
            return JsonResponse({"error": "No message provided"}, status=400)

        modified_user_message = f"Using this knowledge base in the file, respond to the user message: {user_message}"

        contents = [knowledge_base_file, modified_user_message]
        response = chat.send_message(contents, stream=False)
        chatbot_response = response.text

        # Update chat history
        Message.objects.create(
            history=chat_history,
            user_message=modified_user_message,
            bot_message=chatbot_response
        )

        return JsonResponse({"response": chatbot_response})

    return JsonResponse({'error': 'Invalid request method'}, status=405)
