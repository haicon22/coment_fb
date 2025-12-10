# fb_logic.py
import requests
import json
import base64

def feedback_from_number(id_cm: str) -> str:
    return base64.b64encode(f"feedback:{id_cm}".encode()).decode()

def fb_comment(cookie, uid, dtsg, comment_text, id_cm):
    url = "https://www.facebook.com/api/graphql/"
    feedback_id = feedback_from_number(id_cm)

    payload = {
      'av': uid,
      '__user': uid,
      'fb_dtsg': dtsg,
      '__crn': "comet.fbweb.CometSinglePostDialogRoute",
      'fb_api_caller_class': "RelayModern",
      'fb_api_req_friendly_name': "useCometUFICreateCommentMutation",
      'server_timestamps': "true",
      'variables': json.dumps({
          "feedLocation": "POST_PERMALINK_DIALOG",
          "feedbackSource": 2,
          "groupID": None,
          "input": {
              "client_mutation_id": "1",
              "actor_id": uid,
              "attachments": None,
              "feedback_id": feedback_id,
              "formatting_style": None,
              "message": {
                  "ranges": [],
                  "text": comment_text
              },
              "attribution_id_v2": "",
              "vod_video_timestamp": None,
              "is_tracking_encrypted": True,
              "tracking": [],
              "feedback_source": "OBJECT",
              "idempotence_token": "",
              "session_id": ""
          },
          "inviteShortLinkKey": None,
          "renderLocation": None,
          "scale": 3,
          "useDefaultActor": False,
          "focusCommentID": None
      }),
      'doc_id': "24615176934823390"
    }

    headers = {
      'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/143 Version/11.1.1 Safari/605.1.15",
      'x-fb-friendly-name': "useCometUFICreateCommentMutation",
      'sec-fetch-site': "same-origin",
      'accept-language': "vi-VN,vi;q=0.9",
      'sec-fetch-mode': "cors",
      'origin': "https://www.facebook.com",
      'referer': "https://www.facebook.com/",
      'Cookie': cookie
    }

    resp = requests.post(url, data=payload, headers=headers)

    try:
        js = resp.json()
        node = js["data"]["comment_create"]["feedback_comment_edge"]["node"]
        return True, {
            "comment_id": node["legacy_fbid"],
            "text": node["body"]["text"]
        }
    except Exception as e:
        with open("comment_error.json", "w", encoding="utf-8") as f:
            f.write(resp.text)
        return False, f"Lỗi parse JSON → đã lưu vào comment_error.json: {e}"
