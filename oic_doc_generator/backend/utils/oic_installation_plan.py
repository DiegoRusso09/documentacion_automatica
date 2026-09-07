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

from oic_doc_generator.backend.parsers.project_parser import (
    read_project_xml
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

from oic_doc_generator.backend.parsers.schedule_parser import (
    get_schedule_information
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
# INTEGRATION CONNECTION
# =========================================================

def is_integration_connection(
    connection
):

    raw_type = (
        connection.get(
            "raw_type",
            ""
        )
        or
        ""
    ).strip().lower()


    connection_type = (
        connection.get(
            "type",
            ""
        )
        or
        ""
    ).strip().lower()


    return (
        raw_type == "collocatedics"
        or
        connection_type == "local integration"
    )


# =========================================================
# CONFIGURABLE CONNECTIONS
# =========================================================

def get_configurable_connections(
    connections
):

    return [

        connection

        for connection in (
            connections
            or
            []
        )

        if not is_integration_connection(
            connection
        )
    ]


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
# FORMAT OIC VERSION
# =========================================================

def format_oic_version(
    version
):

    value = str(
        version
        or
        ""
    ).strip()


    if not value:

        return ""


    parts = (
        value.split(
            "."
        )
    )


    formatted = []


    for part in parts:

        part = (
            part.strip()
        )


        if part.isdigit():

            formatted.append(
                str(
                    int(
                        part
                    )
                )
            )

        else:

            formatted.append(
                part
            )


    return ".".join(
        formatted
    )


# =========================================================
# GET ADAPTERS FROM SMART TAGS
# =========================================================

def get_smart_tag_adapters(
    smart_tags
):

    smart_tags = (
        smart_tags
        or
        ""
    )


    smart_tags = (
        smart_tags.replace(
            "\\:",
            ":"
        )
    )


    adapters = []

    seen = set()


    for raw_tag in (
        smart_tags.split(
            ","
        )
    ):

        tag = (
            raw_tag.strip()
        )


        if not tag:

            continue


        if not tag.lower().startswith(
            "app:"
        ):

            continue


        adapter = (
            tag.split(
                ":",
                1
            )[1]
            .strip()
            .lower()
        )


        if not adapter:

            continue


        if adapter in seen:

            continue


        seen.add(
            adapter
        )


        adapters.append(
            adapter
        )


    return adapters


# =========================================================
# GET INTEGRATION DEPENDENCIES
# =========================================================

def get_integration_dependencies(
    extracted_iar
):

    dependencies = []

    seen = set()


    applications = (
        read_project_xml(
            extracted_iar
        )
    )


    for application in applications:

        if not application.get(
            "IsIntegration",
            False
        ):

            continue


        integration_code = (
            application.get(
                "IntegrationCode",
                ""
            )
            or
            ""
        ).strip()


        integration_version = (
            application.get(
                "IntegrationVersion",
                ""
            )
            or
            ""
        ).strip()


        integration_operation = (
            application.get(
                "IntegrationOperation",
                ""
            )
            or
            ""
        ).strip()


        integration_service = (
            application.get(
                "IntegrationService",
                ""
            )
            or
            ""
        ).strip()


        if not integration_code:

            continue


        key = (

            integration_code.upper(),

            integration_version.upper()

        )


        if key in seen:

            continue


        seen.add(
            key
        )


        dependencies.append({

            "code":
                integration_code,

            "version":
                integration_version,

            "operation":
                integration_operation,

            "service":
                integration_service

        })


    return dependencies


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


    scheduled = (
        integration_is_scheduled(
            metadata
        )
    )

    # =====================================================
    # SCHEDULE INFORMATION
    # =====================================================

    schedule_info = {

        "frequency":
            "No definida",

        "ical_expression":
            "",

        "schedule_name":
            ""
    }


    if scheduled:

        schedule_info = (
            get_schedule_information(
                extracted_iar
            )
            or
            schedule_info
        )


    ical_expression = (
        schedule_info.get(
            "ical_expression",
            ""
        )
        or
        ""
    ).strip()


    schedule_name = (
        schedule_info.get(
            "schedule_name",
            ""
        )
        or
        ""
    ).strip()


    # =====================================================
    # DOES IT REALLY HAVE A RECURRENT SCHEDULE?
    # =====================================================

    has_schedule = (

        scheduled

        and

        bool(
            ical_expression
        )

    )


    # =====================================================
    # SCHEDULE NAME FALLBACK
    # =====================================================

    if (
        scheduled
        and
        not schedule_name
    ):

        schedule_name = (
            "Schedule "
            +
            (
                metadata.get(
                    "project_code",
                    ""
                )
                or
                "Integration"
            )
        )


    # =====================================================
    # INSTALLATION RULE
    # =====================================================

    if scheduled:

        if has_schedule:

            execution_mode = (
                "Ejecución programada"
            )


            schedule_display = (
                ical_expression
            )

        else:

            execution_mode = (
                "Ejecución única posterior a la activación"
            )


            schedule_display = (
                "No aplica"
            )

    else:

        execution_mode = (
            "No aplica"
        )


        schedule_display = (
            "No aplica"
        )


    integration_type = (

        "Scheduled"

        if scheduled

        else

        "App Driven"

    )


    smart_tags = (
        metadata.get(
            "smart_tags",
            ""
        )
        or
        ""
    )


    adapters = (
        get_smart_tag_adapters(
            smart_tags
        )
    )


    dependencies = (
        get_integration_dependencies(
            extracted_iar
        )
    )


    version = (
        metadata.get(
            "project_version",
            ""
        )
        or
        ""
    )


    return {

        # =================================================
        # IDENTITY
        # =================================================

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
            version,

        "version_display":
            format_oic_version(
                version
            ),

        # =================================================
        # SCHEDULE
        # =================================================

        "is_scheduled":
            scheduled,

        "has_schedule":
            has_schedule,

        "schedule":
            {

                "name":
                    schedule_name,

                "frequency":
                    schedule_info.get(
                        "frequency",
                        "No definida"
                    ),

                "ical_expression":
                    ical_expression

            },

        "execution_mode":
            execution_mode,

        "schedule_display":
            schedule_display,


        # =================================================
        # SOURCE METADATA
        # =================================================

        "state":
            metadata.get(
                "project_persisted_state",
                ""
            ),

        "source_state":
            metadata.get(
                "project_persisted_state",
                ""
            ),

        "smart_tags":
            smart_tags,

        "mep_type":
            metadata.get(
                "mep_type",
                ""
            ),

        "package_name":
            metadata.get(
                "package_name",
                ""
            ),


        # =================================================
        # INSTALLATION REPRESENTATION
        # =================================================

        "type":
            integration_type,

        "style_display":
            (
                "Schedule"
                if scheduled
                else
                "Application"
            ),

        "trigger_icon":
            (
                "schedule"
                if scheduled
                else
                "rest"
            ),

        "adapter_tags":
            adapters,


        # El IM090 representa el estado esperado
        # al comenzar la instalación en destino.
        "installation_status":
            "Configured",


        # =================================================
        # DEPENDENCIES
        # =================================================

        "dependencies":
            dependencies
    }



# =========================================================
# BUILD ACTIVATION ORDER
# =========================================================

def build_activation_order(
    integrations
):

    integrations = (
        integrations
        or
        []
    )


    # =====================================================
    # UNIQUE INTEGRATIONS
    # =====================================================

    unique_integrations = []

    seen = set()


    for integration in integrations:

        code = (
            integration.get(
                "code",
                ""
            )
            or
            ""
        ).strip()


        version = (
            integration.get(
                "version",
                ""
            )
            or
            ""
        ).strip()


        if not code:

            continue


        key = (

            code.upper(),

            version.upper()

        )


        if key in seen:

            continue


        seen.add(
            key
        )


        unique_integrations.append(
            integration
        )


    # =====================================================
    # NODE INDEXES
    # =====================================================

    nodes = {}

    nodes_by_code = {}

    original_order = {}


    for index, integration in enumerate(
        unique_integrations
    ):

        code = (
            integration.get(
                "code",
                ""
            )
            or
            ""
        ).strip()


        version = (
            integration.get(
                "version",
                ""
            )
            or
            ""
        ).strip()


        key = (

            code.upper(),

            version.upper()

        )


        nodes[
            key
        ] = integration


        nodes_by_code.setdefault(
            code.upper(),
            []
        ).append(
            key
        )


        original_order[
            key
        ] = index


    # =====================================================
    # GRAPH
    #
    # Si A llama B:
    #
    # B -> A
    #
    # porque B debe activarse primero.
    # =====================================================

    indegree = {

        key:
            0

        for key in nodes

    }


    dependents = {

        key:
            []

        for key in nodes

    }


    for node_key, integration in (
        nodes.items()
    ):

        resolved_dependencies = []


        for dependency in (
            integration.get(
                "dependencies",
                []
            )
        ):

            dependency_code = (
                dependency.get(
                    "code",
                    ""
                )
                or
                ""
            ).strip()


            dependency_version = (
                dependency.get(
                    "version",
                    ""
                )
                or
                ""
            ).strip()


            if not dependency_code:

                continue


            # =============================================
            # EXACT CODE + VERSION
            # =============================================

            dependency_key = (

                dependency_code.upper(),

                dependency_version.upper()

            )


            resolved_key = None


            if dependency_key in nodes:

                resolved_key = (
                    dependency_key
                )


            # =============================================
            # FALLBACK BY CODE
            #
            # Solo cuando en el conjunto existe
            # una única versión de ese código.
            # =============================================

            else:

                candidates = (
                    nodes_by_code.get(
                        dependency_code.upper(),
                        []
                    )
                )


                if len(
                    candidates
                ) == 1:

                    resolved_key = (
                        candidates[
                            0
                        ]
                    )


            if not resolved_key:

                continue


            if resolved_key == node_key:

                continue


            if (
                resolved_key
                in
                resolved_dependencies
            ):

                continue


            resolved_dependencies.append(
                resolved_key
            )


            # La integración actual depende de resolved_key.

            indegree[
                node_key
            ] += 1


            dependents[
                resolved_key
            ].append(
                node_key
            )


        integration[
            "resolved_dependencies"
        ] = [

            {

                "code":
                    nodes[
                        dependency_key
                    ].get(
                        "code",
                        ""
                    ),

                "name":
                    nodes[
                        dependency_key
                    ].get(
                        "name",
                        ""
                    ),

                "version":
                    nodes[
                        dependency_key
                    ].get(
                        "version",
                        ""
                    )

            }

            for dependency_key
            in resolved_dependencies

        ]


    # =====================================================
    # FIRST NODES
    # =====================================================

    queue = [

        key

        for key in nodes

        if indegree[
            key
        ] == 0

    ]


    queue.sort(
        key=lambda key:
            original_order[
                key
            ]
    )


    ordered_keys = []


    # =====================================================
    # TOPOLOGICAL SORT
    # =====================================================

    while queue:

        current = (
            queue.pop(
                0
            )
        )


        ordered_keys.append(
            current
        )


        for dependent in (
            dependents[
                current
            ]
        ):

            indegree[
                dependent
            ] -= 1


            if (
                indegree[
                    dependent
                ]
                ==
                0
            ):

                queue.append(
                    dependent
                )


                queue.sort(
                    key=lambda key:
                        original_order[
                            key
                        ]
                )


    # =====================================================
    # CYCLE PROTECTION
    # =====================================================

    warnings = []


    if len(
        ordered_keys
    ) < len(
        nodes
    ):

        remaining = [

            key

            for key in nodes

            if key not in ordered_keys

        ]


        remaining.sort(
            key=lambda key:
                original_order[
                    key
                ]
        )


        warnings.append(
            (
                "Se detectó una dependencia circular "
                "entre integraciones OIC. "
                "Las integraciones involucradas se "
                "mantuvieron en el orden original."
            )
        )


        ordered_keys.extend(
            remaining
        )


    # =====================================================
    # RESULT
    # =====================================================

    ordered_integrations = []


    for activation_order, key in enumerate(
        ordered_keys,
        start=1
    ):

        integration = (
            nodes[
                key
            ]
        )


        integration[
            "activation_order"
        ] = activation_order


        ordered_integrations.append(
            integration
        )


    return (
        ordered_integrations,
        warnings
    )


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

        "configurable_connections":
            get_configurable_connections(
                analysis.get(
                    "connections",
                    []
                )
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

    configurable_connections = (
        get_configurable_connections(
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

        "configurable_connections":
            configurable_connections,

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
                    configurable_connections
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

        "activation_plan":
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


    # =====================================================
    # GLOBAL ACTIVATION PLAN
    # =====================================================

    all_integrations = []


    for item in result[
        "items"
    ]:

        artifact_type = (
            item.get(
                "artifact_type",
                ""
            )
        )


        # =================================================
        # PAR
        # =================================================

        if artifact_type == "par":

            for integration in (
                item.get(
                    "integrations",
                    []
                )
            ):

                integration[
                    "source_artifact_type"
                ] = "par"


                integration[
                    "source_file"
                ] = item.get(
                    "file_name",
                    ""
                )


                all_integrations.append(
                    integration
                )


        # =================================================
        # IAR
        # =================================================

        elif artifact_type == "iar":

            integration = (
                item.get(
                    "integration",
                    {}
                )
            )


            if integration:

                integration[
                    "source_artifact_type"
                ] = "iar"


                integration[
                    "source_file"
                ] = item.get(
                    "file_name",
                    ""
                )


                all_integrations.append(
                    integration
                )


    # =====================================================
    # SORT BY DEPENDENCIES
    # =====================================================

    (
        activation_plan,
        activation_warnings
    ) = build_activation_order(
        all_integrations
    )


    result[
        "activation_plan"
    ] = activation_plan


    result[
        "warnings"
    ].extend(
        activation_warnings
    )


    # =====================================================
    # LOG
    # =====================================================

    print(
        "[IM090][OIC] ACTIVATION ORDER"
    )


    for integration in activation_plan:

        print(
            (
                f"  "
                f"{integration.get('activation_order')}. "
                f"{integration.get('name')} "
                f"({integration.get('version_display')}) "
                f"depends_on="
                f"{integration.get('resolved_dependencies', [])}"
            )
        )


    return result