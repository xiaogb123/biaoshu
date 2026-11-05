from datetime import datetime
from pydantic import BaseModel,ConfigDict

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id :int
    tender_id: int
    kind:str
    filename:str
    page_count:int
    status:str
    created_at:datetime

class UploadAccepted(BaseModel):
    document_id:int
    job_id:int | None

class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    status:str
    progress:int
    error:str | None