"""
Testing utilities and sample requests for MetaDoc API

This file contains helper functions and example requests for testing
the MetaDoc API endpoints during development.
"""

import requests
import json
import os
from typing import Dict, Optional

class MetaDocAPITester:
    """Helper class for testing MetaDoc API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session_token: Optional[str] = None
        self.session = requests.Session()
    
    def _headers(self) -> Dict[str, str]:
        """Get headers with authentication if available"""
        headers = {'Content-Type': 'application/json'}
        if self.session_token:
            headers['Authorization'] = f'Bearer {self.session_token}'
        return headers
    
    def get_auth_url(self) -> str:
        """Get Google OAuth authentication URL"""
        response = self.session.get(f'{self.base_url}/api/v1/auth/login')
        if response.status_code == 200:
            data = response.json()
            return data.get('auth_url', '')
        return ''
    
    def validate_session(self, token: str) -> bool:
        """Validate a session token"""
        response = self.session.post(
            f'{self.base_url}/api/v1/auth/validate',
            json={'session_token': token}
        )
        
        if response.status_code == 200:
            self.session_token = token
            return True
        return False
    
    def upload_file(self, file_path: str, student_name: str = "Test Student", 
                   student_email: str = "test@example.com") -> Dict:
        """Upload a DOCX file for analysis"""
        if not self.session_token:
            raise ValueError("Authentication required. Call validate_session() first.")
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'student_name': student_name,
                'student_email': student_email
            }
            
            headers = {'Authorization': f'Bearer {self.session_token}'}
            
            response = self.session.post(
                f'{self.base_url}/api/v1/submission/upload',
                files=files,
                data=data,
                headers=headers
            )
        
        return response.json()
    
    def submit_drive_link(self, drive_link: str, student_name: str = "Test Student") -> Dict:
        """Submit a Google Drive link for analysis"""
        response = self.session.post(
            f'{self.base_url}/api/v1/submission/drive-link',
            json={
                'drive_link': drive_link,
                'student_name': student_name
            },
            headers=self._headers()
        )
        return response.json()
    
    def get_submission_status(self, job_id: str) -> Dict:
        """Get submission status by job ID"""
        response = self.session.get(
            f'{self.base_url}/api/v1/submission/status/{job_id}'
        )
        return response.json()
    
    def analyze_metadata(self, submission_id: str) -> Dict:
        """Start metadata analysis for a submission"""
        response = self.session.post(
            f'{self.base_url}/api/v1/metadata/analyze/{submission_id}',
            headers=self._headers()
        )
        return response.json()
    
    def analyze_insights(self, submission_id: str) -> Dict:
        """Generate heuristic insights for a submission"""
        response = self.session.post(
            f'{self.base_url}/api/v1/insights/analyze/{submission_id}',
            headers=self._headers()
        )
        return response.json()
    
    def analyze_nlp(self, submission_id: str, enable_ai: bool = False) -> Dict:
        """Run NLP analysis on a submission"""
        response = self.session.post(
            f'{self.base_url}/api/v1/nlp/analyze/{submission_id}',
            json={'enable_ai_summary': enable_ai},
            headers=self._headers()
        )
        return response.json()
    
    def get_dashboard_overview(self) -> Dict:
        """Get dashboard overview statistics"""
        response = self.session.get(
            f'{self.base_url}/api/v1/dashboard/overview',
            headers=self._headers()
        )
        return response.json()
    
    def get_submissions(self, **filters) -> Dict:
        """Get submissions list with optional filters"""
        params = {k: v for k, v in filters.items() if v is not None}
        
        response = self.session.get(
            f'{self.base_url}/api/v1/dashboard/submissions',
            params=params,
            headers=self._headers()
        )
        return response.json()
    
    def export_pdf_report(self, submission_ids: list = None, filters: dict = None) -> Dict:
        """Export submissions as PDF report"""
        payload = {}
        if submission_ids:
            payload['submission_ids'] = submission_ids
        if filters:
            payload['filters'] = filters
        
        response = self.session.post(
            f'{self.base_url}/api/v1/reports/export/pdf',
            json=payload,
            headers=self._headers()
        )
        return response.json()
    
    def create_deadline(self, title: str, deadline_datetime: str, 
                       course_code: str = None, description: str = None) -> Dict:
        """Create a new deadline"""
        payload = {
            'title': title,
            'deadline_datetime': deadline_datetime
        }
        if course_code:
            payload['course_code'] = course_code
        if description:
            payload['description'] = description
        
        response = self.session.post(
            f'{self.base_url}/api/v1/dashboard/deadlines',
            json=payload,
            headers=self._headers()
        )
        return response.json()

def run_complete_workflow_test():
    """Run a complete test workflow"""
    tester = MetaDocAPITester()
    
    print("🧪 MetaDoc API Test Workflow")
    print("=" * 50)
    
    # Step 1: Get auth URL
    print("1. Getting authentication URL...")
    auth_url = tester.get_auth_url()
    if auth_url:
        print(f"✅ Auth URL: {auth_url[:50]}...")
        print("   → Complete authentication manually and get session token")
    else:
        print("❌ Failed to get auth URL")
        return
    
    # Note: In real testing, you would complete OAuth flow and get token
    token = input("\n📋 Enter your session token after authentication: ").strip()
    
    if not tester.validate_session(token):
        print("❌ Invalid session token")
        return
    
    print("✅ Authentication successful!")
    
    # Step 2: Create a deadline
    print("\n2. Creating test deadline...")
    from datetime import datetime, timedelta
    
    future_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
    deadline_result = tester.create_deadline(
        title="Test Assignment",
        deadline_datetime=future_date,
        course_code="TEST101",
        description="Test assignment for API testing"
    )
    
    if 'error' not in deadline_result:
        print("✅ Deadline created successfully")
        deadline_id = deadline_result.get('deadline', {}).get('id')
    else:
        print(f"❌ Deadline creation failed: {deadline_result.get('error')}")
        deadline_id = None
    
    # Step 3: Upload test file (if available)
    test_file_path = input("\n📄 Enter path to a test DOCX file (or press Enter to skip): ").strip()
    
    if test_file_path and os.path.exists(test_file_path):
        print(f"3. Uploading file: {os.path.basename(test_file_path)}")
        
        try:
            upload_result = tester.upload_file(test_file_path, "Test Student", "test@student.com")
            
            if 'error' not in upload_result:
                print("✅ File uploaded successfully")
                job_id = upload_result.get('job_id')
                submission_id = upload_result.get('submission_id')
                
                # Step 4: Check status
                print(f"\n4. Checking submission status...")
                status = tester.get_submission_status(job_id)
                print(f"   Status: {status.get('status', 'Unknown')}")
                
                # Step 5: Run analysis pipeline
                if submission_id:
                    print(f"\n5. Running analysis pipeline...")
                    
                    # Metadata analysis
                    print("   - Running metadata analysis...")
                    metadata_result = tester.analyze_metadata(submission_id)
                    if 'error' not in metadata_result:
                        print("     ✅ Metadata analysis complete")
                    else:
                        print(f"     ❌ Metadata analysis failed: {metadata_result.get('error')}")
                    
                    # Insights analysis
                    print("   - Generating heuristic insights...")
                    insights_result = tester.analyze_insights(submission_id)
                    if 'error' not in insights_result:
                        print("     ✅ Insights analysis complete")
                    else:
                        print(f"     ❌ Insights analysis failed: {insights_result.get('error')}")
                    
                    # NLP analysis
                    print("   - Running NLP analysis...")
                    nlp_result = tester.analyze_nlp(submission_id, enable_ai=False)
                    if 'error' not in nlp_result:
                        print("     ✅ NLP analysis complete")
                    else:
                        print(f"     ❌ NLP analysis failed: {nlp_result.get('error')}")
                    
                    # Step 6: Get dashboard overview
                    print(f"\n6. Getting dashboard overview...")
                    overview = tester.get_dashboard_overview()
                    if 'error' not in overview:
                        stats = overview.get('submission_statistics', {})
                        print(f"   Total submissions: {stats.get('total', 0)}")
                        print(f"   Completed: {stats.get('completed', 0)}")
                        print("   ✅ Dashboard data retrieved")
                    else:
                        print(f"   ❌ Dashboard error: {overview.get('error')}")
                    
                    # Step 7: Export report
                    print(f"\n7. Exporting PDF report...")
                    export_result = tester.export_pdf_report(submission_ids=[submission_id])
                    if 'error' not in export_result:
                        print("   ✅ PDF report generated")
                        print(f"   Export ID: {export_result.get('export_id')}")
                    else:
                        print(f"   ❌ Export failed: {export_result.get('error')}")
            
            else:
                print(f"❌ File upload failed: {upload_result.get('error')}")
        
        except Exception as e:
            print(f"❌ File upload error: {e}")
    
    else:
        print("⏭️ Skipping file upload test")
    
    print("\n" + "=" * 50)
    print("✅ Test workflow completed!")
    print("📊 Check your dashboard at the frontend for results")

if __name__ == '__main__':
    # Run the complete test workflow
    run_complete_workflow_test()