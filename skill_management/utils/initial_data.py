from skill_management.models.designation import Designations
from skill_management.models.enums import EnumInitializer, PlanType, Status, UserStatus, SkillCategory, SkillType, \
    DesignationStatus, Gender, FileType, ProfileStatus
import csv


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
    await PlanType.insert_many([PlanType(id=1, name="course"),
                                PlanType(id=2, name="exam")])
    """
    Insert Status Data
    """
    await Status.insert_many([Status(id=1, name="active"),
                              Status(id=2, name="cancel"),
                              Status(id=3, name="delete")])
    """
    Insert UserStatus Data
    """
    await UserStatus.insert_many([UserStatus(id=1, name="active"),
                                  UserStatus(id=2, name="delete")])
    """
    Insert SkillCategory Data
    """
    await SkillCategory.insert_many([SkillCategory(id=1, name="frontend"),
                                     SkillCategory(id=2, name="backend"),
                                     SkillCategory(id=3, name="devops"),
                                     SkillCategory(id=4, name="qa"),
                                     SkillCategory(id=5, name="database"),
                                     SkillCategory(id=6, name="network"),
                                     SkillCategory(id=7, name="fullstack")])
    """
    Insert SkillType Data
    """
    await SkillType.insert_many([SkillType(id=1, name="core_skill"),
                                 SkillType(id=2, name="soft_skill")])

    """
    Insert DesignationStatus Data
    """
    await DesignationStatus.insert_many([DesignationStatus(id=1, name="active"),
                                         DesignationStatus(id=2, name="inactive")])
    """
    Insert Gender Data
    """
    await Gender.insert_many([Gender(id=1, name="male"),
                              Gender(id=2, name="female"),
                              Gender(id=3, name="others")])
    """
    Insert FileType Data
    """

    await FileType.insert_many([FileType(id=1, name="picture"),
                                FileType(id=2, name="resume"),
                                FileType(id=3, name="letter"),
                                FileType(id=4, name="certificate")])

    """
    Insert ProfileStatus data
    """
    await ProfileStatus.insert_many([ProfileStatus(id=1, name="full_time"),
                                     ProfileStatus(id=2, name="part_time"),
                                     ProfileStatus(id=3, name="delete"),
                                     ProfileStatus(id=4, name="inactive")])
    """
    Insert Designation
    """
    with open("skill_management/static/data/designations.csv", 'r') as file:
        csv_reader = csv.DictReader(file)
        designation_data = []
        for row in csv_reader:
            designation_data.append(Designations.parse_obj(row))
        await Designations.insert_many(designation_data)
    """
    Change Initiating Value
    """
    enum_initializer.is_uploaded = True
    await enum_initializer.save()
