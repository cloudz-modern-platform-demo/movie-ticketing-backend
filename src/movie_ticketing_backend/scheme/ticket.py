"""Pydantic schemas for ticket request/response models."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class IssueTicketRequest(BaseModel):
    """Request schema for issuing tickets."""
    
    theater_name: str = Field(..., min_length=1, max_length=100)
    user_id: str = Field(..., min_length=1, max_length=100)
    movie_title: str = Field(..., min_length=1, max_length=200)
    price_krw: int = Field(..., gt=0, le=1_000_000)
    quantity: int = Field(default=1, ge=1, le=10)
    memo: Optional[str] = Field(default=None)


class IssueTicketSummary(BaseModel):
    """Summary information in the issue ticket response."""
    
    theater_name: str
    movie_title: str
    price_krw: int


class IssueTicketResponse(BaseModel):
    """Response schema for issuing tickets."""
    
    ticket_ids: list[str]
    count: int
    summary: IssueTicketSummary


class RefundTicketRequest(BaseModel):
    """Request schema for refunding tickets."""
    
    ticket_ids: list[str] = Field(..., min_length=1)
    reason: Optional[str] = Field(default=None)
    
    @field_validator('ticket_ids')
    @classmethod
    def validate_ticket_ids(cls, v):
        """Validate that ticket_ids is not empty and contains valid strings."""
        if not v:
            raise ValueError("ticket_ids must not be empty")
        if any(not ticket_id or not isinstance(ticket_id, str) for ticket_id in v):
            raise ValueError("All ticket_ids must be non-empty strings")
        return v


class RefundTicketResponse(BaseModel):
    """Response schema for refunding tickets."""
    
    refunded: list[str]
    already_canceled: list[str]
    not_found: list[str]


class TicketResponse(BaseModel):
    """Response schema for a single ticket."""
    
    id: str
    theater_name: str
    user_id: str
    movie_title: str
    price_krw: int
    status: str
    issued_at: datetime
    canceled_at: Optional[datetime]
    memo: Optional[str]
    
    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    """Response schema for listing tickets."""
    
    tickets: list[TicketResponse]
    total: int
    limit: int
    offset: int

