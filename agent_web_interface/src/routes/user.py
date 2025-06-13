from flask import Blueprint, jsonify, request, url_for, redirect, current_app
from src.models.user import User, db
from flask_jwt_extended import create_access_token, jwt_required, current_user
import os
import secrets # For generating random passwords for OAuth users

user_bp = Blueprint('user', __name__)

@user_bp.route('/auth/google/login')
def google_login():
    # For Authlib >= 0.15, redirect_uri should be passed to authorize_redirect
    # For older versions, it might be configured during oauth.register
    _google_oauth_client = current_app.extensions['authlib.integrations.flask_client'].clients['google']
    redirect_uri = url_for('user.authorize_google', _external=True)
    return _google_oauth_client.authorize_redirect(redirect_uri)

@user_bp.route('/auth/google/callback')
def authorize_google():
    _google_oauth_client = current_app.extensions['authlib.integrations.flask_client'].clients['google']
    try:
        token = _google_oauth_client.authorize_access_token()
    except Exception as e:
        return jsonify(msg=f"Error authorizing Google: {str(e)}"), 400

    userinfo_response = _google_oauth_client.get('userinfo')
    userinfo = userinfo_response.json()

    email = userinfo.get('email')
    if not email:
        return jsonify(msg="Email not found in Google userinfo"), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        # Create a new user
        # Username can be derived from email or name; ensure it's unique
        username = userinfo.get('name', email.split('@')[0])
        # Ensure username is unique
        temp_username = username
        counter = 1
        while User.query.filter_by(username=temp_username).first():
            temp_username = f"{username}{counter}"
            counter += 1
        username = temp_username

        user = User(
            email=email,
            username=username,
        )
        # For OAuth users, we can set a long random password or mark them as OAuth-only
        # For simplicity, generating a random password:
        user.set_password(secrets.token_hex(16))
        db.session.add(user)
        db.session.commit()

    # Generate JWT token for the user
    access_token = create_access_token(identity=user.id)
    # This response will be handled by the frontend.
    # For SPAs, the frontend might open this in a popup and then get the token.
    # Or, this endpoint could redirect to a frontend URL with the token.
    frontend_redirect_base_url = os.environ.get('FRONTEND_REDIRECT_BASE_URL', 'http://localhost:5173') # Default to Vite's common port
    return redirect(f"{frontend_redirect_base_url}/auth/handle-token?token={access_token}")


@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email, or password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "User created successfully"}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad email or password"}), 401

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    if not current_user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(current_user.to_dict()), 200
