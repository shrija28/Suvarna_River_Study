import os
import sys
import secrets

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox --disable-gpu"
project_root = r"d:\Suvarna_River_Study"
sys.path.insert(0, os.path.join(project_root, "qt_version"))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from app import MainWindow

app = QApplication.instance() or QApplication([])

print("--- STARTING LOGIN & AUTHENTICATION INTEGRATION TEST ---")
win = MainWindow()
win.resize(1600, 950)
win.show()

# ----------------------------------------------------------------------------
# Test 1: Application startup opens on Login Page (Home page hidden)
# ----------------------------------------------------------------------------
assert win.root_stack.currentIndex() == 0, f"Expected root_stack index 0 (LoginPage), got {win.root_stack.currentIndex()}"
assert win.is_authenticated() is False, "Expected unauthenticated state on launch"
print("✓ Test 1 Passed: Application launches directly on Login Page (Home page is hidden).")

# Save startup screenshot (shows Login screen)
startup_pix = win.login_page.grab()
out_startup = r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be\auth_test_1_startup_login.png"
startup_pix.save(out_startup)
print(f"  Captured startup screenshot: {out_startup}", flush=True)

# ----------------------------------------------------------------------------
# Test 2: Invalid credentials rejected
# ----------------------------------------------------------------------------
win.login_page.input_username.setText("admin")
win.login_page.input_password.setText("wrongpassword123")
win.login_page.handle_login()

assert win.is_authenticated() is False, "Expected authentication failure"
assert win.root_stack.currentIndex() == 0, "Expected to stay on LoginPage on failure"
assert win.login_page.feedback_banner.isVisible() is True, "Expected error banner to be visible"
assert "Invalid username or password" in win.login_page.feedback_banner.text(), "Expected error message"
print("✓ Test 2 Passed: Invalid credentials rejected with appropriate error banner.")

# ----------------------------------------------------------------------------
# Test 3: Protected pages cannot be accessed without authentication
# ----------------------------------------------------------------------------
win.navigate_to_page(1)  # Try to force navigate to LULC
assert win.root_stack.currentIndex() == 0, "Protected access violated: accessed without auth"
win.go_to_home()
assert win.root_stack.currentIndex() == 0, "Protected access violated: home accessible without auth"
print("✓ Test 3 Passed: Protected pages strictly blocked without authentication.")

# ----------------------------------------------------------------------------
# Test 4: Valid credentials open the existing Home Page
# ----------------------------------------------------------------------------
win.login_page.input_username.setText("admin")
win.login_page.input_password.setText("admin123")
win.login_page.handle_login()

assert win.is_authenticated() is True, "Expected authentication success"
assert win.root_stack.currentIndex() == 1, f"Expected root_stack index 1 (Dashboard), got {win.root_stack.currentIndex()}"
assert win.stack.currentIndex() == 0, f"Expected active page 0 (Home), got {win.stack.currentIndex()}"
assert win.current_user["username"] == "admin", "Expected current_user to be admin"
print(f"✓ Test 4 Passed: Valid credentials successfully authenticate. Logged in as: {win.current_user['username']} ({win.current_user['role']}).")
print("  Existing Home page opened exactly as designed.")

# Save logged-in banner screenshot
dash_pix = win.banner.grab()
out_dash = r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be\auth_test_2_logged_in_dashboard.png"
dash_pix.save(out_dash)
print(f"  Captured logged-in banner screenshot: {out_dash}", flush=True)

# ----------------------------------------------------------------------------
# Test 5: Logout returns to Login Page and clears session
# ----------------------------------------------------------------------------
win.logout()
assert win.is_authenticated() is False, "Expected session cleared on logout"
assert win.root_stack.currentIndex() == 0, "Expected return to Login Page on logout"
assert win.login_page.feedback_banner.isVisible() is True, "Expected logout feedback visible"
assert "logged out" in win.login_page.feedback_banner.text().lower(), "Expected logout success message"
print("✓ Test 5 Passed: Logout cleanly terminates session and returns to Login Page.")

# ----------------------------------------------------------------------------
# Test 6: Registration & Login with new user
# ----------------------------------------------------------------------------
new_user = f"scientist_{secrets.token_hex(3)}"
reg_ok, reg_err = win.auth_service.register(
    username=new_user,
    email=f"{new_user}@suvarnariver.org",
    password="SecurePassword2026",
    confirm_password="SecurePassword2026",
    full_name="Dr. New Researcher",
    role="Lead Scientist"
)
assert reg_ok is True, f"Registration failed: {reg_err}"

win.login_page.input_username.setText(new_user)
win.login_page.input_password.setText("SecurePassword2026")
win.login_page.handle_login()

assert win.is_authenticated() is True, "Expected login success with new user"
assert win.current_user["username"] == new_user
assert win.current_user["role"] == "Lead Scientist"
print(f"✓ Test 6 Passed: User registration verified. Logged in as: {win.current_user['username']} ({win.current_user['role']}).")

print("\n--- ALL 6 AUTHENTICATION & LOGIN INTEGRATION TESTS PASSED SUCCESSFULLY! ---")
