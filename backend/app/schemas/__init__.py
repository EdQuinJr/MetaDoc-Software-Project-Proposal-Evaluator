"""
Request/Response validation schemas for MetaDoc API

Provides validation schemas for API endpoints to ensure data integrity
and provide clear error messages for invalid requests.
"""

from app.schemas.auth_schemas import (
    LoginSchema,
    RegisterSchema,
    TokenGenerationSchema
)
from app.schemas.submission_schemas import (
    SubmissionUploadSchema,
    DriveLinkSchema
)
from app.schemas.deadline_schemas import (
    DeadlineCreateSchema,
    DeadlineUpdateSchema
)
from app.schemas.report_schemas import (
    ReportExportSchema
)

from app.schemas.dto import (
    UserDTO,
    UserSessionDTO,
    UserProfileDTO,
    SubmissionDTO,
    SubmissionListDTO,
    SubmissionDetailDTO,
    SubmissionTokenDTO,
    AnalysisResultDTO,
    MetadataDTO,
    ContentStatisticsDTO,
    HeuristicInsightsDTO,
    NLPResultDTO,
    DeadlineDTO,
    DeadlineListDTO,
    ReportExportDTO
)

__all__ = [
    'LoginSchema',
    'RegisterSchema',
    'TokenGenerationSchema',
    'SubmissionUploadSchema',
    'DriveLinkSchema',
    'DeadlineCreateSchema',
    'DeadlineUpdateSchema',
    'ReportExportSchema',
    'UserDTO',
    'UserSessionDTO',
    'UserProfileDTO',
    'SubmissionDTO',
    'SubmissionListDTO',
    'SubmissionDetailDTO',
    'SubmissionTokenDTO',
    'AnalysisResultDTO',
    'MetadataDTO',
    'ContentStatisticsDTO',
    'HeuristicInsightsDTO',
    'NLPResultDTO',
    'DeadlineDTO',
    'DeadlineListDTO',
    'ReportExportDTO'
]
