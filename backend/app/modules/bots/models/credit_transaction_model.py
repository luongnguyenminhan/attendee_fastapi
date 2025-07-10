import random
import string
from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.core.base_model import BaseEntity


class CreditTransaction(BaseEntity, table=True):
    __tablename__ = "credit_transactions"

    # Core fields
    organization_id: UUID = Field(foreign_key="organizations.id", index=True)
    bot_id: Optional[UUID] = Field(foreign_key="bots.id", index=True, default=None)

    # Credit amounts (in centicredits - 1/100th of a credit)
    centicredits_before: int = Field()
    centicredits_after: int = Field()
    centicredits_delta: int = Field(index=True)  # Positive = credit added, Negative = credit used

    # Transaction relationships
    parent_transaction_id: Optional[UUID] = Field(foreign_key="credit_transactions.id", index=True, default=None)

    # Payment integration
    stripe_payment_intent_id: Optional[str] = Field(default=None, max_length=255, unique=True)

    # Description and metadata
    description: Optional[str] = Field(default=None, max_length=1000)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "ctr_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    organization: "Organization" = Relationship(back_populates="credit_transactions")
    bot: Optional["Bot"] = Relationship(back_populates="credit_transactions")
    parent_transaction: Optional["CreditTransaction"] = Relationship(
        back_populates="child_transactions",
        sa_relationship_kwargs={"remote_side": "CreditTransaction.id"},
    )
    child_transactions: list["CreditTransaction"] = Relationship(
        back_populates="parent_transaction",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    def credits_delta(self) -> float:
        """Get credit delta in actual credits (not centicredits)"""
        return self.centicredits_delta / 100.0

    def credits_before(self) -> float:
        """Get credits before transaction in actual credits"""
        return self.centicredits_before / 100.0

    def credits_after(self) -> float:
        """Get credits after transaction in actual credits"""
        return self.centicredits_after / 100.0

    def is_credit_addition(self) -> bool:
        """Check if this transaction adds credits"""
        return self.centicredits_delta > 0

    def is_credit_deduction(self) -> bool:
        """Check if this transaction deducts credits"""
        return self.centicredits_delta < 0

    def is_bot_usage(self) -> bool:
        """Check if this transaction is for bot usage"""
        return self.bot_id is not None

    def is_stripe_payment(self) -> bool:
        """Check if this transaction is from a Stripe payment"""
        return self.stripe_payment_intent_id is not None

    def is_root_transaction(self) -> bool:
        """Check if this is a root transaction (no parent)"""
        return self.parent_transaction_id is None

    def is_child_transaction(self) -> bool:
        """Check if this is a child transaction"""
        return self.parent_transaction_id is not None

    def get_transaction_type(self) -> str:
        """Get human-readable transaction type"""
        if self.is_stripe_payment():
            return "Payment"
        elif self.is_bot_usage():
            return "Bot Usage"
        elif self.is_credit_addition():
            return "Credit Addition"
        elif self.is_credit_deduction():
            return "Credit Deduction"
        else:
            return "Other"

    def get_display_amount(self) -> str:
        """Get formatted amount for display"""
        amount = abs(self.credits_delta())
        if self.is_credit_addition():
            return f"+{amount:.2f}"
        else:
            return f"-{amount:.2f}"

    def get_description_or_default(self) -> str:
        """Get description or generate a default one"""
        if self.description:
            return self.description

        if self.is_bot_usage() and self.bot:
            return f"Bot usage for {self.bot.name}"
        elif self.is_stripe_payment():
            return "Credit purchase"
        elif self.is_credit_addition():
            return "Credits added"
        elif self.is_credit_deduction():
            return "Credits used"
        else:
            return "Transaction"

    def __repr__(self):
        amount = self.get_display_amount()
        return f"<CreditTransaction {self.object_id}: {amount} credits>"


class CreditTransactionManager:
    """Manager class for credit transactions with business logic"""

    @staticmethod
    def create_transaction(
        organization: "Organization",
        centicredits_delta: int,
        bot: Optional["Bot"] = None,
        description: Optional[str] = None,
        stripe_payment_intent_id: Optional[str] = None,
        parent_transaction: Optional["CreditTransaction"] = None,
    ) -> "CreditTransaction":
        """Create a new credit transaction with proper balance tracking"""

        # Get current balance
        centicredits_before = organization.centicredits
        centicredits_after = centicredits_before + centicredits_delta

        # Create transaction
        transaction = CreditTransaction(
            organization_id=organization.id,
            bot_id=bot.id if bot else None,
            centicredits_before=centicredits_before,
            centicredits_after=centicredits_after,
            centicredits_delta=centicredits_delta,
            description=description,
            stripe_payment_intent_id=stripe_payment_intent_id,
            parent_transaction_id=parent_transaction.id if parent_transaction else None,
        )

        # Update organization balance
        organization.centicredits = centicredits_after

        return transaction

    @staticmethod
    def get_organization_balance(organization: "Organization") -> float:
        """Get organization's current credit balance"""
        return organization.credits()

    @staticmethod
    def get_total_credits_purchased(organization: "Organization") -> float:
        """Get total credits purchased by organization"""

        # This would need to be implemented with actual database session
        # For now, return placeholder
        return 0.0

    @staticmethod
    def get_total_credits_used(organization: "Organization") -> float:
        """Get total credits used by organization"""

        # This would need to be implemented with actual database session
        # For now, return placeholder
        return 0.0

    @staticmethod
    def can_afford_operation(organization: "Organization", cost_centicredits: int) -> bool:
        """Check if organization can afford an operation"""
        return organization.centicredits >= cost_centicredits
