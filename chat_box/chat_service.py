from __future__ import annotations

import os
import json
import threading
import time
import re
from datetime import datetime
from typing import List, Dict, Any

# Try to import LangChain components with fallback
try:
    from langchain_ollama import OllamaLLM
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Warning: LangChain modules not available. Using basic response.")

# Import wiki extractor functions
try:
    import sys
    import os
    # Add the parent directory to sys.path to ensure import works from any location
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from information_extraction import wiki_extractor
    WIKI_AVAILABLE = True
except ImportError:
    WIKI_AVAILABLE = False
    print("Warning: Wiki extractor not available.")


class MockLLM:
    """Mock LLM for when LangChain is not available."""
    def invoke_dummy(self, input_text):
        return f"I received your message: '{input_text}'. This is a mock response since the actual model is not available."


# Absolute path for the chat history JSON file
HISTORY_FILE_PATH = "/Users/kavan/Documents/GitHub/optimus-prime-voice-assistant-MACOS/chat_box/chat_history.json"


class ChatService:
    """Chat service using local Ollama model with JSON-based chat history and ChatPromptTemplate.

    - Stores conversation history in JSON format for better structure
    - Uses ChatPromptTemplate for better context management
    - Maintains full conversation history instead of plain text logs
    """

    def __init__(self, model_name: str = "mistral:instruct") -> None:
        if LANGCHAIN_AVAILABLE:
            self.llm = OllamaLLM(model=model_name)
            
            # Initialize chat history
            self.history: List[Dict[str, Any]] = self.load_history()
            
            # Create ChatPromptTemplate with message history
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant. Use the conversation history to provide context-aware responses."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
            
            # Create chain with prompt and LLM
            self.chain = self.prompt | self.llm
        else:
            self.llm = MockLLM()
            self.history: List[Dict[str, Any]] = self.load_history()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(HISTORY_FILE_PATH), exist_ok=True)
        
        # Add initial message if history is empty
        if not self.history:
            self.add_message('bot', 'How can I help you ?')

    def load_history(self) -> List[Dict[str, Any]]:
        """Load chat history from JSON file."""
        if os.path.exists(HISTORY_FILE_PATH):
            try:
                with open(HISTORY_FILE_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def save_history(self) -> None:
        """Save chat history to JSON file."""
        with open(HISTORY_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def add_message(self, role: str, text: str) -> None:
        """Add a message to the chat history."""
        timestamp = datetime.utcnow().isoformat()
        message = {
            "role": role,
            "text": text,
            "timestamp": timestamp
        }
        self.history.append(message)
        self.save_history()

    def get_formatted_history(self) -> List:
        """Get formatted history for LangChain messages."""
        messages = []
        for entry in self.history:
            if entry['role'] == 'kg':
                messages.append(HumanMessage(content=entry['text']))
            elif entry['role'] == 'bot':
                messages.append(AIMessage(content=entry['text']))
        return messages

    def _is_specific_query(self, user_text: str) -> tuple[bool, str]:
        """Use the NLP model to check if the query is about a specific event, person, or place, and extract the entity."""
        print(f"Debug: LANGCHAIN_AVAILABLE = {LANGCHAIN_AVAILABLE}")
        if not LANGCHAIN_AVAILABLE:
            print("Debug: Using fallback heuristics")
            # Fallback to simple heuristics if LangChain not available
            lower_text = user_text.lower()
            if any(lower_text.startswith(phrase) for phrase in ['who is', 'what is', 'where is', 'tell me about', 'who are', 'what are']):
                if not any(word in lower_text for word in ['grammar', 'english', 'language', 'math', 'science']):
                    entity = self._extract_entity(user_text)
                    print(f"Debug: Heuristics detected specific query, entity: {entity}")
                    return True, entity
            print("Debug: Heuristics detected non-specific query")
            return False, ""

        try:
            print("Debug: Invoking LLM for classification")
            # Create a prompt for classification and extraction
            classification_prompt = f"Analyze the user query. Is it asking about a specific event (like a tournament or historical event), person (like a celebrity or historical figure), or place (like a city or landmark)? If yes, extract the main entity name (e.g., 'ICC Champions Trophy 2025' from 'Who are champions of icc champions trophy 2025 ?'). Respond ONLY with JSON: {{\"is_specific\": true, \"what_specific\": \"entity name\"}} or {{\"is_specific\": false}}.\n\nQuery: {user_text}"
            print(f"Debug: Prompt: {classification_prompt}")
            response = self.llm.invoke(classification_prompt)
            print(f"Debug: LLM response: {response}")
            response_text = response if isinstance(response, str) else str(response)
            # Extract JSON from response
            json_str = self._extract_json_from_response(response_text)
            print(f"Debug: Extracted JSON: {json_str}")
            if json_str:
                try:
                    data = json.loads(json_str)
                    is_specific = data.get('is_specific', False)
                    what_specific = data.get('what_specific', '') if is_specific else ''
                    print(f"Debug: Parsed is_specific: {is_specific}, what_specific: {what_specific}")
                    return is_specific, what_specific
                except json.JSONDecodeError:
                    print("Debug: JSONDecodeError")
                    pass
            print("Debug: No valid JSON found")
            return False, ""
        except Exception as e:
            print(f"Error in classification: {e}")
            return False, ""

    def _extract_entity(self, user_text: str) -> str:
        """Extract the entity from the query, e.g., 'icc champions trophy 2025' from 'Who are champions of icc champions trophy 2025 ?'"""
        # Remove question words and punctuation
        entity = re.sub(r'^(who|what|where|tell me about)\s+', '', user_text.lower(), flags=re.IGNORECASE)
        entity = re.sub(r'[^\w\s]', '', entity).strip()
        return entity

    def ask(self, user_text: str) -> str:
        user_text = (user_text or '').strip()
        if not user_text:
            return ''

        # Check if user requested tabular form
        is_tabular_request = any(phrase in user_text.lower() for phrase in ['table', 'tabular', 'form', 'give in table', 'view in table', 'show as table'])

        # Check if it's a specific query about event/person/place
        is_specific, entity = self._is_specific_query(user_text)
        print(f"Debug: is_specific={is_specific}, entity='{entity}'")

        # Note: User message is already added by JavaScript for immediate UI feedback
        # We only add the bot response here to avoid duplication

        try:
            if LANGCHAIN_AVAILABLE:
                # Format history for the prompt
                chat_history = self.get_formatted_history()
                print("Wiki: "+str(WIKI_AVAILABLE))
                if is_specific and WIKI_AVAILABLE:
                    # Entity is already extracted by _is_specific_query
                    if entity:
                        # Search and parse
                        url = wiki_extractor.search_wikipedia(entity)
                        if url:
                            data = wiki_extractor.parse_article(url)
                            # Save JSON
                            filename = re.sub(r'[^A-Za-z0-9]+', '_', entity)[:40] + '.json'
                            wiki_extractor.save_json(data, filename)
                            # Extract sections text
                            sections_text = '\n\n'.join([sec['text'] for sec in data.get('sections', []) if sec['text']])
                            # Create prompt with context
                            context_prompt = f"Based on the following information from Wikipedia:\n{sections_text}\n\nUser question: {user_text}"
                            # Use direct LLM invoke without chat history to ensure context is used
                            response = self.llm.invoke(context_prompt)
                        else:
                            # Fallback if no URL found
                            response = self.chain.invoke({
                                "chat_history": chat_history,
                                "input": user_text
                            })
                    else:
                        response = self.chain.invoke({
                            "chat_history": chat_history,
                            "input": user_text
                        })
                elif is_tabular_request:
                    # Create a specific prompt for tabular responses
                    response = self.chain.invoke({
                        "chat_history": chat_history,
                        "input": f"{user_text}. Return ONLY a valid JSON array with no explanation or additional text. Format the response as a JSON array of objects."
                    })
                else:
                    # Generate bot response using the chain
                    response = self.chain.invoke({
                        "chat_history": chat_history,
                        "input": user_text
                    })

                response_text = response if isinstance(response, str) else str(response)

                # If it's a tabular request, try to extract and validate JSON
                if is_tabular_request:
                    # Extract JSON from response if it's wrapped in code blocks or has extra text
                    response_text = self._extract_json_from_response(response_text)
            else:
                # Use mock response when LangChain is not available
                response_text = self.llm.invoke(user_text)
        except Exception as e:
            # Handle any error during LLM processing
            response_text = f"Sorry, I encountered an error: {str(e)}"

        # Add bot response to history
        self.add_message('bot', response_text)

        return response_text
    
    def ask_for_summary(self, user_text: str) -> str:
        user_text = (user_text or '').strip()
        if not user_text:
            return ''
        try:
            if LANGCHAIN_AVAILABLE:
                # # Format history for the prompt
                chat_history = self.get_formatted_history()
                
                # Create a specific prompt for summary responses
                response = self.chain.invoke({
                    "chat_history": chat_history,
                    "input": f"{user_text}"
                })
                
                response_text = response if isinstance(response, str) else str(response)
            else:
                # Use mock response when LangChain is not available
                response_text = self.llm.invoke(user_text)
        except Exception as e:
            # Handle any error during LLM processing
            response_text = f"Sorry, I encountered an error: {str(e)}"
        return response_text
        

    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON from response that might be wrapped in markdown or have extra text"""
        import re
        import json
        
        # Remove code block markers if present
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith("```"):
            response_text = response_text[3:]   # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove trailing ```
        
        # Extract JSON array/object using regex
        json_match = re.search(r'\[.*\]|\{.*\}', response_text, re.DOTALL)
        if json_match:
            extracted_json = json_match.group()
            # Validate the extracted JSON
            try:
                parsed = json.loads(extracted_json)
                # Save the JSON to temp.json when we have a valid response
                temp_path = "/Users/kavan/Documents/GitHub/optimus-prime-voice-assistant-MACOS/chat_box/temp.json"
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(parsed, f, ensure_ascii=False, indent=2)
                return json.dumps(parsed)  # Return clean JSON string
            except json.JSONDecodeError:
                pass  # If invalid, return original response
        
        return response_text

    def add_user_message_only(self, user_text: str) -> None:
        """Add only the user message without processing or adding a bot response."""
        user_text = (user_text or '').strip()
        if not user_text:
            return
        self.add_message('kg', user_text)


def run_interactive() -> None:
    """Simple terminal loop to test the chat service and populate the history file."""
    service = ChatService()
    print("Chat started. Type your message and press Enter. Ctrl+C to exit.")
    try:
        while True:
            user_msg = input("kg: ")
            if not user_msg.strip():
                continue
            bot_msg = service.ask(user_msg)
            print(f"bot: {bot_msg}")
    except KeyboardInterrupt:
        print("\nExiting chat.")


if __name__ == "__main__":
    run_interactive()


