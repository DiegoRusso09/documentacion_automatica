# =========================================================
# FILE: connection_model.py
# =========================================================

from dataclasses import (
    dataclass,
    field
)

from typing import Dict


# =========================================================
# CONNECTION PROPERTY MODEL
# =========================================================

@dataclass
class ConnectionPropertyModel:

    name: str = ""

    value: str = ""


# =========================================================
# CONNECTION MODEL
# =========================================================

@dataclass
class ConnectionModel:

    # =====================================================
    # BASIC INFO
    # =====================================================

    name: str = ""

    type: str = ""

    description: str = ""

    revision: str = ""

    status: str = ""

    hidden: bool = False

    percentage_complete: str = ""

    # =====================================================
    # SECURITY
    # =====================================================

    security_policy: str = ""

    authentication_type: str = ""

    csf_map: str = ""

    csf_key: str = ""

    # =====================================================
    # DATABASE
    # =====================================================

    host: str = ""

    port: str = ""

    sid: str = ""

    service_name: str = ""

    # =====================================================
    # SOAP / REST
    # =====================================================

    wsdl_url: str = ""

    tls_version: str = ""

    # =====================================================
    # FTP / SFTP
    # =====================================================

    use_sftp: bool = False

    use_implicit_ssl: bool = False

    disable_directory_check: bool = False

    use_default_user_home: bool = False

    # =====================================================
    # AGENT
    # =====================================================

    agent_group: str = ""

    # =====================================================
    # RAW PROPERTIES
    # =====================================================

    properties: Dict[
        str,
        str
    ] = field(
        default_factory=dict
    )

    # =====================================================
    # METHODS
    # =====================================================

    def get_summary(self):

        parts = []

        if self.type:

            parts.append(
                f"Tipo: {self.type}"
            )

        if self.authentication_type:

            parts.append(

                f"Autenticación: "
                f"{self.authentication_type}"

            )

        if self.security_policy:

            parts.append(

                f"Security Policy: "
                f"{self.security_policy}"

            )

        if self.host:

            parts.append(
                f"Host: {self.host}"
            )

        if self.port:

            parts.append(
                f"Port: {self.port}"
            )

        if self.service_name:

            parts.append(

                f"Service Name: "
                f"{self.service_name}"

            )

        if self.sid:

            parts.append(
                f"SID: {self.sid}"
            )

        if self.wsdl_url:

            parts.append(
                f"WSDL: {self.wsdl_url}"
            )

        if self.tls_version:

            parts.append(
                f"TLS: {self.tls_version}"
            )

        if self.agent_group:

            parts.append(

                f"Agent Group: "
                f"{self.agent_group}"

            )

        return ", ".join(parts)

    # =====================================================
    # IS DATABASE
    # =====================================================

    def is_database(self):

        return (
            self.type.lower()
            == "dbaas"
        )

    # =====================================================
    # IS SOAP
    # =====================================================

    def is_soap(self):

        return (
            self.type.lower()
            == "soap"
        )

    # =====================================================
    # IS REST
    # =====================================================

    def is_rest(self):

        return (
            self.type.lower()
            == "rest"
        )

    # =====================================================
    # IS SFTP
    # =====================================================

    def is_sftp(self):

        return (
            self.type.lower()
            == "sftp"
        )

    # =====================================================
    # USES WALLET
    # =====================================================

    def uses_wallet(self):

        return (
            self.security_policy.upper()
            == "ORACLE_WALLET"
        )

    # =====================================================
    # USES BASIC AUTH
    # =====================================================

    def uses_basic_auth(self):

        return (
            self.security_policy.upper()
            == "BASIC_AUTH"
        )