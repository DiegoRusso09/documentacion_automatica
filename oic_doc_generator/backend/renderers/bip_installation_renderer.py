# =========================================================
# FILE:
# oic_doc_generator/backend/renderers/bip_installation_renderer.py
# =========================================================

from html import escape


from oic_doc_generator.backend.renderers.screenshot_renderer import (
    render_html_to_image
)


# =========================================================
# BASE HTML
# =========================================================

def build_base_html(
    content,
    width=760
):

    return f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <style>

        html,
        body {{
            margin: 0;
            padding: 0;
            background: white;
            font-family: Arial, Helvetica, sans-serif;
            color: #222;
        }}


        body {{
            width: {width}px;
        }}


        * {{
            box-sizing: border-box;
        }}

    </style>

</head>

<body>

    {content}

</body>

</html>
"""


# =========================================================
# RENDER
# =========================================================

def render_bip_html(
    html_content
):

    return (
        render_html_to_image(

            html_content=
                html_content,

            resources_path=
                None
        )
    )


# =========================================================
# ROUTE IMAGE
# =========================================================

def render_bip_path_image(
    catalog_path
):

    safe_path = escape(
        catalog_path
        or
        ""
    )


    content = f"""

    <div
        style="
            width: 740px;
            padding: 20px 18px 8px 18px;
            background: #ffffff;
        "
    >

        <div
            style="
                display: inline-block;
                min-width: 680px;
                padding: 7px 8px;
                border: 1px solid #b8b8b8;
                background: #ffffff;
                font-size: 16px;
                line-height: 22px;
                color: #404040;
                box-shadow:
                    inset 0 1px 2px rgba(0, 0, 0, 0.06);
            "
        >
            {safe_path}
        </div>

    </div>
    """


    return (
        render_bip_html(
            build_base_html(
                content
            )
        )
    )


# =========================================================
# TASK ITEM
# =========================================================

def build_task_item(
    symbol,
    text,
    disabled=False,
    highlighted=False
):

    text_color = (
        "#b8b8b8"
        if disabled
        else
        "#3978b8"
    )


    border = (
        "2px solid #e63131"
        if highlighted
        else
        "2px solid transparent"
    )


    return f"""

    <div
        style="
            height: 42px;
            display: flex;
            align-items: center;
            gap: 9px;
            padding: 4px 8px;
            border: {border};
            font-size: 18px;
            color: {text_color};
        "
    >

        <span
            style="
                width: 25px;
                display: inline-block;
                text-align: center;
                font-size: 23px;
                color: {
                    '#b8b8b8'
                    if disabled
                    else
                    '#7d8791'
                };
            "
        >
            {symbol}
        </span>

        <span>
            {escape(text)}
        </span>

    </div>
    """


# =========================================================
# TASKS IMAGE
# =========================================================

def render_bip_tasks_image(
    folder_name
):

    safe_folder_name = escape(
        folder_name
        or
        ""
    )


    left_items = "".join([

        build_task_item(
            "▰",
            "Expandir"
        ),

        build_task_item(
            "✕",
            "Eliminar"
        ),

        build_task_item(
            "▣",
            "Copiar"
        ),

        build_task_item(
            "▤",
            "Pegar",
            disabled=True
        ),

        build_task_item(
            "●",
            "Permisos",
            disabled=True
        )
    ])


    right_items = "".join([

        build_task_item(
            "↑",
            "Cargar",
            highlighted=True
        ),

        build_task_item(
            "↓",
            "Descargar"
        ),

        build_task_item(
            "✂",
            "Cortar"
        ),

        build_task_item(
            "▥",
            "Renombrar"
        ),

        build_task_item(
            "▧",
            "Propiedades"
        ),

        build_task_item(
            "↗",
            "Exportar XLIFF"
        )
    ])


    content = f"""

    <div
        style="
            width: 520px;
            margin: 12px;
            border: 1px solid #d8dde3;
            background: #ffffff;
        "
    >

        <div
            style="
                height: 58px;
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 0 18px;
                border-bottom: 1px solid #e1e4e8;
                font-size: 23px;
                font-weight: 600;
                color: #242424;
            "
        >

            <span
                style="
                    display: inline-block;
                    width: 30px;
                    height: 21px;
                    background: #4ca3d9;
                    border: 1px solid #2f83ba;
                    border-radius: 1px;
                "
            >
            </span>

            <span>
                {safe_folder_name}
            </span>

        </div>


        <div
            style="
                display: grid;
                grid-template-columns: 1fr 1fr;
                padding: 10px;
                column-gap: 8px;
            "
        >

            <div>
                {left_items}
            </div>

            <div>
                {right_items}
            </div>

        </div>

    </div>
    """


    return (
        render_bip_html(
            build_base_html(
                content,
                width=550
            )
        )
    )


# =========================================================
# UPLOAD IMAGE
# =========================================================

def render_bip_upload_image(
    file_name
):

    safe_file_name = escape(
        file_name
        or
        ""
    )


    content = f"""

    <div
        style="
            width: 720px;
            margin: 12px;
            border: 1px solid #aeb4ba;
            background: #ffffff;
            box-shadow:
                0 1px 4px rgba(0, 0, 0, 0.18);
        "
    >

        <!-- HEADER -->

        <div
            style="
                height: 54px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 18px;
                border-bottom: 1px solid #d4d7da;
                background: #fafafa;
                font-size: 22px;
                font-weight: 600;
            "
        >

            <span>
                Cargar
            </span>

            <span
                style="
                    font-size: 24px;
                    font-weight: bold;
                "
            >
                ×
            </span>

        </div>


        <!-- BODY -->

        <div
            style="
                min-height: 245px;
                padding: 32px 40px;
                position: relative;
            "
        >

            <div
                style="
                    display: flex;
                    align-items: center;
                    margin-bottom: 28px;
                    font-size: 18px;
                "
            >

                <div
                    style="
                        width: 145px;
                        font-weight: 600;
                    "
                >
                    Archivo
                </div>


                <div
                    style="
                        height: 37px;
                        min-width: 300px;
                        padding: 8px 10px;
                        border: 1px solid #c6c9cc;
                        background: #f8f8f8;
                        color: #555;
                        overflow: hidden;
                        white-space: nowrap;
                        text-overflow: ellipsis;
                    "
                >
                    {safe_file_name}
                </div>


                <div
                    style="
                        margin-left: 8px;
                        height: 37px;
                        padding: 8px 15px;
                        border: 1px solid #9ca3aa;
                        background: #f3f3f3;
                        font-size: 15px;
                    "
                >
                    Examinar...
                </div>

            </div>


            <div
                style="
                    display: flex;
                    align-items: center;
                    gap: 14px;
                    font-size: 18px;
                "
            >

                <span
                    style="
                        font-weight: 600;
                    "
                >
                    Sobrescribir archivo existente
                </span>


                <span
                    style="
                        width: 22px;
                        height: 22px;
                        display: inline-block;
                        border: 2px solid #a5a5a5;
                        background: white;
                    "
                >
                </span>

            </div>


            <!-- BUTTONS -->

            <div
                style="
                    position: absolute;
                    right: 28px;
                    bottom: 20px;
                    display: flex;
                    gap: 10px;
                "
            >

                <div
                    style="
                        padding: 9px 19px;
                        border: 1px solid #a9b6c1;
                        background: #eef4f8;
                        font-size: 16px;
                        font-weight: 600;
                    "
                >
                    Cargar
                </div>


                <div
                    style="
                        padding: 9px 19px;
                        border: 1px solid #a9b6c1;
                        background: #eef4f8;
                        font-size: 16px;
                        font-weight: 600;
                    "
                >
                    Cancelar
                </div>

            </div>

        </div>

    </div>
    """


    return (
        render_bip_html(
            build_base_html(
                content,
                width=750
            )
        )
    )

# =========================================================
# VALIDATION / RESULT IMAGE
# =========================================================

def render_bip_validation_image(
    object_name,
    artifact_type,
    folder_name=""
):

    safe_object_name = escape(
        object_name
        or
        ""
    )


    safe_folder_name = escape(
        folder_name
        or
        ""
    )


    # =====================================================
    # TYPE
    # =====================================================

    if artifact_type == "folder":

        type_label = "Carpeta"

        icon_html = """
            <span
                style="
                    display:inline-block;
                    width:32px;
                    height:22px;
                    background:#4ca3d9;
                    border:1px solid #2f83ba;
                    border-radius:2px;
                "
            ></span>
        """


    elif artifact_type == "datamodel":

        type_label = "Data Model"

        icon_html = """
            <span
                style="
                    width:28px;
                    height:32px;
                    display:inline-flex;
                    align-items:center;
                    justify-content:center;
                    border:1px solid #8b9298;
                    background:#f2f2f2;
                    font-size:12px;
                    color:#555;
                "
            >
                DM
            </span>
        """


    else:

        type_label = "Reporte"

        icon_html = """
            <span
                style="
                    width:28px;
                    height:32px;
                    display:inline-flex;
                    align-items:center;
                    justify-content:center;
                    border:1px solid #8b9298;
                    background:#ffffff;
                    font-size:12px;
                    color:#3978b8;
                "
            >
                RPT
            </span>
        """


    folder_header = ""


    if safe_folder_name:

        folder_header = f"""

            <div
                style="
                    height:50px;
                    display:flex;
                    align-items:center;
                    gap:10px;
                    padding:0 18px;
                    background:#f5f6f7;
                    border-bottom:1px solid #d8dde3;
                    font-size:18px;
                    font-weight:600;
                "
            >

                <span
                    style="
                        display:inline-block;
                        width:25px;
                        height:18px;
                        background:#4ca3d9;
                        border:1px solid #2f83ba;
                    "
                >
                </span>

                <span>
                    {safe_folder_name}
                </span>

            </div>
        """


    content = f"""

    <div
        style="
            width:680px;
            margin:12px;
            border:1px solid #c7ccd1;
            background:#ffffff;
        "
    >

        {folder_header}


        <div
            style="
                min-height:82px;
                display:flex;
                align-items:center;
                padding:16px 22px;
                gap:15px;
            "
        >

            {icon_html}


            <div>

                <div
                    style="
                        font-size:18px;
                        color:#3978b8;
                        margin-bottom:5px;
                    "
                >
                    {safe_object_name}
                </div>


                <div
                    style="
                        font-size:13px;
                        color:#707070;
                    "
                >
                    {type_label}
                </div>

            </div>


            <div
                style="
                    margin-left:auto;
                    font-size:13px;
                    color:#4e7d35;
                    font-weight:600;
                "
            >
                Disponible
            </div>

        </div>

    </div>
    """


    return (
        render_bip_html(
            build_base_html(
                content,
                width=710
            )
        )
    )