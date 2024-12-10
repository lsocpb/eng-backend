from sqlalchemy.orm import Session

from db_management.dto import PersonalRegisterForm, CompanyRegisterForm
from db_management.models import UserBilling, User, CompanyBilling
from response_models.auth_responses import hash_password
from utils.constants import UserAccountType


def create_personal_account(session: Session, dto: PersonalRegisterForm) -> User:
    billing_details = UserBilling(
        first_name=dto.billing_details.first_name,
        last_name=dto.billing_details.last_name,
        address=dto.billing_details.address,
        postal_code=dto.billing_details.postal_code,
        city=dto.billing_details.city,
        country=dto.billing_details.country,
        state=dto.billing_details.state,
        phone_number=dto.billing_details.phone_number
    )

    user = User(
        password_hash=hash_password(dto.account_details.password),
        username=dto.account_details.username,
        email=dto.account_details.email,
        billing_details=billing_details,
        account_type=UserAccountType.PERSONAL
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_company_account(session: Session, dto: CompanyRegisterForm) -> User:
    billing_details = CompanyBilling(
        name=dto.billing_details.company_name,
        tax_id=dto.billing_details.tax_id,
        address=dto.billing_details.address,
        postal_code=dto.billing_details.postal_code,
        city=dto.billing_details.city,
        country=dto.billing_details.country,
        state=dto.billing_details.state,
        phone_number=dto.billing_details.phone_number,
        bank_account=dto.billing_details.bank_account
    )

    user = User(
        password_hash=hash_password(dto.account_details.password),
        username=dto.account_details.username,
        email=dto.account_details.email,
        billing_details=billing_details,
        account_type=UserAccountType.BUSINESS_UNVERIFIED
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user
