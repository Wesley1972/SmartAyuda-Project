from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import AttendanceLog


@csrf_exempt
def record_scan(request):
    # Check if the incoming request is a POST method (sending data)
    if request.method == 'POST':
        # Decode the JSON package sent by your bridge script
        data = json.loads(request.body)
        scanned_uid = data.get('uid')

        if scanned_uid:
            # Save the new scan directly into your SQLite database
            AttendanceLog.objects.create(uid=scanned_uid)
            return JsonResponse({'status': 'success', 'message': f'Successfully logged UID: {scanned_uid}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)