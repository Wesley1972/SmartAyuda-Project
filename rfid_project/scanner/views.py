from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
from django.utils import timezone
from .models import User, RFIDCard, AdminSetReliefLog, AidClaim
from django.http import HttpResponse

LATEST_SCAN = None

def get_valid_owner(card):
    if not card.owner_id:
        return None
    try:
        return card.owner
    except User.DoesNotExist:
        card.owner = None
        card.save()
        return None

@csrf_exempt
def assign_supply(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        uid = data.get('uid')

        if not uid:
            return JsonResponse({'status': 'error', 'message': 'Missing card UID.'}, status=400)

        try:
            card = RFIDCard.objects.get(uid=uid)
            owner = get_valid_owner(card)
            if not owner:
                return JsonResponse({'status': 'error', 'message': 'Card not linked to a user.'}, status=400)

            # Grab the most recent supply record and link the user to it
            latest_supply = AdminSetReliefLog.objects.order_by('-timestamp').first()
            if not latest_supply:
                return JsonResponse({'status': 'error', 'message': 'No saved supplies found.'}, status=400)

            latest_supply.users.add(owner)
            AidClaim.objects.get_or_create(relief_log=latest_supply, user=owner)
            return JsonResponse({
                'status': 'success',
                'log_id': latest_supply.id,
                'recipient_count': latest_supply.users.count(),
                'message': 'Supply linked to user successfully!'
            })

        except RFIDCard.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Card not found in database.'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def get_admin_logs(request):
    logs = AdminSetReliefLog.objects.all().order_by('timestamp')

    data = []
    for log in logs:
        data.append({
            'id': log.id,
            'location': log.location,
            'supplies': log.supplies_relief,
            'timestamp': log.timestamp.isoformat(),
            'recipient_count': log.users.count()
        })
    return JsonResponse({'logs': data})

@csrf_exempt
def save_supply(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        log_id = data.get('id')
        location = data.get('location')
        supplies = data.get('supplies')

        if not location or not supplies:
            return JsonResponse({'status': 'error', 'message': 'Missing location or supplies'}, status=400)

        if log_id:
            log = AdminSetReliefLog.objects.get(id=log_id)
            log.location = location
            log.supplies_relief = supplies
            log.timestamp = timezone.now()
            log.save()
        else:
            log = AdminSetReliefLog.objects.create(
                location=location,
                supplies_relief=supplies
            )

        return JsonResponse({
            'status': 'success',
            'id': log.id,
            'recipient_count': log.users.count(),
            'message': 'Supplies and location saved successfully!'
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def get_user_details(request):
    uid = request.GET.get('uid')
    if uid:
        try:
            card = RFIDCard.objects.get(uid=uid)
            owner = get_valid_owner(card)
            if owner:
                return JsonResponse({
                    'status': 'success',
                    'full_name': owner.full_name,
                    'address': owner.address,
                    'role': owner.role
                })
        except RFIDCard.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'}, status=404)

@csrf_exempt
def update_user(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        uid = data.get('uid')
        full_name = data.get('full_name')
        address = data.get('address')
        role = data.get('role', 'user')

        if not all([uid, full_name, address]):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

        card = RFIDCard.objects.get(uid=uid)

        owner = get_valid_owner(card)
        if not owner:
            return JsonResponse({'status': 'error', 'message': 'This card is not linked to a user'}, status=400)

        owner.full_name = full_name
        owner.address = address
        owner.role = role
        owner.save()

        return JsonResponse({'status': 'success', 'message': 'User details updated successfully!'})

    except RFIDCard.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Card not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

@csrf_exempt
def record_scan(request):
    global LATEST_SCAN
    if request.method == 'POST':
        data = json.loads(request.body)
        scanned_uid = data.get('uid')

        if scanned_uid:
            card, created = RFIDCard.objects.get_or_create(uid=scanned_uid)

            if card.owner:
                owner = get_valid_owner(card)
                if owner:
                    LATEST_SCAN = {'uid': card.uid, 'is_linked': True, 'name': owner.full_name, 'role': owner.role}
            else:
                LATEST_SCAN = {'uid': card.uid, 'is_linked': False, 'name': None}
            return JsonResponse({'status': 'success', 'message': f'Scan received: {scanned_uid}'})
    return JsonResponse({'status': 'error'}, status=400)

def api_ping(request):
    return HttpResponse("ok", content_type="text/plain")

def check_scanner_status(request):
    global LATEST_SCAN
    if LATEST_SCAN:
        data_to_send = LATEST_SCAN
        LATEST_SCAN = None
        return JsonResponse({'status': 'success', 'scan_data': data_to_send})
    return JsonResponse({'status': 'waiting'})

def get_logs(request):
    logs = AdminSetReliefLog.objects.all().order_by('-timestamp')[:50]
    data = []
    for log in logs:
        for user in log.users.all():
            data.append({
                'owner': user.full_name,
                'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'supplies': log.supplies_relief,
                'location': log.location
            })
    return JsonResponse({'logs': data})

@csrf_exempt
def link_card(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        uid = data.get('uid')
        full_name = data.get('full_name')
        address = data.get('address')

        if not all([uid, full_name, address]):
            return JsonResponse({'status': 'error', 'message': 'Missing data fields'}, status=400)

        try:
            card = RFIDCard.objects.get(uid=uid)

            owner = get_valid_owner(card)
            if owner:
                return JsonResponse({'status': 'error', 'message': 'Card is already linked!'}, status=400)

            new_user = User.objects.create(
                full_name=full_name,
                address=address
            )
            card.owner = new_user
            card.save()

            return JsonResponse({'status': 'success', 'message': 'User registered successfully!'})

        except RFIDCard.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Card not found in system.'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def get_recipients(request):
    log_id = request.GET.get('log_id')
    if not log_id:
        return JsonResponse({'status': 'error', 'message': 'Missing log_id'}, status=400)

    try:
        log = AdminSetReliefLog.objects.get(id=log_id)
        recipients_data = []

        for user in log.users.all():
            claim = AidClaim.objects.filter(relief_log=log, user=user).first()
            received_time = claim.time_received if claim else log.timestamp

            recipients_data.append({
                'full_name': user.full_name,
                'address': user.address,
                'time_received': received_time.isoformat()
            })

        return JsonResponse({
            'status': 'success',
            'location': log.location,
            'supplies': log.supplies_relief,
            'timestamp': log.timestamp.isoformat(),
            'total_recipients': len(recipients_data),
            'recipients': recipients_data
        })
    except AdminSetReliefLog.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Supply record not found'}, status=404)

@csrf_exempt
def manual_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        full_name = data.get('full_name', '').strip()

        user = User.objects.filter(full_name__iexact=full_name).first()
        if user:
            return JsonResponse({'status': 'success', 'name': user.full_name, 'role': user.role})
        return JsonResponse({'status': 'error', 'message': 'Name not found.'}, status=404)

def get_user_records(request):
    full_name = request.GET.get('name', '').strip()
    user = User.objects.filter(full_name__iexact=full_name).first()
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

    card = RFIDCard.objects.filter(owner=user).first()
    card_uid = card.uid if card else 'No Card Linked'

    logs = AdminSetReliefLog.objects.filter(users=user).order_by('-timestamp')
    history = []

    for log in logs:
        claim = AidClaim.objects.filter(relief_log=log, user=user).first()
        received_time = claim.time_received if claim else log.timestamp
        history.append({
            'supplies': log.supplies_relief,
            'time_received': received_time.isoformat()
        })

    return JsonResponse({
        'status': 'success',
        'full_name': user.full_name,
        'address': user.address,
        'uid': card_uid,
        'history': history
    })

def dashboard(request):
    return render(request, 'admin_portal.html')

def edit_user_view(request):
    return render(request, 'edit_user.html')

def user_portal_view(request):
    return render(request, 'user_portal.html')

def save_user_view(request):
    return render(request, 'save_user.html')

def recipients_view(request):
    return render(request, 'recipients.html')

def index_view(request):
    return render(request, 'index.html')

