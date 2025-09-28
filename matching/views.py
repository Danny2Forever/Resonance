from django.shortcuts import render, get_object_or_404
from django.views import View
from users.models import User

class MatchUserView(View):
    """
    CBV สำหรับแสดงหน้า match / swipe
    """
    def get(self, request):
        # ดึงผู้ใช้ปัจจุบันจาก session
        spotify_id = request.session.get("spotify_id")
        if not spotify_id:
            # ถ้าไม่ login → redirect หรือ render หน้า login
            return render(request, "login.html", {"spotify_auth_url": "/login/"})

        current_user = get_object_or_404(User, spotify_id=spotify_id)

        # ตัวอย่าง: เลือก user คนต่อไปสำหรับ swipe
        potential_users = User.objects.exclude(id=current_user.id)[:1]  # เลือก user คนแรก
        next_user = potential_users[0] if potential_users else None

        return render(request, "match.html", {"current_user": current_user, "next_user": next_user})
