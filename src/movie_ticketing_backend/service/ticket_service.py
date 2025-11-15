"""Ticket service for business logic."""

import uuid
from typing import Optional
from sqlalchemy.orm import Session

from movie_ticketing_backend.db.repository import TicketRepository
from movie_ticketing_backend.scheme.ticket import (
    IssueTicketRequest,
    IssueTicketResponse,
    IssueTicketSummary,
    RefundTicketRequest,
    RefundTicketResponse,
    TicketResponse,
    TicketListResponse,
)
from movie_ticketing_backend.util.idempotency import idempotency_cache


class TicketService:
    """Service class for ticket operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the service with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.repository = TicketRepository(db)
    
    def issue_tickets(
        self,
        request: IssueTicketRequest,
        idempotency_key: Optional[str] = None,
    ) -> IssueTicketResponse:
        """
        Issue new tickets based on the request.
        
        Args:
            request: Issue ticket request data
            idempotency_key: Optional idempotency key for duplicate prevention
            
        Returns:
            IssueTicketResponse with created ticket IDs
            
        Raises:
            ValueError: If idempotency key conflict occurs
        """
        # Check idempotency if key is provided
        if idempotency_key:
            request_data = request.model_dump()
            is_duplicate, cached_response = idempotency_cache.check_and_store(
                idempotency_key, request_data
            )
            if is_duplicate and cached_response:
                return IssueTicketResponse(**cached_response)
        
        # Create tickets
        ticket_ids = []
        for _ in range(request.quantity):
            ticket_id = str(uuid.uuid4())
            self.repository.create_ticket(
                ticket_id=ticket_id,
                theater_name=request.theater_name,
                user_id=request.user_id,
                movie_title=request.movie_title,
                price_krw=request.price_krw,
                memo=request.memo,
            )
            ticket_ids.append(ticket_id)
        
        # Prepare response
        response = IssueTicketResponse(
            ticket_ids=ticket_ids,
            count=len(ticket_ids),
            summary=IssueTicketSummary(
                theater_name=request.theater_name,
                movie_title=request.movie_title,
                price_krw=request.price_krw,
            ),
        )
        
        # Store response in idempotency cache
        if idempotency_key:
            idempotency_cache.store_response(
                idempotency_key, response.model_dump()
            )
        
        return response
    
    def refund_tickets(self, request: RefundTicketRequest) -> RefundTicketResponse:
        """
        Refund tickets based on the request.
        
        Args:
            request: Refund ticket request data
            
        Returns:
            RefundTicketResponse with refund results
        """
        refunded = []
        already_canceled = []
        not_found = []
        
        for ticket_id in request.ticket_ids:
            ticket = self.repository.get_ticket_by_id(ticket_id)
            
            if ticket is None:
                not_found.append(ticket_id)
            elif ticket.status == "canceled":
                already_canceled.append(ticket_id)
            elif ticket.status == "issued":
                canceled_ticket = self.repository.cancel_ticket(ticket_id)
                if canceled_ticket:
                    refunded.append(ticket_id)
        
        return RefundTicketResponse(
            refunded=refunded,
            already_canceled=already_canceled,
            not_found=not_found,
        )
    
    def get_ticket(self, ticket_id: str) -> Optional[TicketResponse]:
        """
        Get a single ticket by ID.
        
        Args:
            ticket_id: Ticket identifier
            
        Returns:
            TicketResponse if found, None otherwise
        """
        ticket = self.repository.get_ticket_by_id(ticket_id)
        if ticket:
            return TicketResponse.model_validate(ticket)
        return None
    
    def list_tickets(
        self,
        theater_name: Optional[str] = None,
        user_id: Optional[str] = None,
        movie_title: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> TicketListResponse:
        """
        List tickets with optional filters and pagination.
        
        Args:
            theater_name: Filter by theater name
            user_id: Filter by user ID
            movie_title: Filter by movie title
            status: Filter by ticket status
            limit: Maximum number of tickets to return
            offset: Number of tickets to skip
            
        Returns:
            TicketListResponse with list of tickets and pagination info
        """
        tickets, total = self.repository.list_tickets(
            theater_name=theater_name,
            user_id=user_id,
            movie_title=movie_title,
            status=status,
            limit=limit,
            offset=offset,
        )
        
        ticket_responses = [
            TicketResponse.model_validate(ticket) for ticket in tickets
        ]
        
        return TicketListResponse(
            tickets=ticket_responses,
            total=total,
            limit=limit,
            offset=offset,
        )

