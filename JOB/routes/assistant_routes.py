from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from services.career_assistant import CareerAssistant

assistant_bp = Blueprint("assistant", __name__, url_prefix="/assistant")
assistant_service = CareerAssistant()

@assistant_bp.route("")
@login_required
def chat_view():
    context_job_id = request.args.get("job_id", type=int)
    return render_template("career_assistant.html", context_job_id=context_job_id)

@assistant_bp.route("/api/chat", methods=["POST"])
@login_required
def handle_chat_message():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    context_job_id = data.get("context_job_id")

    if not message:
        return jsonify({"success": False, "error": "Message cannot be empty."}), 400

    response = assistant_service.process_message(
        user=current_user,
        message=message,
        context_job_id=context_job_id
    )
    return jsonify({"success": True, "data": response})
