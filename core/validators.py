from pydantic import BaseModel, Field

class NFTIDValidator(BaseModel):
    nft_id: str = Field(..., regex=r'^0x[a-fA-F0-9]{40}$')
