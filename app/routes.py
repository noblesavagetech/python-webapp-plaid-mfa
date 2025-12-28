from flask import Blueprint, request, jsonify, url_for, redirect, session
from app import db
from app.models import QuestionnaireResponse, WaveToken
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from requests_oauthlib import OAuth2Session

bp = Blueprint('routes', __name__)


@bp.route('/questionnaire', methods=['POST'])
@jwt_required()
def submit_questionnaire():
    user_id = get_jwt_identity()
    data = request.json or {}
    score = data.get('score')
    qr = QuestionnaireResponse(user_id=user_id, answers=data, score=score)
    db.session.add(qr)
    db.session.commit()
    return jsonify({"id": qr.id, "score": qr.score}), 201


@bp.route('/questionnaire', methods=['GET'])
@jwt_required()
def list_questionnaires():
    user_id = get_jwt_identity()
    items = QuestionnaireResponse.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": i.id, "answers": i.answers, "score": i.score} for i in items])


@bp.route('/wave/connect')
@jwt_required()
def wave_connect():
    client_id = os.getenv('WAVE_CLIENT_ID')
    redirect_uri = os.getenv('WAVE_REDIRECT_URI') or url_for('routes.wave_callback', _external=True)
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url('https://api.waveapps.com/oauth2/authorize')
    session['oauth_state'] = state
    return redirect(authorization_url)


@bp.route('/wave/callback')
@jwt_required(optional=True)
def wave_callback():
    client_id = os.getenv('WAVE_CLIENT_ID')
    client_secret = os.getenv('WAVE_CLIENT_SECRET')
    redirect_uri = os.getenv('WAVE_REDIRECT_URI') or url_for('routes.wave_callback', _external=True)
    state = session.pop('oauth_state', None)
    oauth = OAuth2Session(client_id, state=state, redirect_uri=redirect_uri)
    try:
        token = oauth.fetch_token('https://api.waveapps.com/oauth2/token', client_secret=client_secret, authorization_response=request.url)
    except Exception as e:
        return jsonify({"error": "token_exchange_failed", "details": str(e)}), 400

    user_id = None
    try:
        user_id = get_jwt_identity()
    except Exception:
        user_id = None

    if not user_id:
        # If not authenticated, token can still be returned to caller to associate later
        return jsonify({"token": token}), 200

    wt = WaveToken(user_id=user_id, access_token=token.get('access_token'), refresh_token=token.get('refresh_token'))
    expires_at = token.get('expires_at')
    if expires_at:
        try:
            from datetime import datetime
            wt.expires_at = datetime.fromtimestamp(int(expires_at))
        except Exception:
            pass

    db.session.add(wt)
    db.session.commit()
    return jsonify({"message": "Wave token saved"}), 200
