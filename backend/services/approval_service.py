from schemas.approval import ApprovalStatus, TravelApproval


class TravelApprovalService:
    """Manages in-memory approval state for travel recommendations."""

    def __init__(self):
        self._approvals: dict[str, TravelApproval] = {}
        self._next_approval_number = 1

    def create_pending_approval(
        self,
        session_id: str,
        selected_recommendation_ids: list[str],
    ) -> TravelApproval:
        """Create and store a pending approval for selected recommendations."""
        approval = TravelApproval(
            approval_id=f"approval-{self._next_approval_number}",
            session_id=session_id,
            selected_recommendation_ids=selected_recommendation_ids,
        )
        self._next_approval_number += 1
        self._approvals[approval.approval_id] = approval
        return approval

    def approve(self, session_id: str, approval_id: str) -> TravelApproval:
        """Approve a pending approval belonging to the supplied session."""
        return self._resolve(session_id, approval_id, ApprovalStatus.APPROVED)

    def reject(self, session_id: str, approval_id: str) -> TravelApproval:
        """Reject a pending approval belonging to the supplied session."""
        return self._resolve(session_id, approval_id, ApprovalStatus.REJECTED)

    def _resolve(
        self,
        session_id: str,
        approval_id: str,
        status: ApprovalStatus,
    ) -> TravelApproval:
        approval = self._approvals.get(approval_id)
        if approval is None:
            raise ValueError("Unknown approval ID")
        if approval.session_id != session_id:
            raise ValueError("Approval does not belong to this session")
        if approval.status is not ApprovalStatus.PENDING:
            raise ValueError("Approval has already been resolved")

        resolved_approval = approval.model_copy(update={"status": status})
        self._approvals[approval_id] = resolved_approval
        return resolved_approval
