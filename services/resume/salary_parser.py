"""
==========================================================
AI JobAgent - Salary Parser
Author : Beere Vishnu Sai

Description:
    Parse and normalize salary information from
    resumes and job descriptions.
==========================================================
"""

import re
from typing import Dict, Optional

from utils import info, exception
from exceptions import SalaryParserError


# ==========================================================
# Currency Symbols
# ==========================================================

CURRENCY_SYMBOLS = {
    "₹": "INR",
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
}


# ==========================================================
# LPA Conversion
# ==========================================================

def lpa_to_amount(value: float) -> int:
    """
    Convert LPA to annual salary.
    """

    return int(value * 100000)


# ==========================================================
# Detect Currency
# ==========================================================

def detect_currency(text: str) -> str:
    """
    Detect salary currency.
    """

    for symbol, code in CURRENCY_SYMBOLS.items():

        if symbol in text:

            return code

    return ""


# ==========================================================
# Parse Salary
# ==========================================================

def parse_salary(text: str) -> Dict[str, Optional[int]]:
    """
    Parse salary text.
    """

    info("Parsing salary.")

    try:

        if not text:

            return {
                "text": "Not Mentioned",
                "currency": "",
                "min_salary": None,
                "max_salary": None,
            }

        salary = text.strip()

        lower = salary.lower()

        currency = detect_currency(salary)

        # --------------------------------------------------
        # ₹6-8 LPA
        # --------------------------------------------------

        match = re.search(

            r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*lpa",

            lower,

        )

        if match:

            return {

                "text": salary,

                "currency": "INR",

                "min_salary": lpa_to_amount(float(match.group(1))),

                "max_salary": lpa_to_amount(float(match.group(2))),

            }

        # --------------------------------------------------
        # ₹12 LPA
        # --------------------------------------------------

        match = re.search(

            r"(\d+(?:\.\d+)?)\s*lpa",

            lower,

        )

        if match:

            amount = lpa_to_amount(float(match.group(1)))

            return {

                "text": salary,

                "currency": "INR",

                "min_salary": amount,

                "max_salary": amount,

            }

        # --------------------------------------------------
        # 90k-120k
        # --------------------------------------------------

        match = re.search(

            r"(\d+)\s*k\s*[-–]\s*(\d+)\s*k",

            lower,

        )

        if match:

            return {

                "text": salary,

                "currency": currency,

                "min_salary": int(match.group(1)) * 1000,

                "max_salary": int(match.group(2)) * 1000,

            }

        # --------------------------------------------------
        # Single Amount (Only if not a 4-digit year without currency symbol)
        # --------------------------------------------------

        match = re.search(

            r"(\d[\d,]*)",

            salary,

        )

        if match:

            clean_str = re.sub(r"[^\d]", "", salary)
            is_probably_year = len(clean_str) == 4 and clean_str.startswith(("19", "20"))

            if currency or not is_probably_year:

                amount = int(

                    match.group(1).replace(",", "")

                )

                return {

                    "text": salary,

                    "currency": currency,

                    "min_salary": amount,

                    "max_salary": amount,

                }

        return {

            "text": salary,

            "currency": currency,

            "min_salary": None,

            "max_salary": None,

        }

    except Exception as e:

        exception("Salary parsing failed.")

        raise SalaryParserError(str(e))


# ==========================================================
# Salary Match
# ==========================================================

def match_salary(

    expected_salary: Optional[int],

    offered_salary: Optional[int],

) -> float:
    """
    Calculate salary match percentage.
    """

    if expected_salary is None:

        return 100.0

    if offered_salary is None:

        return 100.0

    if offered_salary >= expected_salary:

        return 100.0

    score = (

        offered_salary

        /

        expected_salary

    ) * 100

    return round(

        max(score, 0),

        2,

    )


# ==========================================================
# Salary Range
# ==========================================================

def salary_range(data: Dict) -> str:
    """
    Convert salary dictionary to readable string.
    """

    minimum = data.get("min_salary")

    maximum = data.get("max_salary")

    currency = data.get("currency", "")

    if minimum is None:

        return "Not Mentioned"

    if minimum == maximum:

        return f"{currency} {minimum:,}"

    return f"{currency} {minimum:,} - {maximum:,}"


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    samples = [

        "₹6-8 LPA",

        "₹12 LPA",

        "$90k-$120k",

        "$75000",

        "Not Mentioned",

        "",

    ]

    for sample in samples:

        result = parse_salary(sample)

        print(result)

        print(salary_range(result))

        print("-" * 40)

    print(

        match_salary(

            800000,

            700000,

        )

    )