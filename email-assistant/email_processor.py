"""
Email processing utilities for parsing and managing emails.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from email_models import Email, EmailAnalysis, EmailSummary, EmailAgentConfig
from email_agents import EmailCategorizationAgent


class EmailProcessor:
    """Main email processing and management class."""
    
    def __init__(self, config: EmailAgentConfig):
        self.config = config
        self.console = Console()
        self.categorization_agent = EmailCategorizationAgent(config)
        self.emails: List[Email] = []
        self.analyses: Dict[str, EmailAnalysis] = {}
    
    def load_emails_from_json(self, file_path: str) -> List[Email]:
        """Load emails from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            emails = []
            for email_data in data:
                # Convert timestamp string to datetime if needed
                if isinstance(email_data.get('timestamp'), str):
                    email_data['timestamp'] = datetime.fromisoformat(email_data['timestamp'])
                
                email = Email(**email_data)
                emails.append(email)
            
            self.emails = emails
            self.console.print(f"[green]Loaded {len(emails)} emails from {file_path}[/green]")
            return emails
            
        except Exception as e:
            self.console.print(f"[red]Error loading emails: {e}[/red]")
            return []
    
    def load_emails_from_csv(self, file_path: str) -> List[Email]:
        """Load emails from a CSV file."""
        try:
            df = pd.read_csv(file_path)
            emails = []
            
            for _, row in df.iterrows():
                email_data = {
                    'id': str(uuid.uuid4()),
                    'subject': str(row.get('subject', '')),
                    'sender': str(row.get('sender', '')),
                    'recipient': str(row.get('recipient', '')),
                    'body': str(row.get('body', '')),
                    'timestamp': pd.to_datetime(row.get('timestamp', datetime.now())),
                    'is_read': bool(row.get('is_read', False)),
                    'is_important': bool(row.get('is_important', False))
                }
                
                email = Email(**email_data)
                emails.append(email)
            
            self.emails = emails
            self.console.print(f"[green]Loaded {len(emails)} emails from {file_path}[/green]")
            return emails
            
        except Exception as e:
            self.console.print(f"[red]Error loading emails from CSV: {e}[/red]")
            return []
    
    def create_sample_emails(self) -> List[Email]:
        """Create sample emails for testing."""
        sample_emails = [
            Email(
                id=str(uuid.uuid4()),
                subject="URGENT: Project deadline tomorrow",
                sender="boss@company.com",
                recipient="you@company.com",
                body="Hi, we need to finish the quarterly report by tomorrow. This is critical for the board meeting. Please prioritize this task.",
                timestamp=datetime.now(),
                is_read=False
            ),
            Email(
                id=str(uuid.uuid4()),
                subject="Happy Birthday!",
                sender="mom@family.com",
                recipient="you@personal.com",
                body="Happy birthday, sweetie! Hope you have a wonderful day. Love, Mom",
                timestamp=datetime.now(),
                is_read=False
            ),
            Email(
                id=str(uuid.uuid4()),
                subject="Your order has been shipped",
                sender="noreply@amazon.com",
                recipient="you@personal.com",
                body="Your order #12345 has been shipped and will arrive tomorrow. Track your package here: [link]",
                timestamp=datetime.now(),
                is_read=True
            ),
            Email(
                id=str(uuid.uuid4()),
                subject="Meeting invitation: Weekly standup",
                sender="calendar@company.com",
                recipient="you@company.com",
                body="You have been invited to a meeting: Weekly standup on Monday at 9 AM. Location: Conference Room A.",
                timestamp=datetime.now(),
                is_read=False
            ),
            Email(
                id=str(uuid.uuid4()),
                subject="Your bank statement is ready",
                sender="statements@bank.com",
                recipient="you@personal.com",
                body="Your monthly bank statement is now available. Please log in to view your account summary.",
                timestamp=datetime.now(),
                is_read=False
            ),
            Email(
                id=str(uuid.uuid4()),
                subject="50% OFF - Limited Time Offer!",
                sender="deals@store.com",
                recipient="you@personal.com",
                body="Don't miss out on our biggest sale of the year! Get 50% off everything in our store. Use code SAVE50 at checkout.",
                timestamp=datetime.now(),
                is_read=False
            )
        ]
        
        self.emails = sample_emails
        self.console.print(f"[green]Created {len(sample_emails)} sample emails[/green]")
        return sample_emails
    
    def process_emails(self, batch_size: Optional[int] = None) -> Dict[str, EmailAnalysis]:
        """Process all emails through the categorization agent."""
        if not self.emails:
            self.console.print("[yellow]No emails to process[/yellow]")
            return {}
        
        batch_size = batch_size or self.config.max_emails_per_batch
        analyses = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Processing emails...", total=len(self.emails))
            
            for i in range(0, len(self.emails), batch_size):
                batch = self.emails[i:i + batch_size]
                
                for email in batch:
                    analysis = self.categorization_agent.analyze_email(email)
                    analyses[email.id] = analysis
                    
                    # Update email with analysis results
                    email.category = analysis.category
                    email.priority = analysis.priority
                    email.suggested_action = analysis.suggested_action
                    email.confidence_score = analysis.confidence_score
                    
                    progress.advance(task)
        
        self.analyses = analyses
        self.console.print(f"[green]Processed {len(analyses)} emails[/green]")
        return analyses
    
    def get_inbox_summary(self) -> EmailSummary:
        """Generate a comprehensive inbox summary."""
        if not self.emails:
            return EmailSummary(
                total_emails=0,
                unread_count=0,
                urgent_count=0,
                category_breakdown={},
                priority_breakdown={},
                action_breakdown={},
                top_senders=[],
                recent_emails=[],
                suggested_actions=[]
            )
        
        # Basic counts
        total_emails = len(self.emails)
        unread_count = sum(1 for email in self.emails if not email.is_read)
        urgent_count = sum(1 for email in self.emails if email.priority == "high")
        
        # Category breakdown
        category_breakdown = {}
        for email in self.emails:
            if email.category:
                category_breakdown[email.category] = category_breakdown.get(email.category, 0) + 1
        
        # Priority breakdown
        priority_breakdown = {}
        for email in self.emails:
            if email.priority:
                priority_breakdown[email.priority] = priority_breakdown.get(email.priority, 0) + 1
        
        # Action breakdown
        action_breakdown = {}
        for email in self.emails:
            if email.suggested_action:
                action_breakdown[email.suggested_action] = action_breakdown.get(email.suggested_action, 0) + 1
        
        # Top senders
        sender_counts = {}
        for email in self.emails:
            sender_counts[email.sender] = sender_counts.get(email.sender, 0) + 1
        
        top_senders = [
            {"sender": sender, "count": count}
            for sender, count in sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Recent emails (last 5)
        recent_emails = sorted(self.emails, key=lambda x: x.timestamp, reverse=True)[:5]
        
        # Suggested actions
        suggested_actions = []
        for email in self.emails:
            if email.suggested_action and email.suggested_action != "ignore":
                suggested_actions.append({
                    "email_id": email.id,
                    "subject": email.subject,
                    "sender": email.sender,
                    "action": email.suggested_action,
                    "priority": email.priority
                })
        
        return EmailSummary(
            total_emails=total_emails,
            unread_count=unread_count,
            urgent_count=urgent_count,
            category_breakdown=category_breakdown,
            priority_breakdown=priority_breakdown,
            action_breakdown=action_breakdown,
            top_senders=top_senders,
            recent_emails=recent_emails,
            suggested_actions=suggested_actions
        )
    
    def display_inbox_summary(self):
        """Display a rich inbox summary."""
        summary = self.get_inbox_summary()
        
        # Main stats panel
        stats_text = f"""
        📧 Total Emails: {summary.total_emails}
        📬 Unread: {summary.unread_count}
        ⚠️  Urgent: {summary.urgent_count}
        """
        
        self.console.print(Panel(stats_text, title="📊 Inbox Overview", border_style="blue"))
        
        # Category breakdown table
        if summary.category_breakdown:
            category_table = Table(title="📂 Categories")
            category_table.add_column("Category", style="cyan")
            category_table.add_column("Count", style="magenta")
            
            for category, count in summary.category_breakdown.items():
                category_table.add_row(category.value, str(count))
            
            self.console.print(category_table)
        
        # Priority breakdown table
        if summary.priority_breakdown:
            priority_table = Table(title="⚡ Priorities")
            priority_table.add_column("Priority", style="cyan")
            priority_table.add_column("Count", style="magenta")
            
            for priority, count in summary.priority_breakdown.items():
                priority_table.add_row(priority.value, str(count))
            
            self.console.print(priority_table)
        
        # Action breakdown table
        if summary.action_breakdown:
            action_table = Table(title="🎯 Suggested Actions")
            action_table.add_column("Action", style="cyan")
            action_table.add_column("Count", style="magenta")
            
            for action, count in summary.action_breakdown.items():
                action_table.add_row(action.value, str(count))
            
            self.console.print(action_table)
        
        # Top senders
        if summary.top_senders:
            sender_table = Table(title="👥 Top Senders")
            sender_table.add_column("Sender", style="cyan")
            sender_table.add_column("Count", style="magenta")
            
            for sender_info in summary.top_senders:
                sender_table.add_row(sender_info["sender"], str(sender_info["count"]))
            
            self.console.print(sender_table)
    
    def display_emails(self, limit: int = 10, category: Optional[str] = None, priority: Optional[str] = None):
        """Display emails in a table format."""
        filtered_emails = self.emails
        
        if category:
            filtered_emails = [e for e in filtered_emails if e.category and e.category.value == category]
        
        if priority:
            filtered_emails = [e for e in filtered_emails if e.priority and e.priority.value == priority]
        
        # Sort by timestamp (newest first)
        filtered_emails = sorted(filtered_emails, key=lambda x: x.timestamp, reverse=True)
        
        # Limit results
        filtered_emails = filtered_emails[:limit]
        
        if not filtered_emails:
            self.console.print("[yellow]No emails found matching criteria[/yellow]")
            return
        
        # Create table
        table = Table(title=f"📧 Emails ({len(filtered_emails)} shown)")
        table.add_column("Subject", style="cyan", max_width=30)
        table.add_column("Sender", style="green", max_width=25)
        table.add_column("Category", style="magenta")
        table.add_column("Priority", style="red")
        table.add_column("Action", style="yellow")
        table.add_column("Read", style="blue")
        
        for email in filtered_emails:
            read_status = "✓" if email.is_read else "✗"
            category_str = email.category.value if email.category else "Unknown"
            priority_str = email.priority.value if email.priority else "Unknown"
            action_str = email.suggested_action.value if email.suggested_action else "Unknown"
            
            table.add_row(
                email.subject[:30] + "..." if len(email.subject) > 30 else email.subject,
                email.sender[:25] + "..." if len(email.sender) > 25 else email.sender,
                category_str,
                priority_str,
                action_str,
                read_status
            )
        
        self.console.print(table)
    
    def save_analyses(self, file_path: str):
        """Save email analyses to a JSON file."""
        try:
            analyses_data = {
                email_id: {
                    "email_id": analysis.email_id,
                    "category": analysis.category.value,
                    "priority": analysis.priority.value,
                    "suggested_action": analysis.suggested_action.value,
                    "confidence_score": analysis.confidence_score,
                    "key_topics": analysis.key_topics,
                    "sentiment": analysis.sentiment,
                    "urgency_indicators": analysis.urgency_indicators,
                    "suggested_reply_tone": analysis.suggested_reply_tone,
                    "estimated_response_time": analysis.estimated_response_time
                }
                for email_id, analysis in self.analyses.items()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(analyses_data, f, indent=2, ensure_ascii=False)
            
            self.console.print(f"[green]Saved analyses to {file_path}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error saving analyses: {e}[/red]")
