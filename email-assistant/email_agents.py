"""
Email processing agents for categorization and draft generation.
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from email_models import (
    Email, EmailDraft, EmailAnalysis, EmailCategory, 
    EmailPriority, EmailAction, EmailAgentConfig
)


class EmailCategorizationAgent:
    """Agent responsible for categorizing and analyzing emails."""
    
    def __init__(self, config: EmailAgentConfig):
        self.config = config
        self.console = Console()
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.openai_client = OpenAI(api_key=api_key)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(config.embedding_model)
        
        # Category classification prompts
        self.category_prompts = {
            EmailCategory.URGENT: "Identify urgent emails requiring immediate attention",
            EmailCategory.WORK: "Classify work-related emails, meetings, projects, and professional communications",
            EmailCategory.PERSONAL: "Identify personal emails from friends, family, and personal matters",
            EmailCategory.PROMOTIONAL: "Detect promotional emails, newsletters, and marketing content",
            EmailCategory.SOCIAL: "Classify social media notifications and social platform emails",
            EmailCategory.FINANCIAL: "Identify financial emails, bills, banking, and investment communications",
            EmailCategory.TRAVEL: "Classify travel-related emails, bookings, and trip information",
            EmailCategory.HEALTH: "Identify health-related emails, medical appointments, and wellness content",
            EmailCategory.EDUCATION: "Classify educational emails, courses, and learning materials",
            EmailCategory.SPAM: "Detect spam, phishing, and suspicious emails"
        }
    
    def analyze_email(self, email: Email) -> EmailAnalysis:
        """Analyze a single email and return comprehensive analysis."""
        try:
            # Prepare email content for analysis
            email_content = f"""
            Subject: {email.subject}
            From: {email.sender}
            Body: {email.body[:1000]}  # Limit body length for analysis
            """
            
            # Get category classification
            category, category_confidence = self._classify_category(email_content)
            
            # Get priority assessment
            priority = self._assess_priority(email_content, category)
            
            # Get suggested action
            action = self._suggest_action(email_content, category, priority)
            
            # Get sentiment analysis
            sentiment = self._analyze_sentiment(email_content)
            
            # Extract key topics
            key_topics = self._extract_key_topics(email_content)
            
            # Get urgency indicators
            urgency_indicators = self._identify_urgency_indicators(email_content)
            
            # Suggest reply tone
            reply_tone = self._suggest_reply_tone(email_content, category, sentiment)
            
            # Estimate response time
            response_time = self._estimate_response_time(category, priority, urgency_indicators)
            
            return EmailAnalysis(
                email_id=email.id,
                category=category,
                priority=priority,
                suggested_action=action,
                confidence_score=category_confidence,
                key_topics=key_topics,
                sentiment=sentiment,
                urgency_indicators=urgency_indicators,
                suggested_reply_tone=reply_tone,
                estimated_response_time=response_time
            )
            
        except Exception as e:
            self.console.print(f"[red]Error analyzing email {email.id}: {e}[/red]")
            return EmailAnalysis(
                email_id=email.id,
                category=EmailCategory.UNKNOWN,
                priority=EmailPriority.LOW,
                suggested_action=EmailAction.IGNORE,
                confidence_score=0.0,
                sentiment="neutral",
                suggested_reply_tone="professional",
                estimated_response_time="unknown"
            )
    
    def _classify_category(self, email_content: str) -> Tuple[EmailCategory, float]:
        """Classify email category using semantic similarity."""
        try:
            # Create embeddings for email content
            email_embedding = self.embedding_model.encode([email_content])
            
            # Create embeddings for category descriptions
            category_descriptions = list(self.category_prompts.values())
            category_embeddings = self.embedding_model.encode(category_descriptions)
            
            # Calculate similarities
            similarities = np.dot(category_embeddings, email_embedding.T).flatten()
            
            # Get best match
            best_idx = np.argmax(similarities)
            best_category = list(self.category_prompts.keys())[best_idx]
            confidence = float(similarities[best_idx])
            
            return best_category, confidence
            
        except Exception as e:
            self.console.print(f"[yellow]Category classification failed: {e}[/yellow]")
            return EmailCategory.UNKNOWN, 0.0
    
    def _assess_priority(self, email_content: str, category: EmailCategory) -> EmailPriority:
        """Assess email priority based on content and category."""
        try:
            prompt = f"""
            Analyze this email and determine its priority level (high, medium, low):
            
            Email Content: {email_content}
            Category: {category.value}
            
            Consider:
            - Urgency indicators (ASAP, urgent, deadline, etc.)
            - Importance of sender
            - Content relevance
            - Time sensitivity
            
            Respond with only: high, medium, or low
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            priority_text = response.choices[0].message.content.strip().lower()
            
            if "high" in priority_text:
                return EmailPriority.HIGH
            elif "medium" in priority_text:
                return EmailPriority.MEDIUM
            else:
                return EmailPriority.LOW
                
        except Exception as e:
            self.console.print(f"[yellow]Priority assessment failed: {e}[/yellow]")
            return EmailPriority.MEDIUM
    
    def _suggest_action(self, email_content: str, category: EmailCategory, priority: EmailPriority) -> EmailAction:
        """Suggest action for the email."""
        try:
            prompt = f"""
            Based on this email, suggest the most appropriate action:
            
            Email Content: {email_content}
            Category: {category.value}
            Priority: {priority.value}
            
            Available actions:
            - reply: Needs a response
            - forward: Should be forwarded to someone else
            - archive: Can be archived
            - delete: Should be deleted
            - schedule: Needs to be scheduled/followed up
            - flag: Important, flag for later
            - ignore: Can be ignored
            
            Respond with only the action name.
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=20
            )
            
            action_text = response.choices[0].message.content.strip().lower()
            
            # Map to enum
            action_mapping = {
                "reply": EmailAction.REPLY,
                "forward": EmailAction.FORWARD,
                "archive": EmailAction.ARCHIVE,
                "delete": EmailAction.DELETE,
                "schedule": EmailAction.SCHEDULE,
                "flag": EmailAction.FLAG,
                "ignore": EmailAction.IGNORE
            }
            
            for key, action in action_mapping.items():
                if key in action_text:
                    return action
            
            return EmailAction.REPLY  # Default action
            
        except Exception as e:
            self.console.print(f"[yellow]Action suggestion failed: {e}[/yellow]")
            return EmailAction.REPLY
    
    def _analyze_sentiment(self, email_content: str) -> str:
        """Analyze email sentiment."""
        try:
            prompt = f"""
            Analyze the sentiment of this email content:
            
            {email_content}
            
            Respond with only: positive, negative, or neutral
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            sentiment = response.choices[0].message.content.strip().lower()
            
            if "positive" in sentiment:
                return "positive"
            elif "negative" in sentiment:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            self.console.print(f"[yellow]Sentiment analysis failed: {e}[/yellow]")
            return "neutral"
    
    def _extract_key_topics(self, email_content: str) -> List[str]:
        """Extract key topics from email content."""
        try:
            prompt = f"""
            Extract the main topics/keywords from this email content:
            
            {email_content}
            
            Return 3-5 key topics as a comma-separated list.
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            
            topics_text = response.choices[0].message.content.strip()
            topics = [topic.strip() for topic in topics_text.split(",")]
            return topics[:5]  # Limit to 5 topics
            
        except Exception as e:
            self.console.print(f"[yellow]Topic extraction failed: {e}[/yellow]")
            return []
    
    def _identify_urgency_indicators(self, email_content: str) -> List[str]:
        """Identify urgency indicators in email content."""
        urgency_keywords = [
            "urgent", "asap", "immediately", "deadline", "expires",
            "critical", "emergency", "rush", "priority", "important",
            "time sensitive", "quick response", "today", "tomorrow"
        ]
        
        content_lower = email_content.lower()
        found_indicators = [keyword for keyword in urgency_keywords if keyword in content_lower]
        
        return found_indicators
    
    def _suggest_reply_tone(self, email_content: str, category: EmailCategory, sentiment: str) -> str:
        """Suggest appropriate tone for reply."""
        if category == EmailCategory.WORK:
            return "professional"
        elif category == EmailCategory.PERSONAL:
            return "friendly"
        elif sentiment == "negative":
            return "diplomatic"
        else:
            return "professional"
    
    def _estimate_response_time(self, category: EmailCategory, priority: EmailPriority, urgency_indicators: List[str]) -> str:
        """Estimate time needed to respond to email."""
        if priority == EmailPriority.HIGH or urgency_indicators:
            return "immediate"
        elif category == EmailCategory.WORK:
            return "within 24 hours"
        elif category == EmailCategory.PERSONAL:
            return "within 2-3 days"
        else:
            return "when convenient"


class EmailDraftAgent:
    """Agent responsible for generating email drafts."""
    
    def __init__(self, config: EmailAgentConfig):
        self.config = config
        self.console = Console()
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.openai_client = OpenAI(api_key=api_key)
    
    def generate_draft(
        self, 
        recipient: str, 
        purpose: str, 
        tone: str = "professional",
        context: Optional[str] = None,
        reply_to: Optional[Email] = None
    ) -> EmailDraft:
        """Generate an email draft based on requirements."""
        try:
            # Build prompt based on whether it's a reply or new email
            if reply_to:
                prompt = self._build_reply_prompt(recipient, purpose, tone, context, reply_to)
            else:
                prompt = self._build_new_email_prompt(recipient, purpose, tone, context)
            
            # Generate email content
            response = self.openai_client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            email_content = response.choices[0].message.content.strip()
            
            # Parse subject and body from response
            subject, body = self._parse_email_content(email_content)
            
            return EmailDraft(
                id=str(uuid.uuid4()),
                subject=subject,
                recipient=recipient,
                body=body,
                tone=tone,
                purpose=purpose
            )
            
        except Exception as e:
            self.console.print(f"[red]Error generating draft: {e}[/red]")
            return EmailDraft(
                id=str(uuid.uuid4()),
                subject="Draft Generation Failed",
                recipient=recipient,
                body=f"Error generating email draft: {e}",
                tone=tone,
                purpose=purpose
            )
    
    def _build_reply_prompt(
        self, 
        recipient: str, 
        purpose: str, 
        tone: str, 
        context: Optional[str], 
        original_email: Email
    ) -> str:
        """Build prompt for replying to an email."""
        return f"""
        Write a {tone} email reply with the following requirements:
        
        Recipient: {recipient}
        Purpose: {purpose}
        Tone: {tone}
        Context: {context or "No additional context provided"}
        
        Original Email:
        Subject: {original_email.subject}
        From: {original_email.sender}
        Body: {original_email.body[:500]}
        
        Format your response as:
        SUBJECT: [Your subject line]
        BODY: [Your email body]
        
        Make sure the reply is appropriate, professional, and addresses the original email appropriately.
        """
    
    def _build_new_email_prompt(
        self, 
        recipient: str, 
        purpose: str, 
        tone: str, 
        context: Optional[str]
    ) -> str:
        """Build prompt for a new email."""
        return f"""
        Write a {tone} email with the following requirements:
        
        Recipient: {recipient}
        Purpose: {purpose}
        Tone: {tone}
        Context: {context or "No additional context provided"}
        
        Format your response as:
        SUBJECT: [Your subject line]
        BODY: [Your email body]
        
        Make sure the email is clear, professional, and achieves the stated purpose.
        """
    
    def _parse_email_content(self, content: str) -> Tuple[str, str]:
        """Parse subject and body from generated content."""
        lines = content.split('\n')
        subject = "No Subject"
        body_lines = []
        
        in_body = False
        
        for line in lines:
            if line.startswith("SUBJECT:"):
                subject = line.replace("SUBJECT:", "").strip()
            elif line.startswith("BODY:"):
                in_body = True
                body_content = line.replace("BODY:", "").strip()
                if body_content:
                    body_lines.append(body_content)
            elif in_body:
                body_lines.append(line)
        
        body = '\n'.join(body_lines).strip()
        if not body:
            body = content  # Fallback to full content
        
        return subject, body
    
    def improve_draft(self, draft: EmailDraft, improvements: str) -> EmailDraft:
        """Improve an existing draft based on feedback."""
        try:
            prompt = f"""
            Improve this email draft based on the requested changes:
            
            Original Draft:
            Subject: {draft.subject}
            Body: {draft.body}
            
            Improvements requested: {improvements}
            
            Format your response as:
            SUBJECT: [Improved subject line]
            BODY: [Improved email body]
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            email_content = response.choices[0].message.content.strip()
            subject, body = self._parse_email_content(email_content)
            
            # Update the draft
            draft.subject = subject
            draft.body = body
            
            return draft
            
        except Exception as e:
            self.console.print(f"[red]Error improving draft: {e}[/red]")
            return draft
