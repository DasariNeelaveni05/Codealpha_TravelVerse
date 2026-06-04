def notification_context(request):
    if request.user.is_authenticated:
        unread = request.user.notifications.filter(is_read=False).count()
        return {'unread_notifications': unread}
    return {'unread_notifications': 0}
