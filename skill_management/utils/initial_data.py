from skill_management.models.enums import EnumInitializer, PlanType, Status, UserStatus, SkillCategory, SkillType, \
    DesignationStatus, Gender, FileType


async def initialize_database() -> None:
    initializer_marker = await EnumInitializer.find({}).to_list()
    if not initializer_marker:
        enum_initializer = EnumInitializer(is_uploaded=False)
        await enum_initializer.insert()
    else:
        enum_initializer = initializer_marker[0]
    if enum_initializer.is_uploaded:
        return
    # Insert Plan_Type Data
    await PlanType.insert_many([PlanType(id=1, name="course"),
                                PlanType(id=2, name="exam")])

    await Status.insert_many([Status(id=1, name="active"),
                              Status(id=2, name="cancel"),
                              Status(id=3, name="delete")])

    await UserStatus.insert_many([UserStatus(id=1, name="active"),
                                  UserStatus(id=2, name="delete")])

    await SkillCategory.insert_many([SkillCategory(id=1, name="frontend"),
                                     SkillCategory(id=2, name="backend"),
                                     SkillCategory(id=3, name="devops"),
                                     SkillCategory(id=4, name="qa"),
                                     SkillCategory(id=5, name="database"),
                                     SkillCategory(id=6, name="network"),
                                     SkillCategory(id=7, name="fullstack")])
    await SkillType.insert_many([SkillType(id=1, name="core_skill"),
                                 SkillType(id=2, name="soft_skill")])
    await DesignationStatus.insert_many([DesignationStatus(id=1, name="active"),
                                         DesignationStatus(id=2, name="inactive")])
    await Gender.insert_many([Gender(id=1, name="male"),
                              Gender(id=2, name="female"),
                              Gender(id=3, name="others")])

    await FileType.insert_many([FileType(id=1, name="picture"),
                                FileType(id=2, name="resume"),
                                FileType(id=3, name="letter"),
                                FileType(id=4, name="certificate")])

    enum_initializer.is_uploaded = True
    await enum_initializer.save()
