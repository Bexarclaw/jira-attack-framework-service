"""Data models for JIRA entities.

This module defines Pydantic models for JIRA projects, issues,
custom fields, and other entities.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class IssueType(str, Enum):
    """JIRA issue types."""

    TASK = "Task"
    SUBTASK = "Sub-task"
    STORY = "Story"
    BUG = "Bug"
    EPIC = "Epic"


class MaturityLevel(str, Enum):
    """Detection maturity levels for ATT&CK techniques."""

    NOT_TRACKED = "Not Tracked"
    INITIAL = "Initial"
    DEFINED = "Defined"
    RESILIENT = "Resilient"
    OPTIMIZED = "Optimized"


class CustomFieldType(str, Enum):
    """JIRA custom field types."""

    TEXT = "com.atlassian.jira.plugin.system.customfieldtypes:textfield"
    SELECT = "com.atlassian.jira.plugin.system.customfieldtypes:select"
    MULTISELECT = "com.atlassian.jira.plugin.system.customfieldtypes:multiselect"
    URL = "com.atlassian.jira.plugin.system.customfieldtypes:url"
    NUMBER = "com.atlassian.jira.plugin.system.customfieldtypes:float"
    DATE = "com.atlassian.jira.plugin.system.customfieldtypes:datepicker"


class CustomField(BaseModel):
    """JIRA custom field definition.

    Attributes:
        id: Field ID (e.g., customfield_10001)
        name: Display name
        description: Field description
        field_type: Custom field type
        searcherKey: Searcher key for the field
    """

    id: str | None = None
    name: str
    description: str
    field_type: CustomFieldType = Field(alias="type")
    searcherKey: str

    class Config:
        populate_by_name = True


class CustomFieldOption(BaseModel):
    """Option for select/multiselect custom fields.

    Attributes:
        value: Option value
        id: Option ID (assigned by JIRA)
    """

    value: str
    id: str | None = None


class JiraProject(BaseModel):
    """JIRA project definition.

    Attributes:
        id: Project ID
        key: Project key (e.g., ATTACK)
        name: Project name
        description: Project description
        lead: Project lead username
        projectTypeKey: Type of project
        templateKey: Project template
    """

    id: str | None = None
    key: str
    name: str
    description: str | None = None
    lead: str | None = None
    projectTypeKey: str = "software"
    templateKey: str = "com.pyxis.greenhopper.jira:gh-simplified-basic"


class JiraIssueFields(BaseModel):
    """JIRA issue fields.

    Attributes:
        project: Project key
        summary: Issue summary
        description: Issue description
        issuetype: Issue type
        parent: Parent issue (for sub-tasks)
        labels: Issue labels
        custom_fields: Custom field values
    """

    project: dict[str, str]
    summary: str
    description: str
    issuetype: dict[str, str]
    parent: dict[str, str] | None = None
    labels: list[str] = Field(default_factory=list)

    class Config:
        extra = "allow"  # Allow custom fields


class JiraIssue(BaseModel):
    """JIRA issue definition.

    Attributes:
        id: Issue ID
        key: Issue key (e.g., ATTACK-123)
        fields: Issue fields
        self_url: URL to the issue
    """

    id: str | None = None
    key: str | None = None
    fields: JiraIssueFields
    self_url: str | None = Field(None, alias="self")

    class Config:
        populate_by_name = True


class ScreenConfig(BaseModel):
    """JIRA screen configuration.

    Attributes:
        id: Screen ID
        name: Screen name
        description: Screen description
        tab_id: Tab ID within the screen
    """

    id: str | None = None
    name: str
    description: str | None = None
    tab_id: str | None = None


class FieldLayoutConfig(BaseModel):
    """Field layout configuration for issue view.

    Attributes:
        primary: Fields shown in primary section
        secondary: Fields shown in secondary section
        visible: Fields visible in content area
        always_hidden: Fields always hidden
    """

    primary: list[dict[str, str]] = Field(default_factory=list)
    secondary: list[dict[str, str]] = Field(default_factory=list)
    visible: list[dict[str, str]] = Field(default_factory=list)
    always_hidden: list[dict[str, str]] = Field(default_factory=list)

    def to_jira_format(self) -> dict[str, Any]:
        """Convert to JIRA API format.

        Returns:
            Dictionary in JIRA API format
        """
        return {
            "context": {
                "primary": self.primary,
                "secondary": self.secondary,
                "alwaysHidden": self.always_hidden,
            },
            "content": {
                "visible": self.visible,
                "alwaysHidden": [],
            },
        }
