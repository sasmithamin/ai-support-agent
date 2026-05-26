"""
Load knowledge base documents into vector database
"""
import asyncio
import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.vector_store import get_vector_store
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Sample knowledge base documents
SAMPLE_KNOWLEDGE = [
    {
        "title": "Password Reset Guide",
        "category": "authentication",
        "content": """
How to Reset Your Password:

1. Go to the login page at www.example.com/login
2. Click on "Forgot Password?" link below the login form
3. Enter your registered email address
4. Check your email for a password reset link (check spam folder if not received)
5. Click the reset link in the email (valid for 24 hours)
6. Enter your new password (must be at least 8 characters with letters and numbers)
7. Confirm your new password
8. Click "Reset Password" button
9. You will be redirected to the login page
10. Log in with your new password

Troubleshooting:
- If you don't receive the email within 5 minutes, check your spam folder
- Make sure you're using the email address associated with your account
- If the link has expired, request a new password reset
- For further assistance, contact support@example.com

Password Requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- Special characters are optional but recommended
        """
    },
    {
        "title": "Account Login Issues",
        "category": "authentication",
        "content": """
Common Login Problems and Solutions:

1. "Invalid Username or Password" Error:
   - Double-check your email address for typos
   - Ensure Caps Lock is off
   - Try resetting your password
   - Clear browser cache and cookies

2. "Account Locked" Message:
   - Your account locks after 5 failed login attempts
   - Wait 30 minutes for automatic unlock
   - Or use "Forgot Password" to reset immediately
   - Contact support if locked for over 1 hour

3. Two-Factor Authentication Issues:
   - Ensure your phone has signal/internet
   - Check if code has expired (valid for 5 minutes)
   - Request a new code
   - Use backup codes if available

4. Browser Compatibility:
   - We support Chrome, Firefox, Safari, and Edge (latest 2 versions)
   - Clear cache: Ctrl+Shift+Delete (Chrome/Edge) or Cmd+Shift+Delete (Mac)
   - Try incognito/private mode
   - Disable browser extensions temporarily

5. "Session Expired" Error:
   - You'll be logged out after 2 hours of inactivity
   - Simply log in again
   - Check "Remember Me" to stay logged in for 30 days

Still having issues? Contact support@example.com with:
- Your registered email
- Browser and version
- Error message (screenshot if possible)
- Steps you've already tried
        """
    },
    {
        "title": "Billing and Subscription",
        "category": "billing",
        "content": """
Billing Information:

Subscription Plans:
- Free Plan: $0/month (limited features)
- Basic Plan: $9.99/month
- Pro Plan: $19.99/month
- Enterprise Plan: Custom pricing

Payment Methods Accepted:
- Credit/Debit cards (Visa, MasterCard, American Express)
- PayPal
- Bank transfer (Enterprise only)

Billing Cycle:
- Monthly subscriptions renew on the same date each month
- Annual subscriptions renew yearly with 20% discount
- Billing date can be changed once per year

How to Update Payment Information:
1. Log in to your account
2. Go to Settings > Billing
3. Click "Update Payment Method"
4. Enter new card details
5. Click "Save Changes"

How to Cancel Subscription:
1. Go to Settings > Billing
2. Click "Cancel Subscription"
3. Select reason for cancellation (optional)
4. Confirm cancellation
5. You'll have access until the end of your billing period

Refund Policy:
- 30-day money-back guarantee for new customers
- Refunds processed within 5-7 business days
- Contact billing@example.com for refund requests

Common Billing Issues:
- Payment failed: Update payment method or contact your bank
- Double charged: Contact billing@example.com immediately
- Proration: Upgrading mid-cycle is prorated automatically
- Invoice needed: Download from Settings > Billing > Invoices

For billing questions: billing@example.com
        """
    },
    {
        "title": "Getting Started Guide",
        "category": "onboarding",
        "content": """
Welcome! Getting Started with Our Platform:

Step 1: Create Your Account
- Sign up at www.example.com/signup
- Verify your email address
- Complete your profile

Step 2: Choose Your Plan
- Start with the Free plan to explore
- Upgrade anytime from Settings > Billing
- All plans include 24/7 support

Step 3: Set Up Your Workspace
- Create your first project
- Invite team members (Pro/Enterprise only)
- Customize your dashboard

Step 4: Explore Key Features
- Dashboard: Overview of your activity
- Projects: Organize your work
- Reports: Track progress and metrics
- Settings: Customize your experience

Step 5: Get Help
- Help Center: help.example.com
- Video Tutorials: www.example.com/tutorials
- Community Forum: community.example.com
- Live Chat: Available 24/7 in-app

Quick Tips:
✓ Enable two-factor authentication for security
✓ Download our mobile app for on-the-go access
✓ Set up email notifications for important updates
✓ Join our weekly webinars for tips and tricks

Need assistance? Our support team is here 24/7!
        """
    },
    {
        "title": "Technical Support FAQ",
        "category": "technical",
        "content": """
Frequently Asked Questions - Technical Support:

Q: How do I clear my browser cache?
A: Chrome/Edge: Press Ctrl+Shift+Delete (Cmd+Shift+Delete on Mac)
   Firefox: Press Ctrl+Shift+Delete
   Safari: Preferences > Privacy > Manage Website Data > Remove All

Q: What browsers do you support?
A: We support the latest 2 versions of:
   - Google Chrome
   - Mozilla Firefox
   - Safari (Mac only)
   - Microsoft Edge
   Internet Explorer is not supported.

Q: Is there a mobile app?
A: Yes! Download from:
   - iOS: App Store (search "Example App")
   - Android: Google Play Store
   Minimum iOS 14.0 or Android 8.0 required.

Q: How do I export my data?
A: Go to Settings > Data & Privacy > Export Data
   Choose format (CSV, JSON, or PDF)
   You'll receive an email with download link within 24 hours.

Q: What are your server uptime guarantees?
A: We guarantee 99.9% uptime
   Check status: status.example.com
   Scheduled maintenance: announced 48 hours in advance

Q: How do I report a bug?
A: Click "Report Bug" in app menu
   Or email: bugs@example.com
   Include: screenshots, browser info, steps to reproduce

Q: Do you offer API access?
A: Yes, API available on Pro and Enterprise plans
   Documentation: docs.example.com/api
   Rate limits: 1000 requests/hour (Pro), unlimited (Enterprise)

Q: How secure is my data?
A: - 256-bit SSL encryption
   - SOC 2 Type II certified
   - GDPR and CCPA compliant
   - Regular security audits
   - Daily encrypted backups

Q: What's your data retention policy?
A: Active accounts: Data retained indefinitely
   Deleted accounts: Data deleted after 30 days
   Backups: Retained for 90 days

Still have questions? Contact support@example.com
        """
    },
    {
        "title": "Account Settings and Privacy",
        "category": "account",
        "content": """
Account Management Guide:

Profile Settings:
- Update name, photo, and bio
- Change email address (requires verification)
- Set timezone and language preferences
- Manage notification preferences

Privacy Controls:
- Who can view your profile (Public/Private/Team Only)
- Activity visibility settings
- Data sharing preferences
- Cookie preferences

Security Settings:
- Enable two-factor authentication (highly recommended)
- View active sessions and devices
- Set up backup email and phone number
- Review login history
- Generate backup codes

Email Notifications:
- Daily digest of activity
- Real-time alerts for mentions
- Weekly summary reports
- Marketing emails (opt-in/out)
- Security alerts (always enabled)

Data Management:
- Download your data
- Delete specific content
- Request account deletion
- Data portability (GDPR)

Account Deletion:
⚠️ Warning: This action is permanent and cannot be undone
1. Go to Settings > Account > Delete Account
2. Read the warning message carefully
3. Enter your password to confirm
4. Click "Permanently Delete My Account"
5. You have 30 days to cancel deletion

Privacy Policy: www.example.com/privacy
Terms of Service: www.example.com/terms
Contact: privacy@example.com
        """
    }
]


async def load_knowledge_base():
    """Load knowledge documents into vector database"""
    try:
        logger.info("Loading knowledge base documents...")
        
        vector_store = get_vector_store()
        
        # Prepare documents
        documents = [doc["content"].strip() for doc in SAMPLE_KNOWLEDGE]
        metadatas = [
            {
                "title": doc["title"],
                "category": doc["category"],
                "source": "initial_load"
            }
            for doc in SAMPLE_KNOWLEDGE
        ]
        
        # Add to vector store
        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"✅ Loaded {len(SAMPLE_KNOWLEDGE)} knowledge documents")
        
        # Get stats
        stats = vector_store.get_stats()
        logger.info(f"Vector store stats: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to load knowledge base: {e}", exc_info=True)
        return False


async def reset_knowledge_base():
    """Reset knowledge base - deletes all documents"""
    try:
        logger.warning("⚠️  Resetting knowledge base...")
        
        vector_store = get_vector_store()
        vector_store.delete_collection()
        
        logger.info("✅ Knowledge base reset complete")
        
        # Reinitialize
        from src.rag.vector_store import VectorStore
        global _vector_store
        _vector_store = VectorStore()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Knowledge base reset failed: {e}")
        return False


def load_from_directory(directory_path: str):
    """Load knowledge from a directory of text files"""
    directory = Path(directory_path)
    
    if not directory.exists():
        logger.error(f"Directory not found: {directory_path}")
        return False
    
    try:
        vector_store = get_vector_store()
        
        # Supported file types
        text_files = list(directory.glob("*.txt")) + list(directory.glob("*.md"))
        
        if not text_files:
            logger.warning(f"No .txt or .md files found in {directory_path}")
            return False
        
        documents = []
        metadatas = []
        
        for file_path in text_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                documents.append(content)
                metadatas.append({
                    "title": file_path.stem,
                    "category": "custom",
                    "source": str(file_path)
                })
                
                logger.info(f"Loaded: {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        
        if documents:
            vector_store.add_documents(documents=documents, metadatas=metadatas)
            logger.info(f"✅ Loaded {len(documents)} documents from {directory_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error loading from directory: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Knowledge base loader")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset knowledge base before loading"
    )
    parser.add_argument(
        "--directory",
        type=str,
        help="Load documents from a directory"
    )
    
    args = parser.parse_args()
    
    async def main():
        if args.reset:
            await reset_knowledge_base()
        
        if args.directory:
            load_from_directory(args.directory)
        else:
            await load_knowledge_base()
    
    asyncio.run(main())