from lazyopenai.types import BaseTool
from loguru import logger
from mortgage import Loan
from pydantic import Field


class LoanTool(BaseTool):
    """
    Calculates and summarizes loan details based on provided parameters.

    Attributes:
        principal (float): The amount of money borrowed.
        interest (float): The annual interest rate as a decimal between 0 and 1.
        term (int): The loan duration in years.

    Note:
        - `term_unit` is assumed to be 'years'.
        - `compounded` is assumed to be 'monthly'.
        - `currency` is assumed to be '$'.
    """

    principal: float = Field(..., description="The amount of money borrowed.")
    interest: float = Field(
        ...,
        description="The annual interest rate as a decimal between 0 and 1.",
    )
    term: int = Field(..., description="The loan duration in years.")

    def __call__(self) -> str:
        """
        Computes loan details and returns a formatted summary.

        Returns:
            str: A formatted summary of the loan details.
        """
        loan = Loan(
            principal=self.principal,
            interest=self.interest,
            term=self.term,
        )

        logger.info(self.model_dump())

        lines = [
            f"Original Balance: {loan._currency}{loan.principal:.2f}",
            f"Interest Rate: {loan.interest:.2f} %",
            f"APY: {loan.apy:.2f} %",
            f"APR: {loan.apr:.2f} %",
            f"Term: {loan.term:.2f} {loan.term_unit}",
            f"Monthly Payment: {loan._currency}{loan.monthly_payment:.2f}",
            f"Compound Frequency: {loan.compounded}",
            "",
            f"Total principal payments: {loan._currency}{loan.total_principal:.2f}",
            f"Total interest payments: {loan._currency}{loan.total_interest:.2f}",
            f"Total payments: {loan._currency}{loan.total_paid:.2f}",
            f"Interest to principal: {loan.interest_to_principle:.2f} %",
            f"Years to pay: {loan.years_to_pay:.2f}",
        ]

        res = "\n".join(lines)

        logger.info("Loan summary: {}", res)
        return res
