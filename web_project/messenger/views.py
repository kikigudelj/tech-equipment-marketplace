from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Message
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from myapp.forms import MessageForm, MessageForm2
from myapp.models import Product, Notification

def messenger(request):
    user = request.user
    my_conversations = Message.get_all_conversations(user)
    my_user = my_conversations.first()
    return HttpResponseRedirect(reverse('messenger:messages_from_conversations', args=[my_user.id]))



@login_required
def messages_from_conversations(request, user_id=None):
    user = request.user
    my_conversations = Message.get_all_conversations(user)

    notification_id = request.GET.get('notification_id')
    if notification_id:
        notifications = Notification.objects.filter(id=notification_id, receiver=user, is_read=False)
        notifications.update(is_read=True)

    if not my_conversations:
        other_user = None
        all_messages = None
    else:
        if user_id:
            other_user = get_object_or_404(User, pk=user_id)
        else:
            other_user = my_conversations.first().user
        if other_user:
            all_messages = Message.get_all_messages(user, other_user)
        else:
            all_messages = None

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.m_sender = request.user
            message.m_receiver = other_user  
            message.save()
            notification = Notification(
                receiver=other_user,
                sender=request.user,
                message=f"Primili ste novu poruku od {request.user.username}: {message.text}",
                type=1,
                transaction = None
            )
            notification.save()
            print(f"Poruka poslana korisniku {other_user}: {message.text}")
    else:
        form = MessageForm()

    context = {
        'my_conversations': my_conversations,
        'other_user': other_user,
        'all_messages': all_messages,
        'form': form,
        'no_conversations': not my_conversations
    }

    return render(request, 'messenger/messenger.html', context)

@login_required
def send_message_from_profile(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = MessageForm2(request.POST, receiver=receiver)  
        if form.is_valid():
            message = form.save(commit=False)
            message.m_sender = request.user
            message.m_receiver = receiver  
            message.save()

            notification = Notification(
                receiver=receiver,
                sender=request.user,
                message=f"Primili ste novu poruku od {request.user.username}: {message.text}",
                type=1,
                transaction = None
            )
            notification.save()
            print(f"Poruka poslana korisniku {receiver}: {message.text}")

            return redirect('messenger:messages_from_conversations', user_id=user_id)
        else:
            print("Greške u formi:", form.errors)

    return redirect('seller_profile', user_id=user_id)