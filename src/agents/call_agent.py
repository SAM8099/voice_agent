from langchain.prompts import PromptTemplate
from src.schemas.schemas import IntentSchema
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq.chat_models import ChatGroq
from src.utils import INTENT_PROMPT as prompt_template

class CallAgent:
    def __init__(self, key: str = None):
        self.model = ChatGroq(temperature=0,model_name="llama-3.3-70b-versatile",api_key=key)
        self.prompt =  PromptTemplate(input_variables=["user_input"], template=prompt_template)
        self.parser = JsonOutputParser(schema=IntentSchema)

    def call(self, user_input: str):
        chain = self.prompt | self.model | self.parser   
        response = chain.invoke({"user_input": user_input})
        return response