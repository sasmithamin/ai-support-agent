"""
Test the support agent with various queries
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.support_agent import get_support_agent
from src.db.database import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Test queries
TEST_QUERIES = [
    "I forgot my password and can't log in",
    "How do I reset my password?",
    "I'm being charged twice on my credit card",
    "What are your subscription plans and pricing?",
    "My account is locked after too many failed attempts",
    "How do I export my data?",
    "I want to cancel my subscription",
    "Is there a mobile app available?",
    "How secure is my data on your platform?",
    "I'm getting an 'invalid username or password' error"
]


async def test_agent():
    """Test the support agent with sample queries"""
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized\n")
        
        # Get support agent
        agent = get_support_agent()
        logger.info("Support agent initialized\n")
        
        # Test each query
        for i, query in enumerate(TEST_QUERIES, 1):
            print("=" * 80)
            print(f"\n🧪 TEST {i}/{len(TEST_QUERIES)}")
            print(f"📝 Query: {query}\n")
            
            # Process message
            result = agent.process_message(
                user_message=query,
                user_id=f"test_user_{i}"
            )
            
            # Display results
            print(f"🤖 Response:\n{result['response']}\n")
            
            print(f"😊 Sentiment: {result['sentiment']['sentiment']} "
                  f"(score: {result['sentiment']['score']:.2f}, "
                  f"urgency: {result['sentiment']['urgency']})")
            
            print(f"💪 Confidence: {result['confidence']:.1%}")
            
            print(f"🚨 Escalation: {'YES' if result['escalation']['should_escalate'] else 'NO'}")
            if result['escalation']['should_escalate']:
                print(f"   Reason: {result['escalation']['reason']}")
                print(f"   Priority: {result['escalation']['priority']}")
            
            if result['tools_used']:
                print(f"🔧 Tools Used: {', '.join(result['tools_used'])}")
            
            print()
            
            # Pause between tests
            if i < len(TEST_QUERIES):
                await asyncio.sleep(1)
        
        print("=" * 80)
        print("\n✅ All tests completed!")
        
        # Clear conversation history for next run
        agent.clear_history()
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)


async def interactive_mode():
    """Interactive testing mode"""
    try:
        await init_db()
        agent = get_support_agent()
        
        print("\n" + "=" * 80)
        print("🤖 AI SUPPORT AGENT - Interactive Mode")
        print("=" * 80)
        print("\nType your questions (or 'quit' to exit, 'clear' to reset conversation)\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                agent.clear_history()
                print("🔄 Conversation history cleared\n")
                continue
            
            if not user_input:
                continue
            
            # Process message
            result = agent.process_message(user_input)
            
            # Display response
            print(f"\n🤖 Agent: {result['response']}\n")
            
            # Show metadata
            print(f"   [Sentiment: {result['sentiment']['sentiment']}, "
                  f"Confidence: {result['confidence']:.0%}, "
                  f"Escalate: {'Yes' if result['escalation']['should_escalate'] else 'No'}]\n")
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the AI support agent")
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        asyncio.run(interactive_mode())
    else:
        asyncio.run(test_agent())