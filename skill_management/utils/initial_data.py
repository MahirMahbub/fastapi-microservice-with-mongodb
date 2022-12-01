import csv

from skill_management.enums import PlanTypeEnum, SkillTypeEnum, StatusEnum, UserStatusEnum, SkillCategoryEnum, \
    DesignationStatusEnum, GenderEnum, FileTypeEnum, ProfileStatusEnum
from skill_management.models.designation import Designations
from skill_management.models.enums import EnumInitializer, PlanType, Status, UserStatus, SkillCategory, SkillType, \
    DesignationStatus, Gender, FileType, ProfileStatus
from skill_management.models.skill import Skills


async def initialize_database() -> None:
    initializer_marker = await EnumInitializer.find({}).to_list()
    if not initializer_marker:
        enum_initializer = EnumInitializer(is_uploaded=False)
        await enum_initializer.insert()
    else:
        enum_initializer = initializer_marker[0]
    if enum_initializer.is_uploaded:
        return
    """
    Insert Plan_Type Data
    """
    await PlanType.insert_many([PlanType(id=data.value, name=data.name) for data in PlanTypeEnum])

    """
    Insert Status Data
    """
    await Status.insert_many([Status(id=data.value, name=data.name) for data in StatusEnum])

    """
    Insert UserStatus Data
    """
    await UserStatus.insert_many([UserStatus(id=data.value, name=data.name) for data in UserStatusEnum])

    """
    Insert SkillCategory Data
    """
    await SkillCategory.insert_many([SkillCategory(id=data.value, name=data.name) for data in SkillCategoryEnum])

    """
    Insert SkillType Data
    """
    await SkillType.insert_many([SkillType(id=data.value, name=data.name) for data in SkillTypeEnum])

    """
    Insert DesignationStatus Data
    """
    await DesignationStatus.insert_many(
        [DesignationStatus(id=data.value, name=data.name) for data in DesignationStatusEnum])

    """
    Insert Gender Data
    """
    await Gender.insert_many([Gender(id=data.value, name=data.name) for data in GenderEnum])

    """
    Insert FileType Data
    """
    await FileType.insert_many([FileType(id=data.value, name=data.name) for data in FileTypeEnum])

    """
    Insert ProfileStatus data
    """
    await ProfileStatus.insert_many([ProfileStatus(id=data.value, name=data.name) for data in ProfileStatusEnum])

    """
    Insert Designation
    """
    with open("skill_management/static/data/designations.csv", 'r') as file:
        csv_reader = csv.DictReader(file)
        skill_data = []
        for row in csv_reader:
            skill_data.append(Designations.parse_obj(row))
        await Designations.insert_many(skill_data)

    """
    Insert Designation
    """
    with open("skill_management/static/data/skills.csv", 'r') as file:
        csv_reader = csv.DictReader(file)
        skill_data = []
        for row in csv_reader:
            row['skill_categories'] = [int(data) for data in row['skill_categories'].split(",")]
            skill_data.append(Skills.parse_obj(row))  # type: ignore
        await Skills.insert_many(skill_data)  # type: ignore

    """
    Change Initiating Value
    """
    enum_initializer.is_uploaded = True
    await enum_initializer.save()
