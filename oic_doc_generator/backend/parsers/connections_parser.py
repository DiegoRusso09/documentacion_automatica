# =========================================================
# FILE: oic_doc_generator/parsers/connections_parser.py
# =========================================================

import os
import re

import xml.etree.ElementTree as ET

from oic_doc_generator.backend.utils.xml_utils import (
    clean_tag,
    camel_to_snake_upper
)


# =========================================================
# MAP CONNECTION TYPE
# =========================================================

def map_connection_type(
    value
):

    if not value:

        return "UNKNOWN"

    lower = value.lower()

    if "dbaas" in lower:

        return "DBaaS"

    if "database" in lower:

        return "DBaaS"

    if "rest" in lower:

        return "REST"

    if "soap" in lower:

        return "SOAP"

    if "ftp" in lower:

        return "FTP"

    if "sftp" in lower:

        return "SFTP"

    if "erp" in lower:

        return "ERP"

    if "ociobjectstorage" in lower:

        return "OCI_OBJECT_STORAGE"

    if "stage" in lower:

        return "STAGE"

    if "file" in lower:

        return "FILE"

    return value


# =========================================================
# FIND APPLICATION FOLDER
# =========================================================

def find_application_folder(
    base_path,
    application_name
):

    for root, dirs, files in os.walk(
        base_path
    ):

        for d in dirs:

            if (
                d.lower()
                ==
                application_name.lower()
            ):

                return os.path.join(
                    root,
                    d
                )

    return None


# =========================================================
# FIND JCA FILE
# =========================================================

def find_jca_file(
    application_folder
):

    if not application_folder:

        return None

    for root, dirs, files in os.walk(
        application_folder
    ):

        for file in files:

            if file.endswith(
                ".jca"
            ):

                return os.path.join(
                    root,
                    file
                )

    return None


# =========================================================
# ANALYZE DBAAS JCA
# =========================================================

def analyze_dbaas_jca(
    application_folder
):

    result = {

        "Operacion": "",

        "Tabla": "",

        "Package": "",

        "Procedure": "",

        "SQL": ""
    }

    jca_file = find_jca_file(
        application_folder
    )

    if not jca_file:

        return result

    with open(

        jca_file,

        "r",

        encoding="utf-8",

        errors="ignore"

    ) as f:

        content = f.read()

    # =====================================================
    # STORED PROCEDURE
    # =====================================================

    if (
        "DBStoredProcedureInteractionSpec"
        in content
    ):

        result["Operacion"] = (
            "Stored Procedure"
        )

        package_match = re.search(

            r'PackageName\" value=\"([^\"]+)\"',

            content
        )

        procedure_match = re.search(

            r'ProcedureName\" value=\"([^\"]+)\"',

            content
        )

        if package_match:

            result["Package"] = (
                package_match.group(1)
            )

        if procedure_match:

            result["Procedure"] = (
                procedure_match.group(1)
            )

    # =====================================================
    # PURE SQL
    # =====================================================

    if (
        "DBPureSQLInteractionSpec"
        in content
    ):

        result["Operacion"] = (
            "SQL Puro"
        )

        sql_match = re.search(

            r'SqlString\" value=\"([^\"]+)\"',

            content
        )

        if sql_match:

            result["SQL"] = (
                sql_match.group(1)
            )

            table_match = re.search(

                r'from\s+([a-zA-Z0-9_\.]+)',

                result["SQL"],

                re.IGNORECASE
            )

            if table_match:

                result["Tabla"] = (
                    table_match.group(1)
                )

    # =====================================================
    # SELECT
    # =====================================================

    if (
        "DBReadInteractionSpec"
        in content
    ):

        if "QueryName" in content:

            result["Operacion"] = (
                "Select"
            )

        descriptor_match = re.search(

            r'DescriptorName\" value=\"([^\"]+)\"',

            content
        )

        if descriptor_match:

            descriptor = (
                descriptor_match.group(1)
            )

            if "." in descriptor:

                descriptor = descriptor.split(
                    "."
                )[-1]

            result["Tabla"] = (
                camel_to_snake_upper(
                    descriptor
                )
            )

    # =====================================================
    # INSERT UPDATE DELETE
    # =====================================================

    if (
        "DBWriteInteractionSpec"
        in content
    ):

        dml_match = re.search(

            r'DmlType\" value=\"([^\"]+)\"',

            content
        )

        if dml_match:

            result["Operacion"] = (

                dml_match.group(1)
                .capitalize()
            )

        descriptor_match = re.search(

            r'DescriptorName\" value=\"([^\"]+)\"',

            content
        )

        if descriptor_match:

            descriptor = (
                descriptor_match.group(1)
            )

            if "." in descriptor:

                descriptor = descriptor.split(
                    "."
                )[-1]

            result["Tabla"] = (
                camel_to_snake_upper(
                    descriptor
                )
            )

    return result


# =========================================================
# GET CONNECTIONS INFORMATION
# =========================================================

def get_connections_information(
    extracted_iar
):

    result = []

    for root, dirs, files in os.walk(
        extracted_iar
    ):

        if "appinstances" not in root.lower():

            continue

        for file in files:

            if not file.lower().endswith(
                ".xml"
            ):

                continue

            xml_path = os.path.join(
                root,
                file
            )

            try:

                tree = ET.parse(
                    xml_path
                )

                xml_root = tree.getroot()

            except:

                continue

            conn_data = {

                "name": "",

                "type": "",

                "security_policy": "",

                "agent_group": "",

                "properties": {}
            }

            current_property = None

            # =================================================
            # ITER XML
            # =================================================

            for elem in xml_root.iter():

                try:

                    tag = clean_tag(
                        elem.tag
                    )

                except:

                    continue

                text = (
                    elem.text.strip()
                    if elem.text
                    else ""
                )

                # =============================================
                # DISPLAY NAME (PRIORITY)
                # =============================================

                if tag == "displayName":

                    conn_data[
                        "name"
                    ] = text

                # =============================================
                # FALLBACK NAME
                # =============================================

                elif (

                    tag == "name"

                    and

                    not conn_data["name"]
                ):

                    conn_data[
                        "name"
                    ] = text

                # =============================================
                # TYPE
                # =============================================

                elif (
                    tag
                    ==
                    "applicationTypeRef"
                ):

                    conn_data[
                        "type"
                    ] = map_connection_type(
                        text
                    )

                # =============================================
                # SECURITY POLICY
                # =============================================

                elif (
                    tag
                    ==
                    "securityPolicy"
                ):

                    conn_data[
                        "security_policy"
                    ] = text

                # =============================================
                # AGENT GROUP
                # =============================================

                elif (
                    tag
                    ==
                    "agentDefinition"
                ):

                    conn_data[
                        "agent_group"
                    ] = text

                # =============================================
                # PROPERTY NAME
                # =============================================

                elif (
                    tag
                    ==
                    "connectionProperty"
                ):

                    current_property = {}

                elif (
                    tag
                    ==
                    "name"
                ):

                    if current_property is not None:

                        current_property[
                            "name"
                        ] = text

                elif (
                    tag
                    ==
                    "value"
                ):

                    if current_property is not None:

                        current_property[
                            "value"
                        ] = text

                        property_name = (
                            current_property.get(
                                "name",
                                ""
                            )
                        )

                        property_value = (
                            current_property.get(
                                "value",
                                ""
                            )
                        )

                        if property_name:

                            conn_data[
                                "properties"
                            ][
                                property_name
                            ] = property_value

                        current_property = None

            # =================================================
            # FALLBACK NAME FROM FILE
            # =================================================

            if not conn_data["name"]:

                conn_data["name"] = (
                    os.path.splitext(
                        file
                    )[0]
                )

            result.append(
                conn_data
            )

    return result


# =========================================================
# GET CONNECTION XMLS
# =========================================================

def get_connection_xmls(
    extracted_iar
):

    return get_connections_information(
        extracted_iar
    )


# =========================================================
# IM090 - CONNECTION INSTALLATION METADATA
# =========================================================

IM090_INTERNAL_PROPERTIES = {
    "csfkey",
    "csfmap",
    "integration_role"
}


IM090_PROPERTY_LABELS = {

    "Host":
        "Host",

    "Port":
        "Puerto",

    "SID":
        "SID",

    "ServiceName":
        "Service Name",

    "connectionUrl":
        "Connection URL",

    "connectionType":
        "Connection Type",

    "UseSftp":
        "SFTP Connection",

    "ServerTimeZone":
        "Server Time Zone",

    "UsePassiveIpAsHostIp":
        "Usar IP pasiva como Host",

    "UseImplicitSSL":
        "SSL Implícito",

    "enableTwoWaySSL":
        "Two-Way SSL",

    "sslCertificateAlias":
        "SSL Certificate Alias",

    "HostKeyCertificate":
        "Host Key Certificate",

    "WALLET":
        "Wallet",

    "WALLETPASSWORD":
        "Wallet Password",

    "WalletPassword":
        "Wallet Password",

    "PGPPUBLICKEY":
        "PGP Public Key",

    "PGPPRIVATEKEY":
        "PGP Private Key",

    "PGPPRIVATEKEYPASSWORD":
        "PGP Private Key Password",

    "PGPCIPHER":
        "PGP Cipher",

    "PGPHASHINGALGO":
        "PGP Hashing Algorithm"
}


# =========================================================
# XML TEXT
# =========================================================

def get_xml_tag_value(
    xml_root,
    tag_name
):

    for elem in xml_root.iter():

        try:

            tag = clean_tag(
                elem.tag
            )

        except:

            continue


        if tag != tag_name:

            continue


        value = (
            elem.text.strip()
            if elem.text
            else ""
        )


        if value:

            return value


    return ""


# =========================================================
# CONNECTION PROPERTIES
# =========================================================

def extract_connection_properties(
    xml_root
):

    result = {}


    for elem in xml_root.iter():

        try:

            tag = clean_tag(
                elem.tag
            )

        except:

            continue


        if tag != "connectionProperty":

            continue


        property_name = ""
        property_value = ""


        for child in list(
            elem
        ):

            try:

                child_tag = clean_tag(
                    child.tag
                )

            except:

                continue


            child_text = (
                child.text.strip()
                if child.text
                else ""
            )


            if child_tag == "name":

                property_name = (
                    child_text
                )


            elif child_tag == "value":

                property_value = (
                    child_text
                )


        if property_name:

            result[
                property_name
            ] = property_value


    return result


# =========================================================
# CONNECTION TYPE FOR INSTALLATION
# =========================================================

def map_installation_connection_type(
    raw_type,
    properties
):

    raw_type = (
        raw_type
        or
        ""
    )


    lower = raw_type.lower()


    if (
        "dbaas" in lower
        or
        "database" in lower
    ):

        return "Database"


    if "collocatedics" in lower:

        return "Local Integration"


    if "rest" in lower:

        return "REST"


    if "soap" in lower:

        return "SOAP"


    if "ftp" in lower:

        use_sftp = (
            properties.get(
                "UseSftp",
                ""
            )
        )


        if use_sftp:

            return "FTP/SFTP"


        return "FTP"


    if "sftp" in lower:

        return "FTP/SFTP"


    if "erp" in lower:

        return "Oracle ERP Cloud"


    if "hcm" in lower:

        return "Oracle HCM Cloud"


    if (
        "ociobjectstorage" in lower
        or
        "objectstorage" in lower
    ):

        return "OCI Object Storage"


    if "salesforce" in lower:

        return "Salesforce"


    if "stage" in lower:

        return "Stage File"


    if "file" in lower:

        return "File"


    if raw_type:

        return raw_type


    return "Desconocido"


# =========================================================
# PROPERTY GROUP
# =========================================================

def get_installation_property_group(
    property_name
):

    endpoint_properties = {

        "Host",
        "Port",
        "SID",
        "ServiceName",
        "connectionUrl",
        "connectionType"
    }


    security_properties = {

        "WALLET",
        "WALLETPASSWORD",
        "WalletPassword",
        "PGPPUBLICKEY",
        "PGPPRIVATEKEY",
        "PGPPRIVATEKEYPASSWORD",
        "PGPCIPHER",
        "PGPHASHINGALGO",
        "sslCertificateAlias",
        "HostKeyCertificate"
    }


    if property_name in endpoint_properties:

        return "Conexión"


    if property_name in security_properties:

        return "Seguridad"


    return "Propiedades"


# =========================================================
# PROPERTY LABEL
# =========================================================

def get_installation_property_label(
    property_name
):

    return (
        IM090_PROPERTY_LABELS.get(
            property_name,
            property_name
        )
    )


# =========================================================
# SENSITIVE PROPERTY
# =========================================================

def is_sensitive_connection_property(
    property_name
):

    lower = (
        property_name
        or
        ""
    ).lower()


    sensitive_names = [

        "password",
        "privatekey",
        "secret"
    ]


    for value in sensitive_names:

        if value in lower:

            return True


    return False


# =========================================================
# DISPLAY PROPERTY VALUE
# =========================================================

def get_installation_property_value(
    property_name,
    property_value
):

    property_value = (
        property_value
        or
        ""
    ).strip()


    if not property_value:

        return ""


    if is_sensitive_connection_property(
        property_name
    ):

        return (
            "<Configurar en ambiente destino>"
        )


    if (
        property_value.startswith(
            "%%"
        )
        and
        property_value.endswith(
            "%%"
        )
    ):

        return (
            "<Configurar en ambiente destino>"
        )


    return property_value


# =========================================================
# BUILD INSTALLATION ROWS
# =========================================================

def build_connection_installation_rows(
    connection
):

    rows = []


    # =====================================================
    # GENERAL
    # =====================================================

    rows.append({

        "group":
            "General",

        "property":
            "Tipo de conexión",

        "value":
            connection.get(
                "type",
                ""
            )
    })


    integration_role = (
        connection.get(
            "integration_role",
            ""
        )
    )


    if integration_role:

        rows.append({

            "group":
                "General",

            "property":
                "Rol de integración",

            "value":
                integration_role
        })


    agent_group = (
        connection.get(
            "agent_group",
            ""
        )
    )


    if agent_group:

        rows.append({

            "group":
                "General",

            "property":
                "Agent Group",

            "value":
                agent_group
        })


    # =====================================================
    # PROPERTIES
    # =====================================================

    for property_name, raw_value in (
        connection.get(
            "properties",
            {}
        ).items()
    ):

        if (
            property_name.lower()
            in
            IM090_INTERNAL_PROPERTIES
        ):

            continue


        display_value = (
            get_installation_property_value(

                property_name,

                raw_value
            )
        )


        # No mostramos propiedades vacías.
        if not display_value:

            continue


        rows.append({

            "group":
                get_installation_property_group(
                    property_name
                ),

            "property":
                get_installation_property_label(
                    property_name
                ),

            "value":
                display_value
        })


    # =====================================================
    # SECURITY POLICY
    # =====================================================

    security_policy = (
        connection.get(
            "security_policy",
            ""
        )
    )


    if security_policy:

        rows.append({

            "group":
                "Seguridad",

            "property":
                "Security Policy",

            "value":
                security_policy
        })


    # =====================================================
    # REQUIRED CREDENTIALS
    # =====================================================

    connection_type = (
        connection.get(
            "type",
            ""
        )
    )


    requires_user_password = (

        security_policy
        in {
            "BASIC_AUTH",
            "USERNAME_PASSWORD_TOKEN"
        }

        or

        (
            connection_type
            ==
            "FTP/SFTP"

            and

            security_policy
            ==
            "CUSTOM"
        )
    )


    if requires_user_password:

        rows.append({

            "group":
                "Seguridad",

            "property":
                "Usuario",

            "value":
                "<Configurar en ambiente destino>"
        })


        rows.append({

            "group":
                "Seguridad",

            "property":
                "Contraseña",

            "value":
                "<Configurar en ambiente destino>"
        })


    return rows


# =========================================================
# PARSE CONNECTION XML FOR INSTALLATION
# =========================================================

def parse_connection_for_installation(
    xml_path
):

    try:

        tree = ET.parse(
            xml_path
        )

        xml_root = (
            tree.getroot()
        )

    except:

        return None


    properties = (
        extract_connection_properties(
            xml_root
        )
    )


    raw_type = (
        get_xml_tag_value(
            xml_root,
            "applicationTypeRef"
        )
    )


    integration_role = (
        get_xml_tag_value(
            xml_root,
            "integrationRole"
        )
        or
        properties.get(
            "integration_role",
            ""
        )
    )


    connection = {

        "name":
            get_xml_tag_value(
                xml_root,
                "displayName"
            )
            or
            os.path.splitext(
                os.path.basename(
                    xml_path
                )
            )[0],

        "instance_code":
            get_xml_tag_value(
                xml_root,
                "instanceCode"
            ),

        "raw_type":
            raw_type,

        "type":
            map_installation_connection_type(
                raw_type,
                properties
            ),

        "integration_role":
            integration_role,

        "security_policy":
            get_xml_tag_value(
                xml_root,
                "securityPolicy"
            ),

        "agent_group":
            get_xml_tag_value(
                xml_root,
                "agentDefinition"
            ),

        "properties":
            properties
    }


    connection[
        "installation_rows"
    ] = (
        build_connection_installation_rows(
            connection
        )
    )


    return connection


# =========================================================
# GET CONNECTIONS FOR IM090
# =========================================================

def get_installation_connections(
    extracted_iar
):

    result = []


    for root, dirs, files in os.walk(
        extracted_iar
    ):

        if "appinstances" not in root.lower():

            continue


        for file_name in files:

            if not file_name.lower().endswith(
                ".xml"
            ):

                continue


            connection = (
                parse_connection_for_installation(
                    os.path.join(
                        root,
                        file_name
                    )
                )
            )


            if connection:

                result.append(
                    connection
                )


    return result


# =========================================================
# BUILD ACTION DESCRIPTION
# =========================================================

def build_action_description(
    app,
    dbaas=None
):

    if not app:

        return "Acción desconocida."

    # =====================================================
    # INTEGRATION CALL
    # =====================================================

    if app.get(
        "IsIntegration",
        False
    ):

        integration_service = app.get(
            "IntegrationService",
            ""
        )

        integration_code = app.get(
            "IntegrationCode",
            ""
        )

        integration_version = app.get(
            "IntegrationVersion",
            ""
        )

        integration_operation = app.get(
            "IntegrationOperation",
            ""
        )

        invoke_name = app.get(
            "Invoke",
            ""
        )

        return (

            f'Se llama al endpoint '
            f'"{integration_service}" '
            f'de la integración '
            f'"{integration_code}" '
            f'versión '
            f'"{integration_version}" '
            f'con operación '
            f'"{integration_operation}" '
            f'y el conector '
            f'en el flujo es llamado '
            f'{invoke_name}.'
        )

    # =====================================================
    # NORMAL CONNECTION
    # =====================================================

    connection_type = app.get(
        "Tipo",
        "UNKNOWN"
    )

    invoke_name = app.get(
        "Invoke",
        "UNKNOWN"
    )

    desc = (

        f"Se llama a una conexión "
        f"{connection_type} "
        f"llamada "
        f"{invoke_name}"
    )

    # =====================================================
    # DBAAS DETAILS
    # =====================================================

    if dbaas:

        if dbaas.get(
            "Operacion"
        ):

            desc += (
                f", realiza operación "
                f"{dbaas['Operacion']}"
            )

        if dbaas.get(
            "Tabla"
        ):

            desc += (
                f" a la tabla "
                f"{dbaas['Tabla']}"
            )

        if dbaas.get(
            "SQL"
        ):

            desc += (
                f" con el query "
                f"'{dbaas['SQL']}'"
            )

        if (

            dbaas.get("Package")

            and

            dbaas.get("Procedure")
        ):

            desc += (
                f" en el paquete "
                f"{dbaas['Package']}."
                f"{dbaas['Procedure']}"
            )

    desc += "."

    return desc