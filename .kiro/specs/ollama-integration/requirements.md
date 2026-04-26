# Requirements Document

## Introduction

This specification defines the requirements for integrating Ollama AI backend support into the existing 广告思想简史 (Advertising History) Streamlit application. The goal is to restore and enhance the multi-AI backend functionality, allowing users to seamlessly switch between different AI providers (Gemini, Ollama, Azure OpenAI) through environment configuration.

## Glossary

- **AI_Backend**: The artificial intelligence service provider used for chat functionality
- **Ollama**: Open-source platform for running large language models locally
- **Unified_Chat_System**: The abstraction layer that handles multiple AI backends
- **Environment_Configuration**: Settings stored in .env file that control application behavior
- **Streamlit_App**: The main web application built with Streamlit framework

## Requirements

### Requirement 1: Multi-AI Backend Support

**User Story:** As a user, I want to use different AI backends for chat functionality, so that I can choose the most suitable AI service for my needs.

#### Acceptance Criteria

1. WHEN the application starts, THE Unified_Chat_System SHALL detect the configured AI backend from environment variables
2. WHEN AI_BACKEND is set to "ollama", THE Unified_Chat_System SHALL initialize the Ollama client
3. WHEN AI_BACKEND is set to "gemini", THE Unified_Chat_System SHALL initialize the Gemini client  
4. WHEN AI_BACKEND is set to "azure_openai", THE Unified_Chat_System SHALL initialize the Azure OpenAI client
5. WHEN an unsupported backend is configured, THE Unified_Chat_System SHALL display an error message and list supported options

### Requirement 2: Ollama Integration

**User Story:** As a user, I want to use Ollama for local AI chat, so that I can have private conversations without sending data to external services.

#### Acceptance Criteria

1. WHEN Ollama backend is selected, THE Ollama_Client SHALL check connection to the local Ollama service
2. WHEN Ollama service is running, THE Ollama_Client SHALL retrieve available models from the service
3. WHEN Ollama service is not running, THE Ollama_Client SHALL display connection error with troubleshooting instructions
4. WHEN a user sends a message, THE Ollama_Client SHALL generate responses using the configured local model
5. WHEN streaming is enabled, THE Ollama_Client SHALL provide real-time response streaming

### Requirement 3: Environment Configuration

**User Story:** As a system administrator, I want to configure AI backends through environment variables, so that I can easily switch between different AI services without code changes.

#### Acceptance Criteria

1. WHEN .env file contains AI_BACKEND setting, THE Streamlit_App SHALL use the specified backend
2. WHEN Ollama is configured, THE Streamlit_App SHALL read OLLAMA_BASE_URL and OLLAMA_MODEL settings
3. WHEN environment variables are missing, THE Streamlit_App SHALL use default values and display warnings
4. WHEN configuration is invalid, THE Streamlit_App SHALL show clear error messages with correction guidance
5. WHEN configuration changes, THE Streamlit_App SHALL require restart to apply new settings

### Requirement 4: Chat Interface Integration

**User Story:** As a user, I want the AI chat to work seamlessly within the existing application, so that I can access AI assistance while browsing advertising content.

#### Acceptance Criteria

1. WHEN I navigate to "与大师对话" page, THE Streamlit_App SHALL display the unified chat interface
2. WHEN the chat interface loads, THE Streamlit_App SHALL show the current AI backend and model information
3. WHEN I send a message, THE Chat_Interface SHALL display my message and generate an AI response
4. WHEN using Ollama backend, THE Chat_Interface SHALL show streaming responses in real-time
5. WHEN I clear the conversation, THE Chat_Interface SHALL reset the chat history and session state

### Requirement 5: Error Handling and User Feedback

**User Story:** As a user, I want clear feedback when AI services are unavailable, so that I can understand and resolve configuration issues.

#### Acceptance Criteria

1. WHEN Ollama service is not running, THE Streamlit_App SHALL display connection status and startup instructions
2. WHEN API keys are missing, THE Streamlit_App SHALL show configuration guidance with example .env settings
3. WHEN network errors occur, THE Streamlit_App SHALL display retry options and troubleshooting tips
4. WHEN model loading fails, THE Streamlit_App SHALL suggest alternative models and provide download commands
5. WHEN any AI backend fails, THE Streamlit_App SHALL gracefully degrade and maintain application functionality

### Requirement 6: Backend Status and Information

**User Story:** As a user, I want to see which AI backend is currently active, so that I understand which service is processing my requests.

#### Acceptance Criteria

1. WHEN the chat interface loads, THE Streamlit_App SHALL display the active backend name prominently
2. WHEN using Ollama, THE Streamlit_App SHALL show the local model name and connection status
3. WHEN using cloud services, THE Streamlit_App SHALL show the model name and service region if available
4. WHEN backend initialization fails, THE Streamlit_App SHALL show error status with diagnostic information
5. WHEN multiple backends are configured, THE Streamlit_App SHALL indicate which one is currently active

### Requirement 7: Conversation Management

**User Story:** As a user, I want my chat conversations to be properly managed, so that I can have coherent multi-turn discussions with the AI.

#### Acceptance Criteria

1. WHEN I send multiple messages, THE Chat_Interface SHALL maintain conversation context across turns
2. WHEN conversation history exceeds limits, THE Chat_Interface SHALL automatically truncate older messages
3. WHEN I refresh the page, THE Chat_Interface SHALL preserve the current conversation session
4. WHEN I switch between pages, THE Chat_Interface SHALL maintain conversation state
5. WHEN I manually clear history, THE Chat_Interface SHALL reset all conversation context immediately

### Requirement 8: Performance and Responsiveness

**User Story:** As a user, I want the AI chat to respond quickly and efficiently, so that I can have smooth conversations without long delays.

#### Acceptance Criteria

1. WHEN using Ollama locally, THE Chat_Interface SHALL display responses within 10 seconds for typical queries
2. WHEN using cloud services, THE Chat_Interface SHALL display responses within 5 seconds for typical queries
3. WHEN responses are streaming, THE Chat_Interface SHALL update the display in real-time without flickering
4. WHEN the AI is processing, THE Chat_Interface SHALL show appropriate loading indicators
5. WHEN requests timeout, THE Chat_Interface SHALL display timeout messages and allow retry options