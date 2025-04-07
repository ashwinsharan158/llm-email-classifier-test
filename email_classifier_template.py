# Configuration and imports
import os
import json
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Sample email dataset
sample_emails = [
    {
        "id": "001",
        "from": "angry.customer@example.com",
        "subject": "Broken product received",
        "body": "I received my order #12345 yesterday but it arrived completely damaged. This is unacceptable and I demand a refund immediately. This is the worst customer service I've experienced.",
        "timestamp": "2024-03-15T10:30:00Z"
    },
    {
        "id": "002",
        "from": "curious.shopper@example.com",
        "subject": "Question about product specifications",
        "body": "Hi, I'm interested in buying your premium package but I couldn't find information about whether it's compatible with Mac OS. Could you please clarify this? Thanks!",
        "timestamp": "2024-03-15T11:45:00Z"
    },
    {
        "id": "003",
        "from": "happy.user@example.com",
        "subject": "Amazing customer support",
        "body": "I just wanted to say thank you for the excellent support I received from Sarah on your team. She went above and beyond to help resolve my issue. Keep up the great work!",
        "timestamp": "2024-03-15T13:15:00Z"
    },
    {
        "id": "004",
        "from": "tech.user@example.com",
        "subject": "Need help with installation",
        "body": "I've been trying to install the software for the past hour but keep getting error code 5123. I've already tried restarting my computer and clearing the cache. Please help!",
        "timestamp": "2024-03-15T14:20:00Z"
    },
    {
        "id": "005",
        "from": "business.client@example.com",
        "subject": "Partnership opportunity",
        "body": "Our company is interested in exploring potential partnership opportunities with your organization. Would it be possible to schedule a call next week to discuss this further?",
        "timestamp": "2024-03-15T15:00:00Z"
    },
    # No specific email
    {
        "id": "006",
        "from": "grass@grass.com",
        "subject": "grass",
        "body": "grass grass",
        "timestamp": "2024-03-15T15:00:00Z"
    },
    {
        "id": "007",
        "from": "scammer@escammer.com",
        "subject": "you have won $1000000000",
        "body": "Just send a check for $200 to recieve this money",
        "timestamp": "2024-03-15T15:00:00Z"
    }
]


class EmailProcessor:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initialize the email processor with OpenAI API key."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

        # Define valid categories
        self.valid_categories = {
            "complaint", "inquiry", "feedback",
            "support_request", "other"
        }
        
    def vaildate_email(self, email: Dict) -> bool:
        required_fields = ["id", "from", "subject", "body", "timestamp"]
        for field in required_fields:
            if not field in email or not email[field]:
                logger.error(f"Validation failed: Missing or empty field '{field}' in email {email.get('id', 'unknown')}.")
                return False
        return True
    
    def get_email_subject(self, email: Dict) -> str:
        subject = email.get("subject", "")
        if subject:
            return subject
        else:
            logger.error("Validation Error: Missing subject on email.")
        return
    
    def get_email_body(self, email: Dict) -> str:
        body = email.get("body", "")
        if body:
            return body
        else:
            logger.error("Validation Error: Missing Body on email.")
        return
    
    def get_email_from(self, email: Dict) -> str:
        from_s = email.get("from", "")
        if from_s:
            return from_s
        else:
            logger.error("Validation Error: Missing sender email.")
        return
    
    def classify_email(self, email: Dict) -> Optional[str]:
        """
        Classify an email using LLM.
        Returns the classification category or None if classification fails.
        
        TODO: 
        1. Design and implement the classification prompt
        2. Make the API call with appropriate error handling
        3. Validate and return the classification
        """

        if not self.vaildate_email(email):
            return
        from_s = self.get_email_from(email)
        body = self.get_email_body(email)
        subject = self.get_email_subject(email)

        prompt = f"""
            You are an expert email classifier. Analyze the email details below and assign it to one of the following categories: complaint, inquiry, feedback, support_request, or other.

            Guidelines:
            1. Use "complaint" if the email expresses dissatisfaction, frustration, or reports a problem with a product/service.
            2. Use "inquiry" if the email asks for information or clarification regarding a product, service, or technical issue (e.g., asking about compatibility, features, or troubleshooting).
            3. Use "feedback" if the email offers praise, suggestions, or constructive criticism.
            4. Use "support_request" if the email describes technical issues or requests help (e.g., error messages, installation problems).
            5. Use "other" if the email does not clearly match any of the above categories or shows no clear intent.

            Email Details:
            From: {from_s}
            Subject: {subject}
            Body: {body}

            Respond with only one of the category names.
            """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0)
            classification = response.choices[0].message.content.strip().lower()
            if classification in self.valid_categories:
                logger.info(f"email classified as {classification}")
                return classification
            else:
                logger.error(f"Invalid catagory recieved {classification}")
                return None
        except Exception as e:
            logger.error(f"Error during email classification: {e}, ID: {email['id']}")
            return None


    def generate_response(self, email: Dict, classification: str) -> Optional[str]:
        """
        Generate an automated response based on email classification.
        
        TODO:
        1. Design the response generation prompt
        2. Implement appropriate response templates
        3. Add error handling
        """
        if not self.vaildate_email(email):
            return
        from_s = self.get_email_from(email)
        body = self.get_email_body(email)
        subject = self.get_email_subject(email)

        if classification == "complaint":
            prompt = f"""
            Generate a professional and empathetic response to the following complaint email. 
            Ensure to acknowledge the issue, apologize, and provide a solution or next steps.
            
            Here is the email:
            Subject: {subject}
            body: {body}
            only generate the body of the email response and nothing else.
            """
        elif classification == "inquiry":
            prompt = f"""
            Generate a professional response to the following inquiry email. 
            Provide clear and concise information related to the inquiry.
            
            Here is the email:
            Subject: {subject}
            body: {body}
            only generate the body of the email response and nothing else.
            """
        elif classification == "feedback":
            prompt = f"""
            Generate a professional response to the following feedback email. 
            Thank the customer for their feedback and provide any necessary follow-up.
            
            Here is the email:
            Subject: {subject}
            body: {body}
            only generate the body of the email response and nothing else.
            """
        elif classification == "support_request":
            prompt = f"""
            Generate a professional response to the following support request email. 
            Acknowledge the issue and provide a solution or next steps.
            
            Here is the email:
            Subject: {subject}
            body: {body}
            only generate the body of the email response and nothing else.
            """
        else:
            prompt = f"""
            Generate a professional response to the following email. 
            Provide a standard acknowledgment, and direct them to the appropriate department if necessary.
            Here is the email:
            Subject: {subject}
            body: {body}
            only generate the body of the email response and nothing else.
            """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1)
            response_email = response.choices[0].message.content.strip()
            return response_email
        except Exception as e:
            logger.error(f"Error during response generation: {e}, email_id: {email['id']}")
            return None

class EmailAutomationSystem:
    def __init__(self, processor: EmailProcessor):
        """Initialize the automation system with an EmailProcessor."""
        self.processor = processor
        self.response_handlers = {
            "complaint": self._handle_complaint,
            "inquiry": self._handle_inquiry,
            "feedback": self._handle_feedback,
            "support_request": self._handle_support_request,
            "other": self._handle_other
        }

    def process_email(self, email: Dict) -> Dict:
        """
        Process a single email through the complete pipeline.
        Returns a dictionary with the processing results.
        
        TODO:
        1. Implement the complete processing pipeline
        2. Add appropriate error handling
        3. Return processing results
        """
        if not self.processor.vaildate_email(email):
            return
        from_s = self.processor.get_email_from(email)
        classify = self.processor.classify_email(email)
        if classify:
            logger.info(f"Email classified as: {classify}, email_id: {email['id']}")
            response_hander = self.response_handlers.get(classify)
            if response_hander:
                response = response_hander(email)
                return {
                    "email_id": from_s,
                    "success": True,
                    "classification": classify,
                    "response_sent": response
                }
            else:
                logger.error(f"No handler found for classification: {classify}, email_id: {email['id']}")
                return {
                    "email_id": from_s,
                    "success": False,
                    "classification": classify,
                    "response_sent": False
                }
        else:
            logger.error(f"Failed to classify email: {email['id']}")
            return {
                    "email_id": from_s,
                    "success": False,
                    "classification": False,
                    "response_sent": False
                }

    def _handle_complaint(self, email: Dict):
        """
        Handle complaint emails.
        TODO: Implement complaint handling logic
        """
        response = self.processor.generate_response(email, "complaint")
        from_s = self.processor.get_email_from(email)
        body = self.processor.get_email_body(email)
        if response:
            send_complaint_response(from_s, response)
        else:
            logger.error("Failed to generate response for complaint email.")
            # If LLM is unable to generate a response put a ticket in.
            create_urgent_ticket(from_s, "complaint", body)
        return response

    def _handle_inquiry(self, email: Dict):
        """
        Handle inquiry emails.
        TODO: Implement inquiry handling logic
        """
        response = self.processor.generate_response(email, "inquiry")
        from_s = self.processor.get_email_from(email)
        body = self.processor.get_email_body(email)
        if response:
            send_standard_response(from_s, response)
        else:
            # If LLM is unable to generate a response put a ticket in.
            logger.error("Failed to generate response for inquiry email.")
            create_support_ticket(from_s, "inquiry", body)
        return response

    def _handle_feedback(self, email: Dict):
        """
        Handle feedback emails.
        TODO: Implement feedback handling logic
        """
        response = self.processor.generate_response(email, "feedback")
        from_s = self.processor.get_email_from(email)
        body = self.processor.get_email_body(email)
        if response:
            log_customer_feedback(from_s, body)
            send_standard_response(from_s, response)
        else:
            # If LLM is unable to generate a response put a ticket in.
            logger.error("Failed to generate response for feeback email.")
            create_support_ticket(from_s, "feedback")
        return response

    def _handle_support_request(self, email: Dict):
        """
        Handle support request emails.
        TODO: Implement support request handling logic
        """
        response = self.processor.generate_response(email, "support_request")
        from_s = self.processor.get_email_from(email)
        body = self.processor.get_email_body(email)
        if response:
            send_standard_response(from_s, response)
        else:
            # If LLM is unable to generate a response put a ticket in.
            logger.error("Failed to generate response for support request email.")
            create_support_ticket(from_s, body)
        return response

    def _handle_other(self, email: Dict):
        """
        Handle other category emails.
        TODO: Implement handling logic for other categories
        """
        response = self.processor.generate_response(email, "other")
        from_s = self.processor.get_email_from(email)
        body = self.processor.get_email_body(email)
        if response:
            send_standard_response(from_s, response)
        else:
            # If LLM is unable to generate a response put a ticket in.
            logger.error("Failed to generate response for other email.")
            create_support_ticket(from_s, body)
        return response

# Mock service functions
def send_complaint_response(email_id: str, response: str):
    """Mock function to simulate sending a response to a complaint"""
    logger.info(f"Sending complaint response for email {email_id}")
    # In real implementation: integrate with email service


def send_standard_response(email_id: str, response: str):
    """Mock function to simulate sending a standard response"""
    logger.info(f"Sending standard response for email {email_id}")
    # In real implementation: integrate with email service


def create_urgent_ticket(email_id: str, category: str, context: str):
    """Mock function to simulate creating an urgent ticket"""
    logger.info(f"Creating urgent ticket for email {email_id}")
    # In real implementation: integrate with ticket system


def create_support_ticket(email_id: str, context: str):
    """Mock function to simulate creating a support ticket"""
    logger.info(f"Creating support ticket for email {email_id}")
    # In real implementation: integrate with ticket system


def log_customer_feedback(email_id: str, feedback: str):
    """Mock function to simulate logging customer feedback"""
    logger.info(f"Logging feedback for email {email_id}")
    # In real implementation: integrate with feedback system


def run_demonstration():
    """Run a demonstration of the complete system."""
    # Initialize the system
    processor = EmailProcessor()
    automation_system = EmailAutomationSystem(processor)

    # Process all sample emails
    results = []
    for email in sample_emails:
        logger.info(f"\nProcessing email {email['id']}...")
        result = automation_system.process_email(email)
        results.append(result)

    # Create a summary DataFrame
    df = pd.DataFrame(results)
    print("\nProcessing Summary:")
    print(df[["email_id", "success", "classification", "response_sent"]])

    return df


# Example usage:
if __name__ == "__main__":
    results_df = run_demonstration()


        
