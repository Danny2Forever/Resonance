from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import User
from .models import Swipe, Match
from .service import jaccard_similarity, create_mutual_playlist
from chat.models import Chat
from users.service import get_current_user
from spotify.refresh import refresh_user_profile

class MatchUserView(View):
    def get(self, request):
        spotify_id = request.session.get("spotify_id")
        refresh_user_profile(request)
        # ใช้ related เพื้่อง่ายต่อการหา user music profile
        current_user = get_object_or_404(User.objects.select_related('usermusicprofile'), spotify_id=spotify_id)
        
        # เอา user ที่เป็น current_user เคย swipe แล้วออก
        swiped_user_ids = Swipe.objects.filter(swiper=current_user).values_list('swiped_id', flat=True)
        candidates = User.objects.exclude(id=current_user.id).exclude(id__in=swiped_user_ids).select_related('usermusicprofile')

        candidate_scores = []
        for user in candidates:

            user1_profile = current_user.usermusicprofile
            user2_profile = user.usermusicprofile

            # Safely access the attributes of the profile objects
            genres1 = user1_profile.genres if user1_profile else []  
            genres2 = user2_profile.genres if user2_profile else []
            
            artists1 = [a['id'] for a in user1_profile.top_artists] if user1_profile else []
            artists2 = [a['id'] for a in user2_profile.top_artists] if user2_profile else []

            tracks1 = [t['id'] for t in user1_profile.top_tracks] if user1_profile else []
            tracks2 = [t['id'] for t in user2_profile.top_tracks] if user2_profile else []

            genres_score = jaccard_similarity(genres1, genres2)
            artists_score = jaccard_similarity(artists1, artists2)
            tracks_score = jaccard_similarity(tracks1, tracks2)
            
            # ค่าน้ำหนักของแต่ละส่วน
            total_score = 0.3 * genres_score + 0.4 * artists_score + 0.3 * tracks_score
            candidate_scores.append({"user": user, "score": total_score})

        candidate_scores.sort(key=lambda x: x["score"], reverse=True)
        print(candidate_scores)
        
        swipe_user = candidate_scores[0]["user"] if candidate_scores else None
        return render(request, "matching/match.html", {"next_user": swipe_user})

class SwipeActionView(View):
    def post(self, request):
        current_user = get_current_user(request)
        swiped_user = get_object_or_404(User, id=request.POST.get("swiped_id"))
        action = request.POST.get("action")

        if Swipe.objects.filter(swiper=current_user, swiped=swiped_user).exists():
            return JsonResponse({"error": "Already swiped"}, status=400)

        Swipe.objects.create(swiper=current_user, swiped=swiped_user, action=action)
        try:
            similarity_score = float(request.POST.get("similarity_score", 0.0))
        except ValueError:
            similarity_score = 0.0

        if action == "like":
            if Swipe.objects.filter(swiper=swiped_user, swiped=current_user, action="like").exists():
                playlist_obj = create_mutual_playlist(request, current_user, swiped_user)
                new_match = Match.objects.create(
                    user1=current_user,
                    user2=swiped_user,
                    similarity_score=similarity_score,
                    mutual_playlist=playlist_obj
                )
                Chat.objects.create(match=new_match)
                match_details = {
                    "matched_user_name": swiped_user.username,
                    "matched_user_avatar": swiped_user.profile_picture.url if swiped_user.profile_picture else None,
                    "playlist_url": playlist_obj.spotify_url if playlist_obj else None
                }
                return JsonResponse({"matched": True, "match_details": match_details})

        return JsonResponse({"matched": False})
    
class MatchListView(LoginRequiredMixin, View):
    def get(self, request):
        matches = Match.objects.filter(
            Q(user1=request.user) | Q(user2=request.user)
        ).select_related('user1', 'user2', 'mutual_playlist')

        context = {
            'matches': matches
        }
        return render(request, 'matching/my_match.html', context)