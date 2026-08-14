import pytest

from schemas.approval import ApprovalStatus
from services.approval_service import TravelApprovalService


class TestTravelApprovalService:
    """Tests for in-memory travel recommendation approval state."""

    def setup_method(self):
        self.service = TravelApprovalService()

    def test_creates_pending_approval(self):
        approval = self.service.create_pending_approval(
            "session-1",
            ["flight-1", "hotel-1"],
        )

        assert approval.approval_id == "approval-1"
        assert approval.session_id == "session-1"
        assert approval.selected_recommendation_ids == ["flight-1", "hotel-1"]
        assert approval.status is ApprovalStatus.PENDING

    def test_approves_pending_approval(self):
        pending = self.service.create_pending_approval("session-1", ["recommendation-1"])

        approval = self.service.approve("session-1", pending.approval_id)

        assert approval.status is ApprovalStatus.APPROVED

    def test_rejects_pending_approval(self):
        pending = self.service.create_pending_approval("session-1", ["recommendation-1"])

        approval = self.service.reject("session-1", pending.approval_id)

        assert approval.status is ApprovalStatus.REJECTED

    @pytest.mark.parametrize("method_name", ["approve", "reject"])
    def test_rejects_unknown_approval(self, method_name):
        method = getattr(self.service, method_name)

        with pytest.raises(ValueError, match="Unknown approval ID"):
            method("session-1", "missing-approval")

    def test_rejects_approval_for_another_session(self):
        pending = self.service.create_pending_approval("session-1", ["recommendation-1"])

        with pytest.raises(ValueError, match="does not belong to this session"):
            self.service.approve("session-2", pending.approval_id)

    @pytest.mark.parametrize("method_name", ["approve", "reject"])
    def test_cannot_resolve_an_approval_twice(self, method_name):
        pending = self.service.create_pending_approval("session-1", ["recommendation-1"])
        self.service.approve("session-1", pending.approval_id)
        method = getattr(self.service, method_name)

        with pytest.raises(ValueError, match="already been resolved"):
            method("session-1", pending.approval_id)
