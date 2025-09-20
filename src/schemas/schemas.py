from pydantic import BaseModel

class Query(BaseModel):
    user_input: str
    
class IntentSchema(BaseModel):
    intent: str
    customer_name: str | None
    complaint_id: str | None
    description: str | None
    