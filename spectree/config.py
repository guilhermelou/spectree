from enum import Enum
from typing import Dict, List, Optional

from pydantic import AnyUrl, BaseModel, BaseSettings, EmailStr, root_validator

from .models import SecurityScheme, Server
from .page import DEFAULT_PAGE_TEMPLATES


class ModeEnum(str, Enum):
    """the mode of the SpecTree validator"""

    #: includes undecorated routes and routes decorated by this instance
    normal = "normal"
    #: only includes routes decorated by this instance
    strict = "strict"
    #: includes all the routes
    greedy = "greedy"


class Contact(BaseModel):
    """contact information"""

    #: name of the contact
    name: str
    #: contact url
    url: AnyUrl = None
    #: contact email address
    email: EmailStr = None


class License(BaseModel):
    """license information"""

    #: name of the license
    name: str
    #: license url
    url: AnyUrl = None


class Configuration(BaseSettings):
    # OpenAPI configurations
    #: title of the service
    title: str = "Service API Document"
    #: service OpenAPI document description
    description: str = None
    #: service version
    version: str = "0.1.0"
    #: terms of service url
    terms_of_service: AnyUrl = None
    #: author contact information
    contact: Contact = None
    #: license information
    license: License = None

    # SpecTree configurations
    #: OpenAPI doc route path prefix (i.e. /apidoc/)
    path: str = "apidoc"
    #: OpenAPI file route path suffix (i.e. /apidoc/openapi.json)
    filename: str = "openapi.json"
    #: OpenAPI version (doesn't affect anything)
    openapi_version: str = "3.0.3"
    #: the mode of the SpecTree validator :class:`ModeEnum`
    mode: ModeEnum = ModeEnum.normal
    #: A dictionary of documentation page templates. The key is the
    #: name of the template, that is also used in the URL path, while the value is used
    #: to render the documentation page content. (Each page template should contain a
    #: `{spec_url}` placeholder, that'll be replaced by the actual OpenAPI spec URL in
    #: the rendered documentation page
    page_templates = DEFAULT_PAGE_TEMPLATES
    #: opt-in type annotation feature, see the README examples
    annotations = False
    #: servers section of OAS :py:class:`spectree.models.Server`
    servers: Optional[List[Server]] = []
    #: OpenAPI `securitySchemes` :py:class:`spectree.models.SecurityScheme`
    security_schemes: Optional[List[SecurityScheme]] = None
    #: OpenAPI `security` JSON at the global level
    security: Dict = {}

    class Config:
        env_prefix = "spectree_"
        validate_assignment = True

    @root_validator(pre=True)
    def convert_to_lower_case(cls, values):
        return {k.lower(): v for k, v in values.items()}

    @property
    def spec_url(self) -> str:
        return f"/{self.path}/{self.filename}"

    def openapi_info(self) -> Dict:
        info = self.dict(
            include={
                "title",
                "description",
                "version",
                "terms_of_service",
                "contact",
                "license",
            },
            exclude_none=True,
        )
        if info.get("terms_of_service") is not None:
            info["termsOfService"] = info.pop("terms_of_service")
        return info
