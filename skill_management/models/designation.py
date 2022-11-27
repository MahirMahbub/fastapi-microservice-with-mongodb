from beanie import Document


class Designation(Document):
    id: int
    designation: str

    class Settings:
        use_revision = True
        use_state_management = True
        validate_on_save = True

