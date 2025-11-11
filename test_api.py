"""
Test API Script - Ví dụ sử dụng API với Python

HƯỚNG DẪN:
1. Chạy server: uvicorn app.main:app --reload
2. Chạy script này: python test_api.py

Script này demo các use cases thực tế
"""

import requests
from datetime import datetime, date
import json

BASE_URL = "http://localhost:8000/api/v1"


def print_response(title: str, response: requests.Response):
    """Helper function để print response đẹp"""
    print(f"\n{'='*60}")
    print(f"📍 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")


def test_flow():
    """Test complete flow"""

    # =========================================================================
    # USE CASE 1: REGISTER NEW USER
    # =========================================================================
    print("\n🎯 USE CASE 1: ĐĂNG KÝ USER MỚI")

    user_data = {
        "email": "demo@example.com",
        "full_name": "Nguyễn Văn Demo",
        "password": "password123",
        "bio": "Software Engineer tại ABC Company"
    }

    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print_response("Đăng ký user mới", response)

    if response.status_code != 201:
        print("⚠️  User có thể đã tồn tại. Tiếp tục test với user này...")

    # =========================================================================
    # USE CASE 2: LOGIN VÀ LẤY TOKEN
    # =========================================================================
    print("\n🎯 USE CASE 2: LOGIN")

    login_data = {
        "username": user_data["email"],  # OAuth2 dùng "username"
        "password": user_data["password"]
    }

    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data,  # Form data
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print_response("Login", response)

    if response.status_code != 200:
        print("❌ Login failed. Exiting...")
        return

    # Lưu token
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print(f"\n✅ Token: {token[:50]}...")

    # =========================================================================
    # USE CASE 3: LẤY THÔNG TIN USER HIỆN TẠI
    # =========================================================================
    print("\n🎯 USE CASE 3: XEM THÔNG TIN CỦA MÌNH")

    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response("Thông tin user hiện tại", response)

    user_id = response.json()["id"]

    # =========================================================================
    # USE CASE 4: TẠO ACTIVITIES
    # =========================================================================
    print("\n🎯 USE CASE 4: LOG HOẠT ĐỘNG CỦA USER")

    activities = [
        {"action_type": "LOGIN", "description": "User logged in via web"},
        {"action_type": "VIEW", "description": "Viewed product catalog"},
        {"action_type": "VIEW", "description": "Viewed product details - iPhone 15"},
        {"action_type": "UPDATE", "description": "Updated profile information"},
        {"action_type": "CREATE", "description": "Created new post"},
    ]

    for activity in activities:
        response = requests.post(
            f"{BASE_URL}/users/{user_id}/activities",
            json=activity,
            headers=headers
        )
        if response.status_code == 201:
            print(f"✅ Logged: {activity['action_type']} - {activity['description']}")

    # =========================================================================
    # USE CASE 5: XEM LỊCH SỬ HOẠT ĐỘNG
    # =========================================================================
    print("\n🎯 USE CASE 5: XEM LỊCH SỬ HOẠT ĐỘNG")

    response = requests.get(
        f"{BASE_URL}/users/{user_id}/activities?skip=0&limit=10",
        headers=headers
    )
    print_response("Lịch sử hoạt động (10 gần nhất)", response)

    # =========================================================================
    # USE CASE 6: XEM ACTIVITIES TRONG NGÀY
    # =========================================================================
    print("\n🎯 USE CASE 6: XEM ACTIVITIES HÔM NAY")

    today = date.today().isoformat()
    response = requests.get(
        f"{BASE_URL}/users/{user_id}/activities/date/{today}",
        headers=headers
    )
    print_response(f"Activities hôm nay ({today})", response)

    # =========================================================================
    # USE CASE 7: THỐNG KÊ ACTIVITIES
    # =========================================================================
    print("\n🎯 USE CASE 7: THỐNG KÊ ACTIVITIES HÔM NAY")

    response = requests.get(
        f"{BASE_URL}/users/{user_id}/activities/stats/{today}",
        headers=headers
    )
    print_response("Thống kê activities breakdown", response)

    # =========================================================================
    # USE CASE 8: XEM ACTIVITIES THEO LOẠI
    # =========================================================================
    print("\n🎯 USE CASE 8: XEM TẤT CẢ LOGIN ACTIVITIES")

    response = requests.get(
        f"{BASE_URL}/users/{user_id}/activities/type/LOGIN",
        headers=headers
    )
    print_response("Tất cả LOGIN activities", response)

    # =========================================================================
    # USE CASE 9: XEM USER STATISTICS
    # =========================================================================
    print("\n🎯 USE CASE 9: XEM THỐNG KÊ USER")

    response = requests.get(
        f"{BASE_URL}/users/{user_id}/statistics",
        headers=headers
    )
    print_response("User statistics", response)

    # =========================================================================
    # USE CASE 10: UPDATE USER PROFILE
    # =========================================================================
    print("\n🎯 USE CASE 10: UPDATE PROFILE")

    update_data = {
        "full_name": "Nguyễn Văn Demo (Updated)",
        "bio": "Senior Software Engineer tại XYZ Company"
    }

    response = requests.put(
        f"{BASE_URL}/users/{user_id}",
        json=update_data,
        headers=headers
    )
    print_response("Update profile", response)

    # =========================================================================
    # USE CASE 11: LIST USERS (PAGINATION)
    # =========================================================================
    print("\n🎯 USE CASE 11: XEM DANH SÁCH USERS")

    response = requests.get(
        f"{BASE_URL}/users?skip=0&limit=5",
        headers=headers
    )
    print_response("Danh sách users (page 1, limit 5)", response)

    # =========================================================================
    # USE CASE 12: USERS ĐĂNG KÝ HÔM NAY
    # =========================================================================
    print("\n🎯 USE CASE 12: XEM USERS ĐĂNG KÝ HÔM NAY")

    response = requests.get(
        f"{BASE_URL}/users/today",
        headers=headers
    )
    print_response("Users đăng ký hôm nay", response)

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "="*60)
    print("✅ HOÀN THÀNH TEST FLOW!")
    print("="*60)
    print("\nĐã test các use cases:")
    print("1. ✅ Đăng ký user")
    print("2. ✅ Login và lấy JWT token")
    print("3. ✅ Xem thông tin user hiện tại")
    print("4. ✅ Log activities")
    print("5. ✅ Xem lịch sử hoạt động")
    print("6. ✅ Xem activities theo ngày")
    print("7. ✅ Thống kê activities breakdown")
    print("8. ✅ Filter activities theo type")
    print("9. ✅ User statistics")
    print("10. ✅ Update profile")
    print("11. ✅ List users với pagination")
    print("12. ✅ Users đăng ký hôm nay")

    print("\n💡 TIP: Mở Swagger UI tại http://localhost:8000/docs để test interactive!")


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     FASTAPI USER SERVICE - API TEST SCRIPT                ║
    ║                                                           ║
    ║     Đảm bảo server đang chạy tại http://localhost:8000   ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    try:
        # Check server
        response = requests.get(f"{BASE_URL}/../health", timeout=2)
        if response.status_code == 200:
            print("✅ Server đang chạy!\n")
            test_flow()
        else:
            print("❌ Server không phản hồi đúng")
    except requests.exceptions.ConnectionError:
        print("❌ Không thể kết nối tới server!")
        print("   Chạy lệnh: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
