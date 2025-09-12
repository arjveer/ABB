#!/usr/bin/env python3
"""
Demo of the Email Assistant without requiring OpenAI API key.
Shows the structure and features of the system.
"""

import json
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Mock data for demonstration
SAMPLE_EMAILS = [
    {
        "id": "email-001",
        "subject": "URGENT: Project deadline tomorrow",
        "sender": "boss@company.com",
        "recipient": "you@company.com",
        "body": "Hi, we need to finish the quarterly report by tomorrow. This is critical for the board meeting. Please prioritize this task.",
        "timestamp": "2024-01-15T09:30:00",
        "is_read": False,
        "is_important": True,
        "category": "urgent",
        "priority": "high",
        "suggested_action": "reply",
        "confidence_score": 0.95,
        "sentiment": "neutral",
        "key_topics": ["deadline", "quarterly report", "board meeting"],
        "urgency_indicators": ["urgent", "tomorrow", "critical"]
    },
    {
        "id": "email-002",
        "subject": "Happy Birthday!",
        "sender": "mom@family.com",
        "recipient": "you@personal.com",
        "body": "Happy birthday, sweetie! Hope you have a wonderful day. We're so proud of you. Love, Mom and Dad",
        "timestamp": "2024-01-15T08:00:00",
        "is_read": False,
        "is_important": False,
        "category": "personal",
        "priority": "medium",
        "suggested_action": "reply",
        "confidence_score": 0.88,
        "sentiment": "positive",
        "key_topics": ["birthday", "family", "celebration"],
        "urgency_indicators": []
    },
    {
        "id": "email-003",
        "subject": "Your order has been shipped",
        "sender": "noreply@amazon.com",
        "recipient": "you@personal.com",
        "body": "Your order #12345 has been shipped and will arrive tomorrow. Track your package here: https://amazon.com/track/12345",
        "timestamp": "2024-01-15T07:45:00",
        "is_read": True,
        "is_important": False,
        "category": "promotional",
        "priority": "low",
        "suggested_action": "archive",
        "confidence_score": 0.92,
        "sentiment": "neutral",
        "key_topics": ["shipping", "order", "delivery"],
        "urgency_indicators": []
    },
    {
        "id": "email-004",
        "subject": "Meeting invitation: Weekly standup",
        "sender": "calendar@company.com",
        "recipient": "you@company.com",
        "body": "You have been invited to a meeting: Weekly standup on Monday at 9 AM. Location: Conference Room A.",
        "timestamp": "2024-01-15T07:30:00",
        "is_read": False,
        "is_important": False,
        "category": "work",
        "priority": "medium",
        "suggested_action": "schedule",
        "confidence_score": 0.85,
        "sentiment": "neutral",
        "key_topics": ["meeting", "standup", "calendar"],
        "urgency_indicators": []
    },
    {
        "id": "email-005",
        "subject": "Your bank statement is ready",
        "sender": "statements@bank.com",
        "recipient": "you@personal.com",
        "body": "Your monthly bank statement is now available. Please log in to view your account summary.",
        "timestamp": "2024-01-15T06:00:00",
        "is_read": False,
        "is_important": True,
        "category": "financial",
        "priority": "medium",
        "suggested_action": "flag",
        "confidence_score": 0.90,
        "sentiment": "neutral",
        "key_topics": ["bank statement", "account", "financial"],
        "urgency_indicators": []
    },
    {
        "id": "email-006",
        "subject": "50% OFF - Limited Time Offer!",
        "sender": "deals@store.com",
        "recipient": "you@personal.com",
        "body": "Don't miss out on our biggest sale of the year! Get 50% off everything in our store. Use code SAVE50 at checkout.",
        "timestamp": "2024-01-15T05:30:00",
        "is_read": False,
        "is_important": False,
        "category": "promotional",
        "priority": "low",
        "suggested_action": "delete",
        "confidence_score": 0.94,
        "sentiment": "positive",
        "key_topics": ["sale", "discount", "offer"],
        "urgency_indicators": []
    }
]

SAMPLE_DRAFT = {
    "subject": "Meeting Request: Q4 Project Discussion",
    "recipient": "colleague@company.com",
    "body": """Hi [Colleague Name],

I hope this email finds you well. I would like to schedule a meeting to discuss our Q4 project deliverables and timeline.

Given the upcoming deadline and the complexity of the tasks ahead, I believe it would be beneficial for us to align on our approach and ensure we're both on the same page regarding expectations and deliverables.

Would you be available for a 30-minute meeting sometime this week? I'm flexible with timing and can work around your schedule.

Please let me know what works best for you, and I'll send out a calendar invitation.

Best regards,
[Your Name]""",
    "tone": "professional",
    "purpose": "Request a meeting to discuss the quarterly project"
}


def display_inbox_summary(emails):
    """Display inbox summary with mock data."""
    console = Console()
    
    # Calculate stats
    total_emails = len(emails)
    unread_count = sum(1 for email in emails if not email["is_read"])
    urgent_count = sum(1 for email in emails if email["priority"] == "high")
    
    # Category breakdown
    category_breakdown = {}
    for email in emails:
        category = email["category"]
        category_breakdown[category] = category_breakdown.get(category, 0) + 1
    
    # Priority breakdown
    priority_breakdown = {}
    for email in emails:
        priority = email["priority"]
        priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
    
    # Action breakdown
    action_breakdown = {}
    for email in emails:
        action = email["suggested_action"]
        action_breakdown[action] = action_breakdown.get(action, 0) + 1
    
    # Main stats panel
    stats_text = f"""
    📧 Total Emails: {total_emails}
    📬 Unread: {unread_count}
    ⚠️  Urgent: {urgent_count}
    """
    
    console.print(Panel(stats_text, title="📊 Inbox Overview", border_style="blue"))
    
    # Category breakdown table
    if category_breakdown:
        category_table = Table(title="📂 Categories")
        category_table.add_column("Category", style="cyan")
        category_table.add_column("Count", style="magenta")
        
        for category, count in category_breakdown.items():
            category_table.add_row(category.title(), str(count))
        
        console.print(category_table)
    
    # Priority breakdown table
    if priority_breakdown:
        priority_table = Table(title="⚡ Priorities")
        priority_table.add_column("Priority", style="cyan")
        priority_table.add_column("Count", style="magenta")
        
        for priority, count in priority_breakdown.items():
            priority_table.add_row(priority.title(), str(count))
        
        console.print(priority_table)
    
    # Action breakdown table
    if action_breakdown:
        action_table = Table(title="🎯 Suggested Actions")
        action_table.add_column("Action", style="cyan")
        action_table.add_column("Count", style="magenta")
        
        for action, count in action_breakdown.items():
            action_table.add_row(action.title(), str(count))
        
        console.print(action_table)


def display_emails(emails, limit=10):
    """Display emails in a table format."""
    console = Console()
    
    # Sort by timestamp (newest first)
    sorted_emails = sorted(emails, key=lambda x: x["timestamp"], reverse=True)
    
    # Limit results
    display_emails = sorted_emails[:limit]
    
    if not display_emails:
        console.print("[yellow]No emails found[/yellow]")
        return
    
    # Create table
    table = Table(title=f"📧 Emails ({len(display_emails)} shown)")
    table.add_column("Subject", style="cyan", max_width=30)
    table.add_column("Sender", style="green", max_width=25)
    table.add_column("Category", style="magenta")
    table.add_column("Priority", style="red")
    table.add_column("Action", style="yellow")
    table.add_column("Read", style="blue")
    
    for email in display_emails:
        read_status = "✓" if email["is_read"] else "✗"
        category_str = email["category"].title()
        priority_str = email["priority"].title()
        action_str = email["suggested_action"].title()
        
        table.add_row(
            email["subject"][:30] + "..." if len(email["subject"]) > 30 else email["subject"],
            email["sender"][:25] + "..." if len(email["sender"]) > 25 else email["sender"],
            category_str,
            priority_str,
            action_str,
            read_status
        )
    
    console.print(table)


def display_email_analysis(email):
    """Display detailed email analysis."""
    console = Console()
    
    console.print(Panel(
        f"[bold]Category:[/bold] {email['category'].title()}\n"
        f"[bold]Priority:[/bold] {email['priority'].title()}\n"
        f"[bold]Suggested Action:[/bold] {email['suggested_action'].title()}\n"
        f"[bold]Confidence:[/bold] {email['confidence_score']:.2f}\n"
        f"[bold]Sentiment:[/bold] {email['sentiment'].title()}\n"
        f"[bold]Key Topics:[/bold] {', '.join(email['key_topics'])}\n"
        f"[bold]Urgency Indicators:[/bold] {', '.join(email['urgency_indicators']) if email['urgency_indicators'] else 'None'}",
        title="📊 Email Analysis",
        border_style="yellow"
    ))


def display_email_draft(draft):
    """Display generated email draft."""
    console = Console()
    
    console.print(Panel(
        f"[bold]To:[/bold] {draft['recipient']}\n"
        f"[bold]Subject:[/bold] {draft['subject']}\n\n"
        f"[bold]Body:[/bold]\n{draft['body']}",
        title="📧 Generated Email Draft",
        border_style="green"
    ))


def simulate_processing():
    """Simulate email processing with progress bar."""
    console = Console()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing emails...", total=100)
        
        for i in range(100):
            progress.advance(task)
            import time
            time.sleep(0.02)  # Simulate processing time


def main():
    """Run the demo."""
    console = Console()
    
    console.print(Panel(
        "🎬 Email Assistant Demo (No API Required)\n\n"
        "This demo shows the key features of the AI Email Assistant:\n"
        "• Email categorization and analysis\n"
        "• Priority assignment and action suggestions\n"
        "• Email draft generation\n"
        "• Inbox analytics and summaries\n\n"
        "Note: This demo uses mock data. For full functionality, set your OPENAI_API_KEY.",
        title="Demo Mode",
        border_style="blue"
    ))
    
    # Step 1: Load and analyze sample emails
    console.print("\n[bold blue]Step 1: Loading and analyzing sample emails[/bold blue]")
    simulate_processing()
    console.print("[green]✅ Email analysis completed![/green]")
    
    # Step 2: Show inbox summary
    console.print("\n[bold blue]Step 2: Inbox summary and analytics[/bold blue]")
    display_inbox_summary(SAMPLE_EMAILS)
    
    # Step 3: Show email list
    console.print("\n[bold blue]Step 3: Email categorization results[/bold blue]")
    display_emails(SAMPLE_EMAILS, limit=6)
    
    # Step 4: Show detailed analysis
    console.print("\n[bold blue]Step 4: Detailed email analysis[/bold blue]")
    display_email_analysis(SAMPLE_EMAILS[0])  # Show analysis of first email
    
    # Step 5: Show email draft generation
    console.print("\n[bold blue]Step 5: Email draft generation[/bold blue]")
    display_email_draft(SAMPLE_DRAFT)
    
    # Step 6: Show features overview
    console.print("\n[bold blue]Step 6: Key Features Overview[/bold blue]")
    
    features_table = Table(title="🚀 Email Assistant Features")
    features_table.add_column("Feature", style="cyan")
    features_table.add_column("Description", style="white")
    features_table.add_column("Status", style="green")
    
    features = [
        ("Email Categorization", "Automatically categorizes emails into 10+ categories", "✅ Ready"),
        ("Priority Assessment", "Assigns high/medium/low priority based on content", "✅ Ready"),
        ("Action Suggestions", "Recommends reply, forward, archive, delete, etc.", "✅ Ready"),
        ("Sentiment Analysis", "Analyzes email tone and sentiment", "✅ Ready"),
        ("Topic Extraction", "Identifies key topics and themes", "✅ Ready"),
        ("Urgency Detection", "Spots urgency indicators and time-sensitive content", "✅ Ready"),
        ("Draft Generation", "Generates contextually appropriate email drafts", "✅ Ready"),
        ("Tone Control", "Supports professional, casual, and friendly tones", "✅ Ready"),
        ("Reply Generation", "Creates replies to existing emails", "✅ Ready"),
        ("Draft Improvement", "Iteratively improves drafts based on feedback", "✅ Ready"),
        ("Inbox Analytics", "Comprehensive inbox summaries and dashboards", "✅ Ready"),
        ("Visual Interface", "Rich console-based displays with tables and panels", "✅ Ready")
    ]
    
    for feature, description, status in features:
        features_table.add_row(feature, description, status)
    
    console.print(features_table)
    
    # Final message
    console.print("\n[green]Demo completed! 🎉[/green]")
    console.print("\n[bold cyan]To use the full system:[/bold cyan]")
    console.print("1. Set your OPENAI_API_KEY environment variable")
    console.print("2. Run: python main.py interactive")
    console.print("3. Or run: python main.py analyze --sample")
    console.print("4. Or run: python main.py draft 'recipient@email.com' 'purpose'")


if __name__ == "__main__":
    main()
