from alembic import op
import sqlalchemy as sa

revision = "b25c5f2f4590"
down_revision = "e496b0a9ff29"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("payments", sa.Column("razorpay_order_id", sa.String(100), nullable=True))
    op.add_column("payments", sa.Column("razorpay_payment_id", sa.String(100), nullable=True))
    op.create_unique_constraint("uq_payments_razorpay_order_id", "payments", ["razorpay_order_id"])
    op.create_unique_constraint("uq_payments_razorpay_payment_id", "payments", ["razorpay_payment_id"])

def downgrade() -> None:
    op.drop_constraint("uq_payments_razorpay_payment_id", "payments", type_="unique")
    op.drop_constraint("uq_payments_razorpay_order_id", "payments", type_="unique")
    op.drop_column("payments", "razorpay_payment_id")
    op.drop_column("payments", "razorpay_order_id")
