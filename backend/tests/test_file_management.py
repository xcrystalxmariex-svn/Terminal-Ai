"""
File Management API Tests
Tests for file browser features: list files, read files, create/write files, create directories, delete files
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('EXPO_PUBLIC_BACKEND_URL')
if not BASE_URL:
    pytest.skip("EXPO_PUBLIC_BACKEND_URL not set", allow_module_level=True)
BASE_URL = BASE_URL.rstrip('/')


class TestFileManagementAPIs:
    """File management endpoints: GET /api/files, POST /api/files/write, etc."""

    def test_list_root_directory(self, api_client):
        """Test GET /api/files?path=/ lists root directory"""
        response = api_client.get(f"{BASE_URL}/api/files?path=/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "path" in data, "Response should contain 'path' field"
        assert "items" in data, "Response should contain 'items' field"
        assert isinstance(data["items"], list), "items should be a list"
        assert data["path"] == "/", f"Expected path '/', got {data['path']}"
        print(f"✓ Root directory listed: {len(data['items'])} items")

    def test_list_app_directory(self, api_client):
        """Test GET /api/files?path=/app lists /app directory with backend and frontend folders"""
        response = api_client.get(f"{BASE_URL}/api/files?path=/app")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["path"] == "/app", f"Expected path '/app', got {data['path']}"
        assert "parent" in data, "Response should contain 'parent' field"
        assert data["parent"] == "/", f"Parent should be '/', got {data['parent']}"
        
        items = data["items"]
        item_names = [item["name"] for item in items]
        
        # Check that backend and frontend folders exist
        assert "backend" in item_names, "Should contain 'backend' folder"
        assert "frontend" in item_names, "Should contain 'frontend' folder"
        
        # Verify backend item is a directory
        backend_item = next((item for item in items if item["name"] == "backend"), None)
        assert backend_item is not None, "backend folder should exist"
        assert backend_item["is_dir"] is True, "backend should be a directory"
        
        # Verify frontend item is a directory
        frontend_item = next((item for item in items if item["name"] == "frontend"), None)
        assert frontend_item is not None, "frontend folder should exist"
        assert frontend_item["is_dir"] is True, "frontend should be a directory"
        
        print(f"✓ /app directory listed: found backend and frontend folders among {len(items)} items")

    def test_list_backend_directory(self, api_client):
        """Test GET /api/files?path=/app/backend lists server.py and requirements.txt"""
        response = api_client.get(f"{BASE_URL}/api/files?path=/app/backend")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["path"] == "/app/backend", f"Expected path '/app/backend', got {data['path']}"
        
        items = data["items"]
        item_names = [item["name"] for item in items]
        
        # Check that server.py and requirements.txt exist
        assert "server.py" in item_names, "Should contain 'server.py' file"
        assert "requirements.txt" in item_names, "Should contain 'requirements.txt' file"
        
        # Verify server.py is a file (not directory)
        server_item = next((item for item in items if item["name"] == "server.py"), None)
        assert server_item is not None, "server.py should exist"
        assert server_item["is_dir"] is False, "server.py should be a file, not directory"
        assert server_item["size"] is not None, "server.py should have a size"
        assert server_item["size"] > 0, "server.py should not be empty"
        
        print(f"✓ /app/backend directory listed: found server.py and requirements.txt among {len(items)} items")

    def test_read_server_py_file(self, api_client):
        """Test GET /api/files/read?path=/app/backend/server.py reads file content"""
        response = api_client.get(f"{BASE_URL}/api/files/read?path=/app/backend/server.py")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "path" in data, "Response should contain 'path' field"
        assert "name" in data, "Response should contain 'name' field"
        assert "content" in data, "Response should contain 'content' field"
        assert "language" in data, "Response should contain 'language' field"
        assert "size" in data, "Response should contain 'size' field"
        
        assert data["path"] == "/app/backend/server.py", f"Expected path '/app/backend/server.py', got {data['path']}"
        assert data["name"] == "server.py", f"Expected name 'server.py', got {data['name']}"
        assert data["language"] == "python", f"Expected language 'python', got {data['language']}"
        assert len(data["content"]) > 0, "File content should not be empty"
        assert "FastAPI" in data["content"], "server.py should contain 'FastAPI'"
        
        print(f"✓ server.py read successfully: {len(data['content'])} chars, language={data['language']}")

    def test_create_new_file_and_verify(self, api_client):
        """Test POST /api/files/write creates new file and verify it exists"""
        test_file_path = "/tmp/TEST_new_file.txt"
        test_content = "This is a test file created by pytest\nLine 2\nLine 3"
        
        # Create file
        create_response = api_client.post(
            f"{BASE_URL}/api/files/write",
            json={"path": test_file_path, "content": test_content}
        )
        assert create_response.status_code == 200, f"Expected 200, got {create_response.status_code}: {create_response.text}"
        
        create_data = create_response.json()
        assert "message" in create_data, "Response should contain 'message' field"
        assert "path" in create_data, "Response should contain 'path' field"
        assert create_data["path"] == test_file_path, f"Expected path '{test_file_path}', got {create_data['path']}"
        print(f"✓ File created: {test_file_path}")
        
        # Verify file exists by reading it
        read_response = api_client.get(f"{BASE_URL}/api/files/read?path={test_file_path}")
        assert read_response.status_code == 200, f"Expected 200, got {read_response.status_code}: {read_response.text}"
        
        read_data = read_response.json()
        assert read_data["content"] == test_content, "File content should match what was written"
        assert read_data["name"] == "TEST_new_file.txt", "Filename should match"
        print(f"✓ File verified by reading: content matches")

    def test_create_directory_and_verify(self, api_client):
        """Test POST /api/files/mkdir creates directory and verify it exists"""
        test_dir_path = "/tmp/TEST_new_directory"
        
        # Create directory
        create_response = api_client.post(
            f"{BASE_URL}/api/files/mkdir",
            json={"path": test_dir_path}
        )
        assert create_response.status_code == 200, f"Expected 200, got {create_response.status_code}: {create_response.text}"
        
        create_data = create_response.json()
        assert "message" in create_data, "Response should contain 'message' field"
        assert "path" in create_data, "Response should contain 'path' field"
        assert create_data["path"] == test_dir_path, f"Expected path '{test_dir_path}', got {create_data['path']}"
        print(f"✓ Directory created: {test_dir_path}")
        
        # Verify directory exists by listing /tmp
        list_response = api_client.get(f"{BASE_URL}/api/files?path=/tmp")
        assert list_response.status_code == 200, f"Expected 200, got {list_response.status_code}"
        
        list_data = list_response.json()
        item_names = [item["name"] for item in list_data["items"]]
        assert "TEST_new_directory" in item_names, "Created directory should appear in /tmp listing"
        
        dir_item = next((item for item in list_data["items"] if item["name"] == "TEST_new_directory"), None)
        assert dir_item is not None, "Directory item should exist"
        assert dir_item["is_dir"] is True, "Item should be a directory"
        print(f"✓ Directory verified by listing: is_dir=True")

    def test_delete_file_and_verify(self, api_client):
        """Test DELETE /api/files deletes a file and verify it's gone"""
        test_file_path = "/tmp/TEST_file_to_delete.txt"
        
        # Create file first
        api_client.post(
            f"{BASE_URL}/api/files/write",
            json={"path": test_file_path, "content": "This file will be deleted"}
        )
        
        # Verify file exists
        read_response = api_client.get(f"{BASE_URL}/api/files/read?path={test_file_path}")
        assert read_response.status_code == 200, "File should exist before deletion"
        print(f"✓ File exists before deletion")
        
        # Delete file
        delete_response = api_client.delete(f"{BASE_URL}/api/files?path={test_file_path}")
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
        
        delete_data = delete_response.json()
        assert "message" in delete_data, "Response should contain 'message' field"
        print(f"✓ File deleted: {test_file_path}")
        
        # Verify file is gone (should return 404)
        verify_response = api_client.get(f"{BASE_URL}/api/files/read?path={test_file_path}")
        assert verify_response.status_code == 404, f"Expected 404 after deletion, got {verify_response.status_code}"
        print(f"✓ File verified deleted: returns 404")

    def test_parent_navigation_with_dotdot(self, api_client):
        """Test GET /api/files?path=/ goes back to root with '..' parent navigation"""
        # First, navigate to /app/backend
        backend_response = api_client.get(f"{BASE_URL}/api/files?path=/app/backend")
        assert backend_response.status_code == 200, f"Expected 200, got {backend_response.status_code}"
        
        backend_data = backend_response.json()
        assert "parent" in backend_data, "Response should contain 'parent' field"
        parent_path = backend_data["parent"]
        assert parent_path == "/app", f"Parent of /app/backend should be /app, got {parent_path}"
        print(f"✓ /app/backend has parent: {parent_path}")
        
        # Navigate to parent (/app)
        parent_response = api_client.get(f"{BASE_URL}/api/files?path={parent_path}")
        assert parent_response.status_code == 200, f"Expected 200, got {parent_response.status_code}"
        
        parent_data = parent_response.json()
        assert parent_data["path"] == "/app", "Parent path should be /app"
        assert parent_data["parent"] == "/", "Parent of /app should be root /"
        print(f"✓ Navigated to parent: {parent_data['path']}")
        
        # Navigate to root (/)
        root_response = api_client.get(f"{BASE_URL}/api/files?path=/")
        assert root_response.status_code == 200, f"Expected 200, got {root_response.status_code}"
        
        root_data = root_response.json()
        assert root_data["path"] == "/", "Should be at root"
        assert root_data["parent"] is None, "Root should have no parent (null)"
        print(f"✓ Reached root: parent=None")


class TestTerminalSessionPersistence:
    """Session persistence endpoint: POST /api/terminal/save-session"""

    def test_save_terminal_session(self, api_client):
        """Test POST /api/terminal/save-session saves terminal session"""
        # First, send a command to terminal to ensure there's content
        api_client.post(f"{BASE_URL}/api/terminal/execute", json={"command": "echo 'SESSION_SAVE_TEST'\n"})
        time.sleep(0.5)  # Wait for command to execute
        
        # Save session
        save_response = api_client.post(f"{BASE_URL}/api/terminal/save-session")
        assert save_response.status_code == 200, f"Expected 200, got {save_response.status_code}: {save_response.text}"
        
        save_data = save_response.json()
        assert "message" in save_data, "Response should contain 'message' field"
        assert "saved" in save_data["message"].lower() or "session" in save_data["message"].lower(), \
            f"Message should indicate save: {save_data['message']}"
        print(f"✓ Terminal session saved: {save_data['message']}")
