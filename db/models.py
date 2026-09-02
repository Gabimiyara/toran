from sqlalchemy import (
    Column,
    Date,
    Time,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    ForeignKeyConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(100), nullable=False)

    phone = Column(String(20), nullable=False, unique=True)

    email = Column(String(255), nullable=True, unique=True)

    password_hash = Column(String(255), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )


class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(100), nullable=False)

    timezone = Column(String(50), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )


class GroupMember(Base):
    __tablename__ = "group_members"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "group_id",
            name="uq_group_member_user_group"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("groups.id"),
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False,
        default="MEMBER"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    joined_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    left_at = Column(
        DateTime(timezone=True),
        nullable=True
    )


class Lesson(Base):
    """
    Permanent definition of a recurring lesson.

    This table represents the lesson itself,
    not a specific occurrence on a specific date.
    """

    __tablename__ = "lessons"

    __table_args__ = (
        UniqueConstraint(
            "id",
            "group_id",
            name="uq_lesson_id_group"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("groups.id"),
        nullable=False
    )

    name = Column(
        String(100),
        nullable=False
    )

    scheduled_start_time = Column(
        Time,
        nullable=False
    )
    
    pickup_location_id = Column(
        UUID(as_uuid=True),
        ForeignKey("locations.id"),
        nullable=True
    )

    lesson_location_id = Column(
        UUID(as_uuid=True),
        ForeignKey("locations.id"),
        nullable=True
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )


class LessonParticipant(Base):
    __tablename__ = "lesson_participants"

    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "user_id",
            name="uq_lesson_participant"
        ),

        ForeignKeyConstraint(
            ["lesson_id", "group_id"],
            ["lessons.id", "lessons.group_id"],
            name="fk_lesson_participant_lesson_group"
        ),

        ForeignKeyConstraint(
            ["user_id", "group_id"],
            ["group_members.user_id", "group_members.group_id"],
            name="fk_lesson_participant_member"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    lesson_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    group_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    joined_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )


class Roster(Base):
    """
    Circular duty roster for a specific lesson.

    Each participant has one roster entry.
    next_roster_id points to the next participant
    in the circular rotation.
    """

    __tablename__ = "roster"

    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "user_id",
            name="uq_roster_lesson_user"
        ),

        UniqueConstraint(
            "id",
            "lesson_id",
            name="uq_roster_id_lesson"
        ),

        ForeignKeyConstraint(
            ["lesson_id", "user_id"],
            ["lesson_participants.lesson_id", "lesson_participants.user_id"],
            name="fk_roster_participant"
        ),

        ForeignKeyConstraint(
            ["next_roster_id", "lesson_id"],
            ["roster.id", "roster.lesson_id"],
            name="fk_roster_next_same_lesson"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id"),
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    next_roster_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )


class LessonWeek(Base):
    """
    Represents one calendar week of a recurring lesson.

    Used to track the duty holder for that week
    and the weekly duty confirmation.
    """

    __tablename__ = "lesson_weeks"

    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "week_start_date",
            name="uq_lesson_week"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id"),
        nullable=False
    )

    week_start_date = Column(
        Date,
        nullable=False
    )

    roster_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roster.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )


class LessonOccurrence(Base):
    """
    Represents one specific occurrence of a recurring lesson.

    Example:
    Lesson = "Evening Torah Lesson"
    Occurrence = 2026-09-02
    """

    __tablename__ = "lesson_occurrences"

    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "date",
            name="uq_lesson_occurrence"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id"),
        nullable=False
    )

    date = Column(
        Date,
        nullable=False
    )

    scheduled_start_time = Column(
        Time,
        nullable=False
    )

    actual_start_time = Column(
        Time,
        nullable=True
    )

    status = Column(
        String(30),
        nullable=False,
        default="SCHEDULED"
    )
    
    cancellation_reason = Column(
        String(500),
        nullable=True
    )
    
    cancelled_by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )


class DutyAssignment(Base):
    """
    Represents the actual person performing the duty
    for one specific lesson occurrence.

    roster_id = the roster position that was expected
    user_id   = the person who actually performed the duty

    user_id can be NULL when the expected duty holder
    has not yet been replaced.
    """

    __tablename__ = "duty_assignments"

    __table_args__ = (
        UniqueConstraint(
            "lesson_occurrence_id",
            name="uq_duty_assignment_occurrence"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    lesson_occurrence_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lesson_occurrences.id"),
        nullable=False
    )

    roster_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roster.id"),
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    

class Location(Base):
    __tablename__ = "locations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String(100),
        nullable=False
    )

    latitude = Column(
        Float,
        nullable=False
    )

    longitude = Column(
        Float,
        nullable=False
    )

    radius = Column(
        Integer,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )


class DutyConfirmation(Base):
    """
    Represents the current confirmation state
    of the duty holder for a specific lesson week.

    This is operational state, not historical data.
    The current duty holder is determined by LessonWeek.roster_id.
    """

    __tablename__ = "duty_confirmations"

    __table_args__ = (
        UniqueConstraint(
            "lesson_week_id",
            name="uq_duty_confirmation_week"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    lesson_week_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lesson_weeks.id"),
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="PENDING"
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )  
    

class SwapRequest(Base):
    """
    Represents an active request to swap a duty.

    This table stores only pending swap requests.
    Once the request is approved, rejected, or cancelled,
    the row is removed.

    Historical swap data will be stored separately.
    """

    __tablename__ = "swap_requests"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id"),
        nullable=False
    )

    requester_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    target_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    type = Column(
        String(10),
        nullable=False
    )

    date = Column(
        Date,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    
class LessonAdmin(Base):
    """
    Represents a user who has administrative permissions
    for a specific lesson.

    Group admins are automatically considered admins
    of all lessons in their group and do not need a row here.
    """

    __tablename__ = "lesson_admins"

    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "user_id",
            name="uq_lesson_admin"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id"),
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    

class SystemSetting(Base):
    """
    Stores operational settings for a specific lesson.

    Each lesson has exactly one settings record.
    Location/GPS configuration is determined by the
    locations configured on the Lesson itself.
    """

    __tablename__ = "system_settings"

    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            name="uq_system_setting_lesson"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id"),
        nullable=False
    )

    duty_notification_minutes = Column(
        Integer,
        nullable=False
    )

    backup_trigger_minutes = Column(
        Integer,
        nullable=False
    )

    backup_response_timeout_minutes = Column(
        Integer,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    
class ScoreRecord(Base):
    """
    Represents the score awarded for one duty assignment.

    Each duty assignment can have only one score record.
    The user who actually performed the duty receives the score.
    """

    __tablename__ = "score_records"

    __table_args__ = (
        UniqueConstraint(
            "duty_assignment_id",
            name="uq_score_record_duty_assignment"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    duty_assignment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("duty_assignments.id"),
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    base_points = Column(
        Float,
        nullable=False
    )

    action_points = Column(
        Float,
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    
class UserDevice(Base):
    """
    Represents a device installation belonging to a user.

    A user can have multiple devices.
    Each device has its own push notification token.
    """

    __tablename__ = "user_devices"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    device_token = Column(
        String(500),
        nullable=False,
        unique=True
    )

    platform = Column(
        String(20),
        nullable=False
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    
class Notification(Base):
    """
    Represents a pending notification for a user.

    Notifications are operational data.
    Historical notification data will be stored separately.
    """

    __tablename__ = "notifications"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    type = Column(
        String(50),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    body = Column(
        String(1000),
        nullable=False
    )

    scheduled_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

    sent_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    
class UserNotificationSettings(Base):
    """
    Stores notification preferences for a user.

    Each user has one notification settings record.
    """

    __tablename__ = "user_notification_settings"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            name="uq_user_notification_settings_user"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    notifications_enabled = Column(
        Boolean,
        nullable=False,
        default=True
    )

    sound_enabled = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )