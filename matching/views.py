# from django.shortcuts import render, redirect, get_object_or_404
# from django.views import View
# from users.models import User
# from .models import *
# from matching.service import jaccard_similarity, create_mutual_playlist
# from django.db.models import Q
# from django.http import JsonResponse
# import json

# class MatchUserView(View):
#     def get(self, request):
#         spotify_id = request.session.get("spotify_id")
#         current_user = get_object_or_404(User, spotify_id=spotify_id)
#         candidates = []

#         # หาคนที่ current_user เคย swipe ไปแล้ว
#         swiped_ids = Swipe.objects.filter(swiper=current_user).values_list("swiped__spotify_id", flat=True)

#         # filter เอาคนที่ยังไม่ถูก swipe
#         users_neverswiped = User.objects.filter(~Q(spotify_id=current_user.spotify_id)).exclude(
#             spotify_id__in=swiped_ids
#         )

#         # คำนวณ score จากความเหมือน genre, artist, track
#         for user in users_neverswiped:
#             genres_score = jaccard_similarity(current_user.music_profile.genres, user.music_profile.genres)
#             artists_score = jaccard_similarity(
#                 [a["id"] for a in current_user.music_profile.top_artists],
#                 [a["id"] for a in user.music_profile.top_artists]
#             )
#             tracks_score = jaccard_similarity(
#                 [t["id"] for t in current_user.music_profile.top_tracks],
#                 [t["id"] for t in user.music_profile.top_tracks]
#             )
#             total_score = 0.3 * genres_score + 0.4 * artists_score + 0.3 * tracks_score
#             candidates.append({"user": user, "score": total_score})

#         # เรียงจากคะแนนมากไปน้อย
#         candidates.sort(key=lambda x: x["score"], reverse=True)
#         next_user = candidates[0]["user"] if candidates else None

#         return render(request, "match.html", {
#             "current_user": current_user,
#             "next_user": next_user,
#             "candidates": candidates,
#         })

# class SwipeActionView(View):
#     def post(self, request):
#         spotify_id = request.session.get("spotify_id")
#         current_user = get_object_or_404(User, spotify_id=spotify_id)

#         swiped_id = request.POST.get("swiped_id")
#         action = request.POST.get("action")  # "like" หรือ "pass"

#         swiped_user = get_object_or_404(User, id=swiped_id)

#         # บันทึก swipe
#         Swipe.objects.create(swiper=current_user, swiped=swiped_user, action=action)

#         if action == "like":
#             both_like = Swipe.objects.filter(
#                 swiper=swiped_user, swiped=current_user, action="like"
#             ).exists()
#             if both_like:
#                 playlist = create_mutual_playlist(current_user, swiped_user)
#                 Match.objects.create(
#                     user1=current_user,
#                     user2=swiped_user,
#                     similarity_score=0,
#                     mutual_playlist=playlist
#                 )
#         return redirect("match_user")

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from users.models import User
from .models import Swipe, Match, MutualPlaylist
from .service import jaccard_similarity, create_mutual_playlist

def get_sorted_candidates(current_user):
    """calculates similarity scores for all users and returns them sorted."""
    #Find users the current_user has already swiped on.
    swiped_ids = Swipe.objects.filter(swiper=current_user).values_list("swiped__id", flat=True)

    #Filter the User queryset to get potential candidates.
    users_neverswiped = User.objects.exclude(id=current_user.id).exclude(id__in=swiped_ids)

    #Calculate the weighted similarity score for each candidate.
    candidates_with_scores = []
    for user in users_neverswiped:
        try:
            genres_score = jaccard_similarity(current_user.music_profile.genres, user.music_profile.genres)
            artists_score = jaccard_similarity(
                [a["id"] for a in current_user.music_profile.top_artists],
                [a["id"] for a in user.music_profile.top_artists]
            )
            tracks_score = jaccard_similarity(
                [t["id"] for t in current_user.music_profile.top_tracks],
                [t["id"] for t in user.music_profile.top_tracks]
            )
            # Calculate weighted total score (30% genres, 40% artists, 30% tracks)
            total_score = 0.3 * genres_score + 0.4 * artists_score + 0.3 * tracks_score
            
            # We only consider users with a score greater than 0
            if total_score > 0:
                candidates_with_scores.append({"user": user, "score": total_score})

        except (AttributeError, TypeError):
            # Handles cases where a user might not have a music profile yet
            continue

    # Sort the list of candidates by score in descending order.
    candidates_with_scores.sort(key=lambda x: x["score"], reverse=True)

    return candidates_with_scores


class DiscoverPageView(View):
    """Renders the initial HTML page, calculating the first user to show"""
    def get(self, request):
        spotify_id = request.session.get("spotify_id")
        current_user = get_object_or_404(User, spotify_id=spotify_id)
        
        # Get the sorted list of candidates using core logic
        candidates = get_sorted_candidates(current_user)
        next_user = candidates[0]['user'] if candidates else None
        
        return render(request, "matching/match.html", {
            "current_user": current_user,
            "next_user": next_user
        })


class SwipeActionAPI(View):
    """ API endpoint that handles a swipe action, checks for a match, always returns the next highest scoring profile"""
    def post(self, request):
        spotify_id = request.session.get("spotify_id")
        current_user = get_object_or_404(User, spotify_id=spotify_id)
        
        swiped_id = request.POST.get("swiped_id")
        action = request.POST.get("action")

        swiped_user = get_object_or_404(User, id=swiped_id)

        # Record the swipe
        Swipe.objects.create(swiper=current_user, swiped=swiped_user, action=action)
        
        is_match = False
        playlist_info = None

        if action == "like":
            if Swipe.objects.filter(swiper=swiped_user, swiped=current_user, action="like").exists():
                is_match = True
                playlist_name, playlist_url = create_mutual_playlist(current_user, swiped_user)
                new_playlist = MutualPlaylist.objects.create(name=playlist_name, spotify_playlist_id=playlist_url.split('/')[-1])
                Match.objects.get_or_create(user1=current_user, user2=swiped_user, defaults={'mutual_playlist': new_playlist})
                playlist_info = {'name': playlist_name, 'url': playlist_url}
        
        # After handling the swipe, get the NEW top candidate
        candidates = get_sorted_candidates(current_user)
        next_user = candidates[0]['user'] if candidates else None

        next_profile_data = None
        if next_user:
            next_profile_data = {
                "id": next_user.id,
                "username": next_user.username,
                "bio": next_user.bio,
                "profile_picture_url": next_user.profile_picture.url if next_user.profile_picture else "/static/default_avatar.png"
            }

        return JsonResponse({
            "status": "ok", 
            "match": is_match, 
            "playlist": playlist_info,
            "next_profile": next_profile_data # Return the next profile in the same response
        })