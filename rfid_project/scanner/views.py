from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import AttendanceLog
from django.shortcuts import render


@csrf_exempt
def record_scan(request):
    if request.method == 'POST':  # Check if the incoming request is a POST method (sending data)
        data = json.loads(request.body) # Decode the JSON package sent by your bridge script
        scanned_uid = data.get('uid')

        if scanned_uid:
            AttendanceLog.objects.create(uid=scanned_uid) # Save the new scan directly into your SQLite database
            return JsonResponse({'status': 'success', 'message': f'Successfully logged UID: {scanned_uid}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

def get_logs(request):
    logs = AttendanceLog.objects.all().order_by('-timestamp')[:50] # Retrieve the 50 most recent attendance logs from the database

    data = [] # Format the data into a simple dictionary list
    for log in logs:
        data.append({
            'uid': log.uid,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })

    return JsonResponse({'logs': data})

def dashboard(request):
    return render(request, 'index.html')