# LLM Integration Exercise: Email Classification and Automation

## Overview
In this exercise, you'll build a system that uses Large Language Models (LLMs) to classify incoming emails and automate responses based on the classification. This tests your ability to:
- Integrate LLMs into a Python workflow
- Design and refine prompts for reliable classification
- Implement error handling and reliability measures
- Create automated response systems

## Setup and Requirements

### Environment Setup
1. Create a new virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

### Requirements File (requirements.txt)
```
openai>=1.3.0
pandas>=2.0.0
python-dotenv>=1.0.0
```

### Configuration
1. Create a `.env` file in your project root:
```
OPENAI_API_KEY=your_api_key_here
```

## Exercise Structure
The exercise is divided into four main parts:

### Part 1: Email Data Processing (10 minutes)
- Load and validate the provided mock email data
- Create functions to extract email data
- Implement basic data validation

### Part 2: LLM Integration (20 minutes)
- Design classification prompts
- Implement API calls
- Create classification system

### Part 3: Prompt Engineering (20 minutes)
- Analyze classification accuracy
- Identify and handle edge cases
- Document prompt iterations and improvements

### Part 4: Response Automation (10 minutes)
- Create response generation system
- Implement category-specific handling
- Add appropriate error handling and logging

## Documentation of Approach and Design Decisions

### Project Structure and Key Components
- **EmailProcessor**:  
  - **Responsibilities**:  
    - Validates incoming emails.
    - Extracts key fields (sender, subject, body).
    - Classifies emails using LLM integration.
    - Generates email responses based on the classification.
  - **Design Considerations**:  
    - Uses a low temperature (0) for classification to ensure consistency.
    - Uses a low but non-zero temperature (0.1) for response generation to allow for constrained creativity.
    - Added a `model` parameter to allow flexibility in choosing the LLM model.
    - The API key is loaded from an environment variable (`OPENAI_API_KEY`) to avoid exposing sensitive information.

- **EmailAutomationSystem**:  
  - **Responsibilities**:  
    - Orchestrates the complete processing pipeline for emails.
    - Invokes specific handlers for each email category.
    - Handles cases where the LLM fails to generate a response by triggering alternative actions (e.g., creating tickets).
  - **Design Considerations**:  
    - Uses a dictionary (`response_handlers`) to map classifications to handler functions, making the system modular.
    - Each `_handle_**` function encapsulates category-specific logic, with room for future improvements and scaling.

### Challenges and Design Optimizations
- **Challenges**:
  - Code repetition, particularly within the `generate_response` and the category-specific handler functions.
  - Limited scalability when handling additional email categories.

- **Design Optimizations**:
  - **Parameterize Valid Categories**: Allow valid categories to be passed as an input argument to `EmailProcessor` to improve flexibility.
  - **Decouple Response Handlers**: Instead of embedding the `_handle_**` functions within `EmailAutomationSystem`, use independent service functions. This reduces code duplication and eases scalability.
  - **Custom LLM Training**: In a production scenario, consider training a custom GPT model with internal resources and FAQ data. This could streamline the response generation by eliminating multiple conditionals in the response function.

## Evaluation Criteria

### 1. Code Quality (25%)
- Clean, well-documented code
- Proper error handling
- Modular design
- Appropriate use of Python best practices

### 2. LLM Integration (25%)
- Effective prompt design
- Proper handling of API calls
- Error handling

### 3. Prompt Engineering (25%)
- Clear documentation of prompt iterations
- Handling of edge cases
- Reasoning about improvements

### 4. System Design (25%)
- Modularity and extensibility
- Logging and monitoring
- Error recovery strategies

## Submission Requirements
1. Your completed code with:
   - Working implementation
   - Documentation of your approach
   - Examples run
2. Documentation of your prompt iterations, including:
   - Initial prompts
   - Problems encountered
   - Improvements made
3. A brief summary covering:
   - Your design decisions
   - Challenges encountered
   - Potential improvements
   - Production considerations
