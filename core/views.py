from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, NoteForm
from .models import Note
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Message

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    notes = Note.objects.filter(user=request.user)
    total_notes = notes.count()
    completed_tasks = Note.objects.filter(user=request.user, is_completed=True).count()
    active_tasks = Note.objects.filter(user=request.user, is_completed=False).count()
    
    context = {
        'total': total_notes,
        'done': completed_tasks,
        'left': active_tasks,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {'u_form': u_form, 'p_form': p_form}
    return render(request, 'core/profile.html', context)

@login_required
def notes_view(request):
    status_filter = request.GET.get('filter', 'all')
    notes = Note.objects.filter(user=request.user).order_by('-created_at')
    
    if status_filter == 'active':
        notes = notes.filter(done=False)
    elif status_filter == 'completed':
        notes = notes.filter(done=True)
        
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            return redirect('notes')
    else:
        form = NoteForm()
        
    context = {
        'notes': notes,
        'form': form,
        'current_filter': status_filter
    }
    return render(request, 'core/notes.html', context)

@login_required
def notes(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if title:
            Note.objects.create(
                user=request.user,
                title=title,
                description=description
            )
            return redirect('notes')

    current_filter = request.GET.get('filter', 'all')
    if current_filter == 'active':
        notes_list = Note.objects.filter(user=request.user, is_completed=False)
    elif current_filter == 'completed':
        notes_list = Note.objects.filter(user=request.user, is_completed=True)
    else:
        notes_list = Note.objects.filter(user=request.user)

    context = {
        'notes': notes_list,
        'current_filter': current_filter,
    }
    return render(request, 'core/notes.html', context)

@login_required
def toggle_note(request, note_id):
    if request.method == 'POST':
        note = get_object_or_404(Note, id=note_id, user=request.user)
        note.is_completed = not note.is_completed
        note.save()
    return redirect('notes')

@login_required
def delete_note(request, note_id):
    if request.method == 'POST':
        note = get_object_or_404(Note, id=note_id, user=request.user)
        note.delete()
    return redirect('notes')

@login_required
def user_list_view(request):
    users = User.objects.exclude(pk=request.user.pk)
    return render(request, 'core/user_list.html', {'users': users})


@login_required
def chat_view(request, user_id):
    if user_id == request.user.pk:
        return redirect('user_list')
        
    other_user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                text=text
            )
            return redirect('chat', user_id=user_id)
            
    chat_messages = Message.objects.filter(
        Q(sender=request.user, recipient=other_user)
        | Q(sender=other_user, recipient=request.user)
    )
    
    chat_messages.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'core/chat.html', {
        'other_user': other_user,
        'chat_messages': chat_messages
    })


@login_required
def inbox_view(request):
    sent_to = Message.objects.filter(sender=request.user).values_list('recipient', flat=True)
    received_from = Message.objects.filter(recipient=request.user).values_list('sender', flat=True)
    partner_ids = set(sent_to) | set(received_from)

    partners = User.objects.filter(pk__in=partner_ids)
    dialogs = []
    
    for partner in partners:
        last_msg = Message.objects.filter(
            Q(sender=request.user, recipient=partner) |
            Q(sender=partner, recipient=request.user)
        ).last()
        
        unread_count = Message.objects.filter(sender=partner, recipient=request.user, is_read=False).count()
        
        dialogs.append({
            'partner': partner,
            'last_message': last_msg,
            'unread_count': unread_count
        })
     
    dialogs.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else None, reverse=True)
    
    return render(request, 'core/inbox.html', {'dialogs': dialogs})