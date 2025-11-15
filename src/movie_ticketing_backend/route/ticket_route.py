"""Ticket routes for API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from movie_ticketing_backend.db.session import get_db
from movie_ticketing_backend.service.ticket_service import TicketService
from movie_ticketing_backend.scheme.ticket import (
    IssueTicketRequest,
    IssueTicketResponse,
    RefundTicketRequest,
    RefundTicketResponse,
    TicketResponse,
    TicketListResponse,
)


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post(
    "/issue",
    response_model=IssueTicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Issue new tickets",
    description="Issue one or more tickets for a movie showing",
)
def issue_tickets(
    request: IssueTicketRequest,
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    """
    Issue new tickets.
    
    Args:
        request: Ticket issue request data
        db: Database session
        idempotency_key: Optional idempotency key for duplicate prevention
        
    Returns:
        IssueTicketResponse with created ticket IDs
        
    Raises:
        HTTPException: 409 if idempotency key conflict occurs
        HTTPException: 500 if database operation fails
    """
    try:
        service = TicketService(db)
        return service.issue_tickets(request, idempotency_key)
    except ValueError as e:
        # Idempotency conflict
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to issue tickets: {str(e)}",
        )


@router.post(
    "/refund",
    response_model=RefundTicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Refund tickets",
    description="Refund one or more tickets by canceling them",
)
def refund_tickets(
    request: RefundTicketRequest,
    db: Session = Depends(get_db),
):
    """
    Refund tickets.
    
    Args:
        request: Ticket refund request data
        db: Database session
        
    Returns:
        RefundTicketResponse with refund results
        
    Raises:
        HTTPException: 500 if database operation fails
    """
    try:
        service = TicketService(db)
        return service.refund_tickets(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refund tickets: {str(e)}",
        )


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a ticket by ID",
    description="Retrieve details of a specific ticket",
)
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
):
    """
    Get a ticket by ID.
    
    Args:
        ticket_id: Ticket identifier
        db: Database session
        
    Returns:
        TicketResponse with ticket details
        
    Raises:
        HTTPException: 404 if ticket not found
        HTTPException: 500 if database operation fails
    """
    try:
        service = TicketService(db)
        ticket = service.get_ticket(ticket_id)
        if ticket is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with ID '{ticket_id}' not found",
            )
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve ticket: {str(e)}",
        )


@router.get(
    "",
    response_model=TicketListResponse,
    status_code=status.HTTP_200_OK,
    summary="List tickets",
    description="List tickets with optional filters and pagination",
)
def list_tickets(
    theater_name: Optional[str] = None,
    user_id: Optional[str] = None,
    movie_title: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    List tickets with filters.
    
    Args:
        theater_name: Filter by theater name
        user_id: Filter by user ID
        movie_title: Filter by movie title
        status: Filter by ticket status
        limit: Maximum number of tickets to return (1-1000)
        offset: Number of tickets to skip
        db: Database session
        
    Returns:
        TicketListResponse with list of tickets
        
    Raises:
        HTTPException: 400 if invalid query parameters
        HTTPException: 500 if database operation fails
    """
    try:
        # Validate limit
        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 1000",
            )
        
        # Validate offset
        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset must be non-negative",
            )
        
        service = TicketService(db)
        return service.list_tickets(
            theater_name=theater_name,
            user_id=user_id,
            movie_title=movie_title,
            status=status,
            limit=limit,
            offset=offset,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tickets: {str(e)}",
        )

