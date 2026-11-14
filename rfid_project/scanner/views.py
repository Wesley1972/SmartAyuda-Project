from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import RFIDCard, ReliefLog
from django.shortcuts import render

LATEST_SCAN = None

@csrf_exempt
def record_scan(request):
    global LATEST_SCAN
    if request.method == 'POST':  # Check if the incoming request is a POST method (sending data)
        data = json.loads(request.body) # Decode the JSON package sent by your bridge script
        scanned_uid = data.get('uid')

        if scanned_uid:
            card, created = RFIDCard.objects.get_or_create(uid=scanned_uid) # 1. Check if the card exists in the database. If not, create it.

            if card.owner: # Check if the card is linked to a user
                owner_name = f"{card.owner.first_name} {card.owner.last_name}"
                LATEST_SCAN = {'uid': card.uid, 'is_linked': True, 'name': owner_name}
            else:
                LATEST_SCAN = {'uid': card.uid, 'is_linked': False, 'name': None}
            return JsonResponse({'status': 'success', 'message': f'Scan received: {scanned_uid}'})
    return JsonResponse({'status': 'error'}, status=400)

# The frontend dashboard will continuously call this to check for new taps
def check_scanner_status(request):
    global LATEST_SCAN
    if LATEST_SCAN:
        # Grab the data and immediately clear the variable so it doesn't loop forever
        data_to_send = LATEST_SCAN
        LATEST_SCAN = None
        return JsonResponse({'status': 'success', 'scan_data': data_to_send})
    return JsonResponse({'status': 'waiting'})

def get_logs(request):
    logs = ReliefLog.objects.all().order_by('-timestamp')[:50]
    data = [] # Format the data into a simple dictionary list
    for log in logs:
        # Check if the card has an owner; if not, mark as Unregistered
        owner_name = f"{log.card_scanned.owner.first_name} {log.card_scanned.owner.last_name}" \
            if log.card_scanned.owner \
            else "Unregistered"

        data.append({
            'uid': log.card_scanned.uid,
            'owner': owner_name,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'supplies': log.supplies_received
        })

    return JsonResponse({'logs': data})

@csrf_exempt
def link_card(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        uid = data.get('uid')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        address = data.get('address')

        # Make sure all fields were filled out
        if not all([uid, first_name, last_name, address]):
            return JsonResponse({'status': 'error', 'message': 'Missing data fields'}, status=400)

        try:
            # Find the unregistered card
            card = RFIDCard.objects.get(uid=uid)

            if card.owner:
                return JsonResponse({'status': 'error', 'message': 'Card is already linked!'}, status=400)

            # Create the new user and attach them to the card
            from .models import User  # Ensure User model is imported
            new_user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                address=address
            )
            card.owner = new_user
            card.save()

            # Also log their first relief entry since they just tapped
            ReliefLog.objects.create(card_scanned=card, supplies_received="Registration Tap")

            return JsonResponse({'status': 'success', 'message': 'User registered successfully!'})

        except RFIDCard.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Card not found in system.'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def dashboard(request):
    return render(request, 'index.html')

# Render admin_portal.html on the Django server
def dashboard(request):
    return render(request, 'admin_portal.html')

# Render edit_user.html on the Django server
def edit_user_view(request):
    return render(request, 'edit_user.html')