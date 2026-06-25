import sqlalchemy

membership_role = sqlalchemy.Enum("owner", "admin", "member", name="membership_role")
