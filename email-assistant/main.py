"""
Main email assistant application with agent orchestration.
"""

import os
import typer
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from dotenv import load_dotenv

from email_models import EmailAgentConfig
from email_processor import EmailProcessor
from email_agents import EmailDraftAgent

# Load environment variables
load_dotenv()

app = typer.Typer(help="AI-powered Email Assistant")
console = Console()


@app.command()
def analyze(
    input_file: Optional[str] = typer.Option(None, "--input", "-i", help="Input JSON/CSV file with emails"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for analyses"),
    sample: bool = typer.Option(False, "--sample", help="Use sample emails for testing"),
    batch_size: int = typer.Option(50, "--batch-size", help="Number of emails to process per batch")
):
    """Analyze and categorize emails in your inbox."""
    
    # Initialize configuration
    config = EmailAgentConfig()
    
    # Initialize processor
    processor = EmailProcessor(config)
    
    # Load emails
    if sample:
        console.print("[blue]Using sample emails for demonstration[/blue]")
        processor.create_sample_emails()
    elif input_file:
        if input_file.endswith('.json'):
            processor.load_emails_from_json(input_file)
        elif input_file.endswith('.csv'):
            processor.load_emails_from_csv(input_file)
        else:
            console.print("[red]Unsupported file format. Use .json or .csv[/red]")
            return
    else:
        console.print("[red]Please provide an input file or use --sample flag[/red]")
        return
    
    if not processor.emails:
        console.print("[red]No emails loaded[/red]")
        return
    
    # Process emails
    console.print(f"[blue]Processing {len(processor.emails)} emails...[/blue]")
    analyses = processor.process_emails(batch_size)
    
    # Display results
    processor.display_inbox_summary()
    console.print()
    processor.display_emails(limit=10)
    
    # Save analyses if requested
    if output_file:
        processor.save_analyses(output_file)


@app.command()
def draft(
    recipient: str = typer.Argument(..., help="Recipient email address"),
    purpose: str = typer.Argument(..., help="Purpose of the email"),
    tone: str = typer.Option("professional", "--tone", help="Email tone (professional, casual, friendly)"),
    context: Optional[str] = typer.Option(None, "--context", help="Additional context for the email"),
    reply_to: Optional[str] = typer.Option(None, "--reply-to", help="Email ID to reply to")
):
    """Generate an email draft."""
    
    # Initialize configuration
    config = EmailAgentConfig()
    
    # Initialize draft agent
    draft_agent = EmailDraftAgent(config)
    
    # Load original email if replying
    original_email = None
    if reply_to:
        # In a real implementation, you'd load the email from storage
        console.print(f"[yellow]Reply-to functionality requires email storage implementation[/yellow]")
    
    # Generate draft
    console.print(f"[blue]Generating {tone} email draft...[/blue]")
    draft = draft_agent.generate_draft(
        recipient=recipient,
        purpose=purpose,
        tone=tone,
        context=context,
        reply_to=original_email
    )
    
    # Display draft
    console.print(Panel(
        f"[bold]To:[/bold] {draft.recipient}\n"
        f"[bold]Subject:[/bold] {draft.subject}\n\n"
        f"[bold]Body:[/bold]\n{draft.body}",
        title="📧 Email Draft",
        border_style="green"
    ))
    
    # Ask for improvements
    if Confirm.ask("Would you like to improve this draft?"):
        improvements = Prompt.ask("What improvements would you like?")
        improved_draft = draft_agent.improve_draft(draft, improvements)
        
        console.print(Panel(
            f"[bold]To:[/bold] {improved_draft.recipient}\n"
            f"[bold]Subject:[/bold] {improved_draft.subject}\n\n"
            f"[bold]Body:[/bold]\n{improved_draft.body}",
            title="📧 Improved Email Draft",
            border_style="green"
        ))


@app.command()
def interactive():
    """Start interactive email assistant session."""
    
    # Initialize configuration
    config = EmailAgentConfig()
    
    # Initialize agents
    processor = EmailProcessor(config)
    draft_agent = EmailDraftAgent(config)
    
    console.print(Panel(
        "🤖 Welcome to the AI Email Assistant!\n\n"
        "This assistant can help you:\n"
        "• Categorize and analyze your emails\n"
        "• Generate email drafts\n"
        "• Suggest actions for your inbox\n\n"
        "Let's get started!",
        title="Email Assistant",
        border_style="blue"
    ))
    
    # Load sample emails for demo
    processor.create_sample_emails()
    processor.process_emails()
    
    while True:
        console.print("\n[bold cyan]What would you like to do?[/bold cyan]")
        console.print("1. View inbox summary")
        console.print("2. List emails")
        console.print("3. Generate email draft")
        console.print("4. Analyze specific email")
        console.print("5. Exit")
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            processor.display_inbox_summary()
        
        elif choice == "2":
            limit = int(Prompt.ask("How many emails to show?", default="10"))
            processor.display_emails(limit=limit)
        
        elif choice == "3":
            recipient = Prompt.ask("Recipient email")
            purpose = Prompt.ask("Email purpose")
            tone = Prompt.ask("Tone", choices=["professional", "casual", "friendly"], default="professional")
            context = Prompt.ask("Additional context (optional)", default="")
            
            draft = draft_agent.generate_draft(
                recipient=recipient,
                purpose=purpose,
                tone=tone,
                context=context if context else None
            )
            
            console.print(Panel(
                f"[bold]To:[/bold] {draft.recipient}\n"
                f"[bold]Subject:[/bold] {draft.subject}\n\n"
                f"[bold]Body:[/bold]\n{draft.body}",
                title="📧 Email Draft",
                border_style="green"
            ))
        
        elif choice == "4":
            if not processor.analyses:
                console.print("[yellow]No email analyses available[/yellow]")
                continue
            
            # Show email list for selection
            processor.display_emails(limit=5)
            email_id = Prompt.ask("Enter email ID to analyze")
            
            # Find and display analysis
            analysis = processor.analyses.get(email_id)
            if analysis:
                console.print(Panel(
                    f"[bold]Category:[/bold] {analysis.category.value}\n"
                    f"[bold]Priority:[/bold] {analysis.priority.value}\n"
                    f"[bold]Suggested Action:[/bold] {analysis.suggested_action.value}\n"
                    f"[bold]Confidence:[/bold] {analysis.confidence_score:.2f}\n"
                    f"[bold]Sentiment:[/bold] {analysis.sentiment}\n"
                    f"[bold]Key Topics:[/bold] {', '.join(analysis.key_topics)}\n"
                    f"[bold]Urgency Indicators:[/bold] {', '.join(analysis.urgency_indicators)}\n"
                    f"[bold]Suggested Reply Tone:[/bold] {analysis.suggested_reply_tone}\n"
                    f"[bold]Estimated Response Time:[/bold] {analysis.estimated_response_time}",
                    title="📊 Email Analysis",
                    border_style="yellow"
                ))
            else:
                console.print("[red]Email not found[/red]")
        
        elif choice == "5":
            console.print("[green]Goodbye! 👋[/green]")
            break


@app.command()
def demo():
    """Run a demonstration of the email assistant."""
    
    console.print(Panel(
        "🎬 Email Assistant Demo\n\n"
        "This demo will show you the key features of the AI Email Assistant:",
        title="Demo Mode",
        border_style="blue"
    ))
    
    # Initialize configuration
    config = EmailAgentConfig()
    
    # Initialize agents
    processor = EmailProcessor(config)
    draft_agent = EmailDraftAgent(config)
    
    # Step 1: Load and analyze sample emails
    console.print("\n[bold blue]Step 1: Loading and analyzing sample emails[/bold blue]")
    processor.create_sample_emails()
    processor.process_emails()
    processor.display_inbox_summary()
    
    # Step 2: Show email list
    console.print("\n[bold blue]Step 2: Email categorization results[/bold blue]")
    processor.display_emails(limit=6)
    
    # Step 3: Generate email draft
    console.print("\n[bold blue]Step 3: Generating email draft[/bold blue]")
    draft = draft_agent.generate_draft(
        recipient="colleague@company.com",
        purpose="Request a meeting to discuss the quarterly project",
        tone="professional",
        context="Need to align on deliverables and timeline"
    )
    
    console.print(Panel(
        f"[bold]To:[/bold] {draft.recipient}\n"
        f"[bold]Subject:[/bold] {draft.subject}\n\n"
        f"[bold]Body:[/bold]\n{draft.body}",
        title="📧 Generated Email Draft",
        border_style="green"
    ))
    
    # Step 4: Show analysis details
    console.print("\n[bold blue]Step 4: Detailed email analysis[/bold blue]")
    if processor.analyses:
        first_analysis = list(processor.analyses.values())[0]
        console.print(Panel(
            f"[bold]Category:[/bold] {first_analysis.category.value}\n"
            f"[bold]Priority:[/bold] {first_analysis.priority.value}\n"
            f"[bold]Suggested Action:[/bold] {first_analysis.suggested_action.value}\n"
            f"[bold]Confidence:[/bold] {first_analysis.confidence_score:.2f}\n"
            f"[bold]Sentiment:[/bold] {first_analysis.sentiment}\n"
            f"[bold]Key Topics:[/bold] {', '.join(first_analysis.key_topics)}\n"
            f"[bold]Urgency Indicators:[/bold] {', '.join(first_analysis.urgency_indicators)}",
            title="📊 Sample Email Analysis",
            border_style="yellow"
        ))
    
    console.print("\n[green]Demo completed! 🎉[/green]")
    console.print("Use 'email-assistant interactive' to try it yourself!")


if __name__ == "__main__":
    app()
