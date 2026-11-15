from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import RFIDCard, ReliefLog, AdminSetReliefLog
from django.shortcuts import render

LATEST_SCAN = None

def get_admin_logs(request):
    logs = AdminSetReliefLog.objects.all().order_by('timestamp')

    data = []
    for log in logs:
        data.append({
            'id': log.id,
            'location': log.location,
            'supplies': log.supplies_relief,
            'timestamp': log.timestamp.isoformat()
        })
    return JsonResponse({'logs': data})

@csrf_exempt
def save_supply(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        location = data.get('location')
        supplies = data.get('supplies')

        if not location or not supplies:
            return JsonResponse({'status': 'error', 'message': 'Missing location or supplies'}, status=400)

        log = AdminSetReliefLog.objects.create(
            location=location,
            supplies_relief=supplies
        )

        return JsonResponse({
            'status': 'success',
            'id': log.id,
            'message': 'Supplies and location saved successfully!'
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def get_user_details(request):
    # Grab the UID from the end of the web address (e.g., ?uid=1234)
    uid = request.GET.get('uid') #
    if uid:
        try:
            card = RFIDCard.objects.get(uid=uid)
            if card.owner:
                # Send their current name and address back to the webpage
                return JsonResponse({
                    'status': 'success',
                    'full_name': card.owner.full_name,
                    'address': card.owner.address
                })
        except RFIDCard.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'}, status=404)

@csrf_exempt
def update_user(request):
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        }, status=405)

    try:
        data = json.loads(request.body)

        uid = data.get('uid')
        full_name = data.get('full_name')
        address = data.get('address')

        if not all([uid, full_name, address]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields'
            }, status=400)

        card = RFIDCard.objects.get(uid=uid)

        if not card.owner:
            return JsonResponse({
                'status': 'error',
                'message': 'This card is not linked to a user'
            }, status=400)

        card.owner.full_name = full_name
        card.owner.address = address
        card.owner.save()

        return JsonResponse({
            'status': 'success',
            'message': 'User details updated successfully!'
        })

    except RFIDCard.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Card not found'
        }, status=404)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)

@csrf_exempt
def record_scan(request):
    global LATEST_SCAN
    if request.method == 'POST':  # Check if the incoming request is a POST method (sending data)
        data = json.loads(request.body) # Decode the JSON package sent by your bridge script
        scanned_uid = data.get('uid')

        if scanned_uid:
            card, created = RFIDCard.objects.get_or_create(uid=scanned_uid) # 1. Check if the card exists in the database. If not, create it.

            if card.owner: # Check if the card is linked to a user
                owner_name = card.owner.full_name
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
        owner_name = log.card_scanned.owner.full_name \
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
        full_name = data.get('full_name')
        address = data.get('address')

        # Make sure all fields were filled out
        if not all([uid, full_name, address]):
            return JsonResponse({'status': 'error', 'message': 'Missing data fields'}, status=400)

        try:
            # Find the unregistered card
            card = RFIDCard.objects.get(uid=uid)

            if card.owner:
                return JsonResponse({'status': 'error', 'message': 'Card is already linked!'}, status=400)

            # Create the new user and attach them to the card
            from .models import User  # Ensure User model is imported
            new_user = User.objects.create(
                full_name=full_name,
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

def user_portal_view(request):
    return render(request, 'user_portal.html')

def save_user_view(request):
    return render(request, 'save_user.html')



