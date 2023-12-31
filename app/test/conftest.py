import pytest
from decouple import config
from app.db.connection import Session
from passlib.context import CryptContext
from app.db.models import User as UserModel
from app.db.models import Category as CategoryModel
from app.db.models import Expense as ExpenseModel
from app.use_cases.user import UserUseCases
from app.schemas.user import User

SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')
cryptContext = CryptContext(schemes=['sha256_crypt'])

@pytest.fixture()
def db_session():
    try:
        session = Session()
        yield session
    finally:
        session.close()

@pytest.fixture()
def user_on_db(db_session):
    user = UserModel(
        username='username',
        password=cryptContext.hash('pass#')
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    yield user

    db_session.delete(user)
    db_session.commit()

@pytest.fixture()
def another_user_on_db(db_session):
    user = UserModel(
        username='username2',
        password=cryptContext.hash('pass#')
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    yield user

    db_session.delete(user)
    db_session.commit()

@pytest.fixture()
def authenticated_user(db_session):
    user = UserModel(
        username='authenticated_user',
        password=cryptContext.hash('pass#')
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    uc = UserUseCases(db_session=db_session)
    token_data = uc.user_login(user=User(username=user.username,password='pass#'), expires_in=1)

    headers = {"Authorization": f"Bearer {token_data.access_token}"}

    data = [headers, user]

    yield data

    db_session.delete(user)
    db_session.commit()

@pytest.fixture()
def category_on_db(db_session, authenticated_user):
    user = authenticated_user[1]

    category = CategoryModel(name='category 1', user_id=user.id)
    
    db_session.add(category)
    db_session.commit()

    db_session.refresh(category)

    data = [authenticated_user[0], user, category]

    yield data

    db_session.delete(category)
    db_session.commit()


@pytest.fixture()
def categories_on_db(db_session, authenticated_user):
    user = authenticated_user[1]

    new_categories = [
        CategoryModel(name='category 1', user_id=user.id),
        CategoryModel(name='category 2', user_id=user.id),
        CategoryModel(name='category 3', user_id=user.id),
        CategoryModel(name='category 4', user_id=user.id)
    ]

    for category in new_categories:
        db_session.add(category)
    db_session.commit()

    for category in new_categories:
        db_session.refresh(category)

    data = [authenticated_user[0], user, new_categories]

    yield data

    for category in new_categories:
        db_session.delete(category)
    db_session.commit()

@pytest.fixture()
def expense_on_db(db_session, category_on_db):
    token = category_on_db[0]
    user = category_on_db[1]
    category = category_on_db[2]

    expense = ExpenseModel(description='Expense Description', value=99.99, category_id=category.id)

    db_session.add(expense)
    db_session.commit()
    db_session.refresh(expense)

    data = [token, user, expense, category]

    yield data

    db_session.delete(expense)
    db_session.commit()

@pytest.fixture()
def expenses_on_db(db_session, category_on_db):
    token = category_on_db[0]
    user = category_on_db[1]
    category = category_on_db[2]

    new_expenses = [
        ExpenseModel(description='Expense Description 1', value=99.99, category_id=category.id),
        ExpenseModel(description='Expense Description 2', value=89.99, category_id=category.id),
        ExpenseModel(description='Expense Description 3', value=79.99, category_id=category.id),
        ExpenseModel(description='Expense Description 4', value=69.99, category_id=category.id)
    ]

    for expense in new_expenses:
        db_session.add(expense)
    db_session.commit()

    for expense in new_expenses:
        db_session.refresh(expense)

    data = [token, user, new_expenses]

    yield data

    for expense in new_expenses:
        db_session.delete(expense)
    db_session.commit()