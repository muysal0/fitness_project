import pytest
from src.membership import Member

def test_create_member_successfully():
    # Arrange (Hazırlık)
    member_id = 1
    name = "Ali Veli"
    m_type = "standard"

    # Act (Eylem)
    member = Member(member_id, name, m_type)

    # Assert (Doğrulama)
    assert member.member_id == 1
    assert member.name == "Ali Veli"
    assert member.membership_type == "standard"