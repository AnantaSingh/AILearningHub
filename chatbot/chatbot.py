import nltk
import numpy as np
import random
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
import ssl
import os
from pathlib import Path
from functools import lru_cache
import sys

class ChatBot:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatBot, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not ChatBot._is_initialized:
            self.GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey")
            self.GREETING_RESPONSES = ["Hi! I'm your AI Learning Assistant.", 
                                     "Hello! How can I help you learn about AI?", 
                                     "Hey there! Ready to explore AI concepts?",
                                     "Welcome! What would you like to learn about?"]
            
            # Set up NLTK
            self._setup_nltk()
            
            # Initialize the bot
            self.knowledge_base = self._read_knowledge_base()
            self.sentences = self._preprocess_text(self.knowledge_base)
            
            # Create TF-IDF vectorizer with improved parameters
            self.vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 3),
                max_features=5000,
                min_df=2,
                max_df=0.95
            )
            # Cache the TF-IDF matrix
            self.tfidf_matrix = self._create_tfidf_matrix()
            
            ChatBot._is_initialized = True

    @lru_cache(maxsize=128)
    def _get_response_cached(self, user_input):
        """Cached version of response generation for frequently asked questions"""
        try:
            user_vec = self.vectorizer.transform([user_input])
            similarities = cosine_similarity(user_vec, self.tfidf_matrix)
            top_indices = similarities[0].argsort()[-3:][::-1]
            top_similarities = similarities[0][top_indices]
            
            if top_similarities[0] > 0.3:
                response = self.sentences[top_indices[0]]
                response = ': '.join(response.split(': ')[1:])
                
                if len(response.split()) < 15 and top_similarities[1] > 0.25:
                    second_response = ': '.join(self.sentences[top_indices[1]].split(': ')[1:])
                    response = f"{response} {second_response}"
                
                return response
            return None
        except Exception:
            return None

    def _create_tfidf_matrix(self):
        """Create and cache the TF-IDF matrix"""
        return self.vectorizer.fit_transform(self.sentences)

    def _setup_nltk(self):
        """Set up NLTK with proper error handling"""
        try:
            # Create unverified SSL context for NLTK downloads
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context

            # Create NLTK data directory if it doesn't exist
            nltk_data_dir = str(Path.home() / 'nltk_data')
            os.makedirs(nltk_data_dir, exist_ok=True)

            # Download required NLTK data
            required_packages = ['punkt', 'averaged_perceptron_tagger', 'wordnet']
            
            # First try downloading punkt specifically
            try:
                nltk.download('punkt', quiet=True, download_dir=nltk_data_dir)
            except Exception as e:
                print(f"Warning: Failed to download punkt package: {e}")
                # Try alternative download method
                import subprocess
                subprocess.run([sys.executable, '-m', 'nltk.downloader', 'punkt'])

            # Download other packages
            for package in required_packages:
                if package != 'punkt':  # Skip punkt as we already tried it
                    try:
                        nltk.download(package, quiet=True, download_dir=nltk_data_dir)
                    except Exception as e:
                        print(f"Warning: Failed to download NLTK package {package}: {e}")

            # Verify punkt is available
            try:
                from nltk.tokenize import PunktSentenceTokenizer
                tokenizer = PunktSentenceTokenizer()
                # Test the tokenizer
                test_text = "This is a test. This is another test."
                tokenizer.tokenize(test_text)
            except Exception as e:
                print(f"Warning: Punkt tokenizer not working properly: {e}")
                print("Falling back to basic sentence splitting.")
                self.use_basic_tokenizer = True
            else:
                self.use_basic_tokenizer = False

        except Exception as e:
            print(f"Warning: NLTK setup encountered an error: {e}")
            print("The chatbot will continue to function with reduced capabilities.")
            self.use_basic_tokenizer = True

    def _basic_sentence_tokenize(self, text):
        """Basic sentence tokenization fallback"""
        # Split on common sentence endings
        text = text.replace('\n', ' ')
        sentences = []
        current = []
        
        for word in text.split():
            current.append(word)
            if word.endswith(('.', '!', '?')):
                sentences.append(' '.join(current))
                current = []
        
        if current:  # Add any remaining text
            sentences.append(' '.join(current))
        
        return sentences

    @property
    def topics(self):
        """Get available topics for suggestions"""
        return list(self.knowledge_base.keys())

    def get_topic_sections(self, topic):
        """Get sections available for a specific topic"""
        return list(self.knowledge_base.get(topic, {}).keys())

    def _greeting(self, sentence):
        """Check if the input is a greeting and return an appropriate response"""
        for word in sentence.lower().split():
            if word in self.GREETING_INPUTS:
                return random.choice(self.GREETING_RESPONSES)
        return None

    def get_response(self, user_input):
        """Generate a response to user input with improved matching and context"""
        # Check for greeting
        greeting_response = self._greeting(user_input)
        if greeting_response:
            return greeting_response

        try:
            # Check cache first
            user_input_processed = user_input.lower().strip()
            cached_response = self._get_response_cached(user_input_processed)
            
            if cached_response:
                return cached_response
                
            # If not in cache, generate new response
            user_vec = self.vectorizer.transform([user_input_processed])
            similarities = cosine_similarity(user_vec, self.tfidf_matrix)
            top_indices = similarities[0].argsort()[-3:][::-1]
            top_similarities = similarities[0][top_indices]
            
            if top_similarities[0] > 0.3:
                response = self.sentences[top_indices[0]]
                response = ': '.join(response.split(': ')[1:])
                
                if len(response.split()) < 15 and top_similarities[1] > 0.25:
                    second_response = ': '.join(self.sentences[top_indices[1]].split(': ')[1:])
                    response = f"{response} {second_response}"
                
                return response
            else:
                return ("I'm not quite sure about that. Could you please rephrase your question "
                       "or ask specifically about AI, machine learning, deep learning, or NLP?")
                
        except Exception as e:
            print(f"Error generating response: {e}")
            return ("I encountered an error while processing your question. "
                   "Please try asking in a different way.")

    def _read_knowledge_base(self):
        """Read and organize the knowledge base"""
        return {
            "ai_basics": {
                "overview": """
                    Artificial Intelligence (AI) is the simulation of human intelligence by machines. 
                    AI systems can perform tasks that typically require human intelligence, such as 
                    visual perception, speech recognition, decision-making, and language translation.
                """,
                "types": """
                    There are two main types of AI:
                    1. Narrow AI (Weak AI): Designed for specific tasks like facial recognition or chess
                    2. General AI (Strong AI): Systems with generalized human cognitive abilities
                """,
                "components": """
                    Key components of AI include:
                    - Machine Learning: Algorithms that allow systems to learn from data
                    - Neural Networks: Computing systems inspired by biological neural networks
                    - Deep Learning: Advanced machine learning using multiple layers
                    - Natural Language Processing: Enabling computers to understand human language
                """
            },
            "machine_learning": {
                "overview": """
                    Machine Learning (ML) is a subset of AI that focuses on developing systems that 
                    can learn and improve from experience without explicit programming.
                """,
                "types": """
                    Types of Machine Learning:
                    1. Supervised Learning: Learning from labeled data
                    2. Unsupervised Learning: Finding patterns in unlabeled data
                    3. Reinforcement Learning: Learning through environment interaction
                """,
                "applications": """
                    Common ML applications include:
                    - Image and Speech Recognition
                    - Recommendation Systems
                    - Fraud Detection
                    - Market Analysis
                    - Medical Diagnosis
                """
            },
            "deep_learning": {
                "overview": """
                    Deep Learning is a specialized form of machine learning that uses neural networks 
                    with multiple layers (deep neural networks) to progressively extract higher-level 
                    features from raw input.
                """,
                "characteristics": """
                    Key characteristics of deep learning:
                    - Automatic Feature Extraction from raw data
                    - Hierarchical Learning with increasing complexity
                    - End-to-End Learning capabilities
                """,
                "applications": """
                    Applications include:
                    - Computer Vision and Image Recognition
                    - Natural Language Processing
                    - Speech Recognition
                    - Autonomous Vehicles
                    - Game Playing AI
                """
            },
            "nlp": {
                "overview": """
                    Natural Language Processing (NLP) is a branch of AI that helps computers 
                    understand, interpret, and manipulate human language.
                """,
                "tasks": """
                    Key NLP tasks include:
                    - Text Classification and Categorization
                    - Sentiment Analysis
                    - Machine Translation
                    - Named Entity Recognition
                    - Question Answering
                    - Text Generation
                """,
                "applications": """
                    NLP powers:
                    - Virtual Assistants (Siri, Alexa)
                    - Machine Translation Services
                    - Chatbots and Conversational AI
                    - Text Analysis Tools
                    - Speech Recognition Systems
                """
            }
        }

    def _preprocess_text(self, knowledge_base):
        """Process the knowledge base into sentences with improved context"""
        processed_sentences = []
        
        for topic, sections in knowledge_base.items():
            for section, content in sections.items():
                # Clean the content
                content = content.strip().replace('\n', ' ')
                
                # Add topic and section context to each sentence
                try:
                    if self.use_basic_tokenizer:
                        sentences = self._basic_sentence_tokenize(content)
                    else:
                        sentences = nltk.sent_tokenize(content)
                        
                    for sentence in sentences:
                        # Clean each sentence
                        sentence = ' '.join(sentence.split())
                        if sentence:
                            # Add context prefix for better matching
                            contextualized_sentence = f"{topic} {section}: {sentence}"
                            processed_sentences.append(contextualized_sentence)
                except Exception as e:
                    print(f"Warning: Error processing text: {e}")
                    # If tokenization fails, treat the entire content as one sentence
                    sentence = ' '.join(content.split())
                    if sentence:
                        contextualized_sentence = f"{topic} {section}: {sentence}"
                        processed_sentences.append(contextualized_sentence)
        
        return processed_sentences

# For command line testing
if __name__ == "__main__":
    chatbot = ChatBot()
    print("Bot: Hi! I'm your AI chatbot. I can help you learn about AI, ML, and related topics.")
    print("Bot: Type 'quit' to exit")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Bot: Goodbye! Have a great day!")
            break
            
        response = chatbot.get_response(user_input)
        print("Bot:", response) 