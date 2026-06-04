# =========================================================
# FILE: integration_model.py
# =========================================================

from dataclasses import (
    dataclass,
    field
)

from typing import List


# =========================================================
# CONNECTION MODEL
# =========================================================

@dataclass
class ConnectionModel:

    name: str = ""

    type: str = ""

    security_policy: str = ""

    agent_group: str = ""

    authentication_type: str = ""

    properties: dict = field(
        default_factory=dict
    )


# =========================================================
# LOOKUP MODEL
# =========================================================

@dataclass
class LookupModel:

    name: str = ""

    path: str = ""


# =========================================================
# JAVASCRIPT MODEL
# =========================================================

@dataclass
class JavaScriptModel:

    name: str = ""

    path: str = ""


# =========================================================
# SERVICE FIELD MODEL
# =========================================================

@dataclass
class ServiceFieldModel:

    name: str = ""

    type: str = ""


# =========================================================
# SERVICE MODEL
# =========================================================

@dataclass
class ServiceModel:

    endpoint_name: str = ""

    request_fields: List[
        ServiceFieldModel
    ] = field(
        default_factory=list
    )

    response_fields: List[
        ServiceFieldModel
    ] = field(
        default_factory=list
    )


# =========================================================
# FLOW ROW MODEL
# =========================================================

@dataclass
class FlowRowModel:

    sequence: int = 0

    action_name: str = ""

    description: str = ""


# =========================================================
# ENDPOINT FLOW MODEL
# =========================================================

@dataclass
class EndpointFlowModel:

    endpoint_name: str = ""

    description: str = ""

    rows: List[
        FlowRowModel
    ] = field(
        default_factory=list
    )


# =========================================================
# SCHEDULE MODEL
# =========================================================

@dataclass
class ScheduleModel:

    frequency: str = ""

    ical_expression: str = ""


# =========================================================
# INTEGRATION MODEL
# =========================================================

@dataclass
class IntegrationModel:

    name: str = ""

    version: str = ""

    integration_type: str = ""

    persisted_state: str = ""

    active: bool = False

    has_javascript: bool = False

    lookups: List[
        LookupModel
    ] = field(
        default_factory=list
    )

    javascript_files: List[
        JavaScriptModel
    ] = field(
        default_factory=list
    )

    connections: List[
        ConnectionModel
    ] = field(
        default_factory=list
    )

    endpoint_flows: List[
        EndpointFlowModel
    ] = field(
        default_factory=list
    )

    services: List[
        ServiceModel
    ] = field(
        default_factory=list
    )

    schedule: ScheduleModel = field(
        default_factory=ScheduleModel
    )

    path: str = ""