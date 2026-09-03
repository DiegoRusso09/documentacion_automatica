# =========================================================
# FILE:
# oic_doc_generator/backend/utils/oic_installation_plan.py
# =========================================================

import os
import shutil
import xml.etree.ElementTree as ET


from oic_doc_generator.backend.parsers.iar_parser import (
    extract_iar
)

from oic_doc_generator.backend.parsers.par_parser import (
    extract_package,
    find_all_iar_files
)

from oic_doc_generator.backend.parsers.integration_parser import (
    get_integration_metadata,
    integration_is_scheduled
)

from oic_doc_generator.backend.parsers.connections_parser import (
    get_installation_connections
)

from oic_doc_generator.backend.parsers.lookup_parser import (
    get_lookup_names
)

from oic_doc_generator.backend.parsers.javascript_parser import (
    get_javascript_names
)


# =========================================================
# FILE NAME
# =========================================================

def get_oic_file_name(
    uploaded_file
):

    return (
        os.path.basename(
            getattr(
                uploaded_file,
                "name",
                ""
            )
            or
            str(
                uploaded_file
            )
        )
    )


# =========================================================
# UNIQUE STRINGS
# =========================================================

def unique_strings(
    values
):

    result = []

    seen = set()


    for value in values:

        value = (
            str(
                value
                or
                ""
            ).strip()
        )


        if not value:

            continue


        key = value.upper()


        if key in seen:

            continue


        seen.add(
            key
        )

        result.append(
            value
        )


    return result


# =========================================================
# UNIQUE CONNECTIONS
# =========================================================

def unique_connections(
    connections
):

    result = []

    seen = set()


    for connection in connections:

        key = (
            connection.get(
                "instance_code",
                ""
            )
            or
            connection.get(
                "name",
                ""
            )
        ).upper()


        if not key:

            continue


        if key in seen:

            continue


        seen.add(
            key
        )

        result.append(
            connection
        )


    return result


# =========================================================
# GET API LIBRARY NAMES
# =========================================================
#
# Intentamos obtener el nombre lógico de la librería.
#
# Si no existe metadata XML, usamos los nombres detectados
# por javascript_parser como fallback.
#
# =========================================================

def get_api_library_names(
    extracted_iar
):

    result = []


    for root, dirs, files in os.walk(
        extracted_iar
    ):

        for file_name in files:

            if not file_name.lower().endswith(
                ".xml"
            ):

                continue


            xml_path = os.path.join(
                root,
                file_name
            )


            try:

                tree = ET.parse(
                    xml_path
                )

                xml_root = (
                    tree.getroot()
                )

            except:

                continue


            root_tag = (
                str(
                    xml_root.tag
                )
                .split("}")[-1]
                .lower()
            )


            if root_tag != "api-library":

                continue


            for child in list(
                xml_root
            ):

                child_tag = (
                    str(
                        child.tag
                    )
                    .split("}")[-1]
                    .lower()
                )


                if (
                    child_tag
                    ==
                    "name"
                ):

                    name = (
                        child.text.strip()
                        if child.text
                        else ""
                    )


                    if name:

                        result.append(
                            name
                        )

                    break


    if result:

        return unique_strings(
            result
        )


    return unique_strings(
        get_javascript_names(
            extracted_iar
        )
    )


# =========================================================
# BUILD INTEGRATION INFO
# =========================================================

def build_integration_info(
    extracted_iar
):

    metadata = (
        get_integration_metadata(
            extracted_iar
        )
    )


    integration_type = (

        "Scheduled"

        if integration_is_scheduled(
            metadata
        )

        else

        "App Driven"
    )


    return {

        "name":
            (
                metadata.get(
                    "project_name",
                    ""
                )
                or
                metadata.get(
                    "project_code",
                    ""
                )
            ),

        "code":
            metadata.get(
                "project_code",
                ""
            ),

        "version":
            metadata.get(
                "project_version",
                ""
            ),

        "state":
            metadata.get(
                "project_persisted_state",
                ""
            ),

        "type":
            integration_type
    }


# =========================================================
# ANALYZE IAR
# =========================================================

def analyze_iar_for_installation(
    iar_source
):

    extracted_iar = None


    try:

        extracted_iar = (
            extract_iar(
                iar_source
            )
        )


        return {

            "integration":
                build_integration_info(
                    extracted_iar
                ),

            "connections":
                get_installation_connections(
                    extracted_iar
                ),

            "lookups":
                unique_strings(
                    get_lookup_names(
                        extracted_iar
                    )
                ),

            "javascript_libraries":
                get_api_library_names(
                    extracted_iar
                )
        }


    finally:

        if (
            extracted_iar
            and
            os.path.isdir(
                extracted_iar
            )
        ):

            shutil.rmtree(
                extracted_iar,
                ignore_errors=True
            )


# =========================================================
# BUILD IAR ITEM
# =========================================================

def build_iar_installation_item(
    uploaded_file,
    order
):

    try:

        uploaded_file.seek(
            0
        )

    except:

        pass


    file_name = (
        get_oic_file_name(
            uploaded_file
        )
    )


    analysis = (
        analyze_iar_for_installation(
            uploaded_file
        )
    )


    try:

        uploaded_file.seek(
            0
        )

    except:

        pass


    return {

        "order":
            order,

        "artifact_type":
            "iar",

        "type_label":
            "IAR",

        "file_name":
            file_name,

        "package_path":
            "../OIC/"
            +
            file_name,

        "navigation":
            "Design > Integrations > Import",

        "import_image":
            "import_iar_oic.png",

        "integration":
            analysis.get(
                "integration",
                {}
            ),

        "connections":
            analysis.get(
                "connections",
                []
            ),

        "lookups":
            analysis.get(
                "lookups",
                []
            ),

        "javascript_libraries":
            analysis.get(
                "javascript_libraries",
                []
            )
    }


# =========================================================
# BUILD PAR ITEM
# =========================================================

def build_par_installation_item(
    uploaded_file,
    order
):

    extracted_package = None


    try:

        uploaded_file.seek(
            0
        )

    except:

        pass


    file_name = (
        get_oic_file_name(
            uploaded_file
        )
    )


    integrations = []

    connections = []

    lookups = []

    javascript_libraries = []


    try:

        extracted_package = (
            extract_package(
                uploaded_file
            )
        )


        iar_files = (
            find_all_iar_files(
                extracted_package
            )
        )


        for iar_path in iar_files:

            analysis = (
                analyze_iar_for_installation(
                    iar_path
                )
            )


            integration = (
                analysis.get(
                    "integration",
                    {}
                )
            )


            if integration:

                integrations.append(
                    integration
                )


            connections.extend(
                analysis.get(
                    "connections",
                    []
                )
            )


            lookups.extend(
                analysis.get(
                    "lookups",
                    []
                )
            )


            javascript_libraries.extend(
                analysis.get(
                    "javascript_libraries",
                    []
                )
            )


    finally:

        if (
            extracted_package
            and
            os.path.isdir(
                extracted_package
            )
        ):

            shutil.rmtree(
                extracted_package,
                ignore_errors=True
            )


        try:

            uploaded_file.seek(
                0
            )

        except:

            pass


    # =====================================================
    # DEDUPE INTEGRATIONS
    # =====================================================

    unique_integrations = []

    integration_keys = set()


    for integration in integrations:

        key = (

            integration.get(
                "code",
                ""
            ).upper(),

            integration.get(
                "version",
                ""
            ).upper()
        )


        if key in integration_keys:

            continue


        integration_keys.add(
            key
        )

        unique_integrations.append(
            integration
        )


    connections = (
        unique_connections(
            connections
        )
    )


    lookups = (
        unique_strings(
            lookups
        )
    )


    javascript_libraries = (
        unique_strings(
            javascript_libraries
        )
    )


    return {

        "order":
            order,

        "artifact_type":
            "par",

        "type_label":
            "PAR",

        "file_name":
            file_name,

        "package_path":
            "../OIC/"
            +
            file_name,

        "navigation":
            "Design > Packages > Import",

        "import_image":
            "import_par_oic.png",

        "integrations":
            unique_integrations,

        "connections":
            connections,

        "lookups":
            lookups,

        "javascript_libraries":
            javascript_libraries,

        "summary": {

            "integration_count":
                len(
                    unique_integrations
                ),

            "connection_count":
                len(
                    connections
                ),

            "lookup_count":
                len(
                    lookups
                ),

            "javascript_library_count":
                len(
                    javascript_libraries
                )
        }
    }


# =========================================================
# BUILD OIC INSTALLATION PLAN
# =========================================================

def build_oic_installation_plan(
    oic_files
):

    result = {

        "items":
            [],

        "warnings":
            []
    }


    if not oic_files:

        return result


    current_order = 1


    for uploaded_file in oic_files:

        file_name = (
            get_oic_file_name(
                uploaded_file
            )
        )


        lower_name = (
            file_name.lower()
        )


        try:

            if lower_name.endswith(
                ".iar"
            ):

                item = (
                    build_iar_installation_item(

                        uploaded_file,

                        current_order
                    )
                )


            elif lower_name.endswith(
                ".par"
            ):

                item = (
                    build_par_installation_item(

                        uploaded_file,

                        current_order
                    )
                )


            else:

                result[
                    "warnings"
                ].append(

                    (
                        "Archivo OIC no soportado "
                        f"para IM090: {file_name}"
                    )
                )

                continue


            result[
                "items"
            ].append(
                item
            )


            current_order += 1


        except Exception as error:

            result[
                "warnings"
            ].append(

                (
                    f"Error analizando {file_name}: "
                    f"{str(error)}"
                )
            )


    return result