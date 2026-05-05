from app.services.supabase_client import get_supabase_client


def get_authenticated_client(access_token: str):
    client = get_supabase_client()
    client.postgrest.auth(access_token)
    return client


def save_analysis_supabase(
    report: dict,
    video_path: str,
    user_id: str,
    access_token: str
):
    supabase = get_authenticated_client(access_token)

    title = video_path.split("/")[-1].split(".")[0]
    score = report["score_comunicacao"]["score"]
    ai_available = report.get("analise_global_ia", {}).get("disponivel", False)

    supabase.table("analyses") \
        .delete() \
        .eq("user_id", user_id) \
        .eq("video_name", video_path) \
        .execute()

    data = {
        "user_id": user_id,
        "title": title,
        "video_name": video_path,
        "score": score,
        "transcription": report["transcricao"],
        "report_json": report,
        "ai_available": ai_available,
    }

    supabase.table("analyses").insert(data).execute()


def get_all_analyses_supabase(user_id: str, access_token: str):
    supabase = get_authenticated_client(access_token)

    response = (
        supabase
        .table("analyses")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data


def get_analysis_by_id_supabase(
    analysis_id: str,
    user_id: str,
    access_token: str
):
    supabase = get_authenticated_client(access_token)

    response = (
        supabase
        .table("analyses")
        .select("*")
        .eq("id", analysis_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not response.data:
        return None

    return response.data["report_json"]


def delete_analysis_supabase(
    analysis_id: str,
    user_id: str,
    access_token: str
):
    supabase = get_authenticated_client(access_token)

    (
        supabase
        .table("analyses")
        .delete()
        .eq("id", analysis_id)
        .eq("user_id", user_id)
        .execute()
    )


def get_average_score_supabase(user_id: str, access_token: str):
    data = get_all_analyses_supabase(user_id, access_token)

    if not data:
        return 0

    scores = [row["score"] for row in data]
    return round(sum(scores) / len(scores), 2)


def get_history_stats_supabase(user_id: str, access_token: str):
    data = get_all_analyses_supabase(user_id, access_token)

    if not data:
        return {
            "total_analyses": 0,
            "best_score": 0,
            "score_delta": 0,
        }

    chronological_data = list(reversed(data))
    scores = [row["score"] for row in chronological_data]

    return {
        "total_analyses": len(scores),
        "best_score": max(scores),
        "score_delta": scores[-1] - scores[0],
    }


def get_score_history_supabase(user_id: str, access_token: str):
    data = get_all_analyses_supabase(user_id, access_token)
    chronological_data = list(reversed(data))

    return [
        (row["title"], row["score"])
        for row in chronological_data
    ]