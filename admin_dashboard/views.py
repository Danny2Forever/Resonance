from django.views.generic import TemplateView
from users.models import User
from matching.models import Match, Swipe, MutualPlaylist
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseForbidden 
from users.service import get_current_user
from django.core.paginator import Paginator

class AdminDashboardView(View):
    def get(self, request):
        current_user = get_current_user(request)
        if not current_user or not current_user.is_admin:
            return HttpResponseForbidden("Access denied: Admins only.")

        # Dashboard stats
        total_users = User.objects.count()
        total_matches = Match.objects.count()
        total_swipes = Swipe.objects.count()
        total_playlists = MutualPlaylist.objects.count()

        # Recent Swipes (latest 100)
        recent_swipes = (
            Swipe.objects.select_related("swiper", "swiped")
            .order_by("-swiped_at")[:100]
        )
        swipes_paginator = Paginator(recent_swipes, 10)  # 10 per page
        swipes_page_number = request.GET.get("swipe_page", 1)
        # print(swipes_paginator.get_page(2)[0])
        swipes_page_obj = swipes_paginator.get_page(swipes_page_number)

        # Recent Matches (latest 50)
        recent_matches = (
            Match.objects.select_related("user1", "user2")
            .order_by("-matched_at")[:50]
        )
        matches_paginator = Paginator(recent_matches, 10)  # 10 per page
        matches_page_number = request.GET.get("match_page", 1)
        matches_page_obj = matches_paginator.get_page(matches_page_number)

        context = {
            "total_users": total_users,
            "total_matches": total_matches,
            "total_swipes": total_swipes,
            "total_playlists": total_playlists,
            "swipes_page_obj": swipes_page_obj,
            "matches_page_obj": matches_page_obj,
        }

        return render(request, "admin-dashboard/dashboard.html", context)
