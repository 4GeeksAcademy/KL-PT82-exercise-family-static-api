import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

jackson_family = FamilyStructure("Jackson")

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

# 1) GET /members — Get all family members
@app.route('/members', methods=['GET'])
def get_members():
    try:
        members = jackson_family.get_all_members()
        if not isinstance(members, list):
            return jsonify({"error": "Bad request"}), 400
        return jsonify(members), 200
    except Exception:
        return jsonify({"error": "Internal server error"}), 500

# 2) GET /members/<int:member_id> — Get one member by id
@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    try:
        member = jackson_family.get_member(member_id)
        if not member:
            return jsonify({"error": "Member not found"}), 404
        return jsonify(member), 200
    except Exception:
        return jsonify({"error": "Internal server error"}), 500

# 3) POST /members — Add a new member
@app.route('/members', methods=['POST'])
def add_member():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    try:
        body = request.get_json()
        # Validate required fields (id optional)
        required_fields = {"first_name", "age", "lucky_numbers"}
        if not body or not required_fields.issubset(body.keys()):
            return jsonify({"error": "Missing required fields"}), 400
        
        new_member = jackson_family.add_member(body)
        return jsonify(new_member), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500

# 4) DELETE /members/<int:member_id> — Delete a member by id
@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    try:
        deleted = jackson_family.delete_member(member_id)
        if deleted:
            return jsonify({"done": True}), 200
        return jsonify({"error": "Member not found"}), 404
    except Exception:
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
