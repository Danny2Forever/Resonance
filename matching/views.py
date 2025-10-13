from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from users.models import User
from .models import Swipe, Match
from .service import jaccard_similarity, create_mutual_playlist
from chat.models import Chat


class MatchUserView(View):
    def get(self, request):
        spotify_id = request.session.get("spotify_id")
        # Use select_related to efficiently fetch the related music_profile in the same query
        current_user = get_object_or_404(User.objects.select_related('music_profile'), spotify_id=spotify_id)
        
        swiped_user_ids = Swipe.objects.filter(swiper=current_user).values_list('swiped_id', flat=True)

        # Fetch the music_profiles for all candidates to avoid extra queries in the loop
        candidates = User.objects.exclude(id=current_user.id).exclude(id__in=swiped_user_ids).select_related('music_profile')

        candidate_scores = []
        for user in candidates:
            # Access attributes directly
            # Provide default empty lists if a profile or its attributes don't exist
            
            user1_profile = getattr(current_user, 'music_profile', None)
            user2_profile = getattr(user, 'music_profile', None)

            # Safely access the attributes of the profile objects
            genres1 = getattr(user1_profile, 'genres', []) if user1_profile else []
            genres2 = getattr(user2_profile, 'genres', []) if user2_profile else []
            
            artists1 = [a['id'] for a in getattr(user1_profile, 'top_artists', [])] if user1_profile else []
            artists2 = [a['id'] for a in getattr(user2_profile, 'top_artists', [])] if user2_profile else []

            tracks1 = [t['id'] for t in getattr(user1_profile, 'top_tracks', [])] if user1_profile else []
            tracks2 = [t['id'] for t in getattr(user2_profile, 'top_tracks', [])] if user2_profile else []

            genres_score = jaccard_similarity(genres1, genres2)
            artists_score = jaccard_similarity(artists1, artists2)
            tracks_score = jaccard_similarity(tracks1, tracks2)
            
            total_score = 0.3 * genres_score + 0.4 * artists_score + 0.3 * tracks_score
            candidate_scores.append({"user": user, "score": total_score})

        candidate_scores.sort(key=lambda x: x["score"], reverse=True)
        
        next_user = candidate_scores[0]["user"] if candidate_scores else None

        return render(request, "matching/match.html", {"current_user": current_user, "next_user": next_user})

class SwipeActionView(View):
    def post(self, request):
        current_user = get_object_or_404(User, spotify_id=request.session.get("spotify_id"))
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