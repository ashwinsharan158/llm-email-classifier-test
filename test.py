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
    }
]

'''export OPENAI_API_KEY="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"'''

class EmailProcessor:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initialize the email processor with OpenAI API key."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Define valid categories
        self.valid_categories = {
            "complaint", "inquiry", "feedback",
            "support_request", "other"
        }
        self.model = model

    def classify_email(self, email: Dict) -> Optional[str]:
        """
        Classify an email using LLM.
        Returns the classification category or None if classification fails.
        
        TODO: 
        1. Design and implement the classification prompt
        2. Make the API call with appropriate error handling
        3. Validate and return the classification
        """
        if not email.get("body"):
            logger.error("Email body is empty or missing.")
            return None
        
        prompt = f"""
        classify the following email based on its content into one of the following categories: {', '.join(self.valid_categories)}
        , and classify it as 'other' only if it doesn't fit any of the categories mentioned, or the email shows no clear intent.
        
        here is the email:
        from: {email['from']}
        Subject: {email['subject']}
        body: {email['body']}

        Please give only one category name from the categories as output and nothing else.

        """
        try:

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0)
            
            # classification = response.choices[0].message['content'].strip().lower()
            classification = response.choices[0].message.content.strip().lower()
            if classification in self.valid_categories:
                logger.info(f"Email classified as: {classification}")
                return classification
            else:
                logger.error(f"Invalid classification received: {classification}") # Bad Prompt
                return None
            
        except Exception as e:
            logger.error(f"Error during email classification: {e}, email_id: {email['id']}")
            return None



    def generate_response(self, email: Dict, classification: str) -> Optional[str]:
        """
        Generate an automated response based on email classification.
        
        TODO:
        1. Design the response generation prompt
        2. Implement appropriate response templates
        3. Add error handling
        """
        # Based on the classification, the prompt will change 
        if classification == "complaint":
            prompt = f"""
            Generate a professional and empathetic response to the following complaint email. 
            Ensure to acknowledge the issue, apologize, and provide a solution or next steps.
            
            Here is the email:
            Subject: {email['subject']}
            body: {email['body']}
            only generate the body of the email response and nothing else.
            """
        elif classification == "inquiry":
            prompt = f"""
            Generate a professional response to the following inquiry email. 
            Provide clear and concise information related to the inquiry.
            
            Here is the email:
            Subject: {email['subject']}
            body: {email['body']}
            only generate the body of the email response and nothing else.
            """
        elif classification == "feedback":
            prompt = f"""
            Generate a professional response to the following feedback email. 
            Thank the customer for their feedback and provide any necessary follow-up.
            
            Here is the email:
            Subject: {email['subject']}
            body: {email['body']}
            only generate the body of the email response and nothing else.
            """
        elif classification == "support_request":
            prompt = f"""
            Generate a professional response to the following support request email. 
            Acknowledge the issue and provide a solution or next steps.
            
            Here is the email:
            Subject: {email['subject']}
            body: {email['body']}
            only generate the body of the email response and nothing else.
            """
        else:
            prompt = f"""
            Generate a professional response to the following email. 
            Provide a standard acknowledgment, and direct them to the appropriate department if necessary.
            Here is the email:
            Subject: {email['subject']}
            body: {email['body']}
            only generate the body of the email response and nothing else.
            """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1)
            response_text = response.choices[0].message.content.strip()

            return response_text
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
        classify = self.processor.classify_email(email)
        if classify:
            logger.info(f"Email classified as: {classify}, email_id: {email['id']}")
            response_handler = self.response_handlers.get(classify)
            if response_handler:
                response = response_handler(email)
                return {
                    "email_id": email["id"],
                    "success": True,
                    "classification": classify,
                    "response_sent": bool(response)
                }
            else:
                logger.error(f"No handler found for classification: {classify}, email_id: {email['id']}")
                return {
                    "email_id": email["id"],
                    "success": False,
                    "classification": classify,
                    "response_sent": False
                }
        else:
            logger.error(f"Failed to classify email: {email['id']}")
            return {
                "email_id": email["id"],
                "success": False,
                "classification": None,
                "response_sent": False
            }
        
    def _handle_complaint(self, email: Dict):
        """
        Handle complaint emails.
        TODO: Implement complaint handling logic
        """
        response = self.processor.generate_response(email, "complaint")
        if response:
            send_complaint_response(email["id"], response)
        else:
            logger.error("Failed to generate response for complaint email.")
            # Since, it is a complaint, and the LLM couldn't solve, create an urgent ticket
            #  for the complaint
            create_urgent_ticket(email["id"], "complaint", email["body"])

        return response

    def _handle_inquiry(self, email: Dict):
        """
        Handle inquiry emails.
        TODO: Implement inquiry handling logic
        """
        response = self.processor.generate_response(email, "inquiry")
        
        if response:
            send_standard_response(email["id"], response)
        else:
            logger.error("Failed to generate response for inquiry email.")
            create_support_ticket(email["id"], "inquiry", email["body"])

        return response

    def _handle_feedback(self, email: Dict):
        """
        Handle feedback emails.
        TODO: Implement feedback handling logic
        """
        response = self.processor.generate_response(email, "feedback")
        
        if response:
            log_customer_feedback(email["id"], email["body"])
            send_standard_response(email["id"], response)
        else:
            logger.error("Failed to generate response for feedback email.")
            create_support_ticket(email["id"], "feedback", email["body"])

        return response

    def _handle_support_request(self, email: Dict):
        """
        Handle support request emails.
        TODO: Implement support request handling logic
        """

        response = self.processor.generate_response(email, "support_request")
        if response:
            send_standard_response(email["id"], response)
        else:
            logger.error("Failed to generate response for support request email.")
            create_support_ticket(email["id"], response)
        return response

    def _handle_other(self, email: Dict):
        """
        Handle other category emails.
        TODO: Implement handling logic for other categories
        """
        response = self.processor.generate_response(email, "other")

        if response:
            send_standard_response(email["id"], response)
        else:
            logger.error("Failed to generate response for other category email.")
            # Create a ticket for further review
            create_support_ticket(email["id"], "other", email["body"])
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
