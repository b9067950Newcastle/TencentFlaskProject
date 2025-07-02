from flask import Blueprint, request, jsonify
from models import Host
import ipaddress

ping_service_blueprint = Blueprint('ping_service', __name__, template_folder='templates')

@ping_service_blueprint.route("/ping", methods=['GET'])
def ping():
    """通过查询参数检查主机是否存在"""
    ip = request.args.get('ip')

    if not ip:
        return jsonify({
            "error": "Missing 'ip' parameter",
            "usage": "ping?ip=192.168.1.1"
        }), 400

    # 验证IP格式
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return jsonify({"error": "Invalid IP address format"}), 400

    host = Host.get_by_ip(ip)
    if host:
        return jsonify({
            "exists": True,
            "host_id": host.id,
            "host_name": host.host_name,
            "ip": host.ip_address
        })
    return jsonify({"exists": False, "ip": ip})