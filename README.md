# Voice Agent
This is a customer care chatbot which will be integrated with the phone to take customer queries and give much needed response. The type of responses are-
1. Take customer complaint.
2. Tell the customer current status of complaints.

## File Structure
1. app.py - FastAPI backend to take complaint and process it and return output in speech.
2. main.py - Streamlit frontend for presentation for interacting with users.
3. push_data.py - Setup and push sample data into the database for storage and retrieval.
4. requirements.txt - Contains all the necessary frameworks and libraries to work.
5. src/agents/call_agent.py - Contains the class of LLM for taking input.
6. src/memory/database.py - Conatins all the functions to interact , retrieve and push data from the database.
7. src/schemas/schemas - Contains the format of how data will be transfered between frontend and backend and what type of format will the LLM response will have.
8. src/utils.py - Conatins the important constants and entities used in the project.
9. voice_agent.db - The database which stores all the users and their queries.

## Technologies used
FastAPI, Streamlit, Groq LLM, Langchain, pytts, speech-recognition, sqlite3, Pydantic.
