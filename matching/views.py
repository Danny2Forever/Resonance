from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from users.models import User
from chat.models import Chat
from .models import *
from matching.service import jaccard_similarity, create_mutual_playlist
from django.db.models import Q
from django.http import JsonResponse
import json
from django.db import transaction

class MatchUserView(View):
    def get(self, request):
        spotify_id = request.session.get("spotify_id")
        current_user = get_object_or_404(User, spotify_id=spotify_id)
        candidates = []

        # หาคนที่ current_user เคย swipe ไปแล้ว
        swiped_ids = Swipe.objects.filter(swiper=current_user).values_list("swiped__spotify_id", flat=True)

        # filter เอาคนที่ยังไม่ถูก swipe
        users_neverswiped = User.objects.filter(~Q(spotify_id=current_user.spotify_id)).exclude(
            spotify_id__in=swiped_ids
        )

        # คำนวณ score จากความเหมือน genre, artist, track
        for user in users_neverswiped:
            genres_score = jaccard_similarity(current_user.music_profile.genres, user.music_profile.genres)
            artists_score = jaccard_similarity(
                [a["id"] for a in current_user.music_profile.top_artists],
                [a["id"] for a in user.music_profile.top_artists]
            )
            tracks_score = jaccard_similarity(
                [t["id"] for t in current_user.music_profile.top_tracks],
                [t["id"] for t in user.music_profile.top_tracks]
            )
            total_score = 0.3 * genres_score + 0.4 * artists_score + 0.3 * tracks_score
            candidates.append({"user": user, "score": total_score})

        # เรียงจากคะแนนมากไปน้อย
        candidates.sort(key=lambda x: x["score"], reverse=True)
        next_user = candidates[0]["user"] if candidates else None

        return render(request, "match.html", {
            "current_user": current_user,
            "next_user": next_user,
            "candidates": candidates,
        })

class SwipeActionView(View):
    def post(self, request):
        spotify_id = request.session.get("spotify_id")
        current_user = get_object_or_404(User, spotify_id=spotify_id)

        swiped_id = request.POST.get("swiped_id")
        action = request.POST.get("action")  # "like" หรือ "pass"

        swiped_user = get_object_or_404(User, id=swiped_id)

        # บันทึก swipe
        Swipe.objects.create(swiper=current_user, swiped=swiped_user, action=action)

        if action == "like":
            both_like = Swipe.objects.filter(
                swiper=swiped_user, swiped=current_user, action="like"
            ).exists()
            if both_like:
                with transaction.atomic(): # mutual, match กับ chat จะได้ถูกสร้างพร้อมกัน
                    playlist = create_mutual_playlist(current_user, swiped_user)
                    match_obj = Match.objects.create(
                        user1=current_user,
                        user2=swiped_user,
                        similarity_score=0,
                        mutual_playlist=playlist
                    )
                    Chat.objects.create(match=match_obj)
        return redirect("match_user")
