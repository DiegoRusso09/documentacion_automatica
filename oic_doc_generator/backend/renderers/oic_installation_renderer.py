# =========================================================
# FILE:
# oic_doc_generator/backend/renderers/
# oic_installation_renderer.py
# =========================================================

import html
import os
import tempfile

from playwright.sync_api import (
    sync_playwright
)


# =========================================================
# ESCAPE
# =========================================================

def escape_html(
    value
):

    return html.escape(
        str(
            value
            or
            ""
        )
    )


# =========================================================
# TEMP PNG
# =========================================================

def create_temp_png():

    descriptor, image_path = (
        tempfile.mkstemp(
            prefix="im090_oic_",
            suffix=".png"
        )
    )


    os.close(
        descriptor
    )


    return image_path


# =========================================================
# RENDER HTML
# =========================================================

def render_html_exact(
    html_content,
    width,
    height
):

    image_path = (
        create_temp_png()
    )


    with sync_playwright() as playwright:

        browser = (
            playwright.chromium.launch(
                headless=True
            )
        )


        page = (
            browser.new_page(
                viewport={
                    "width":
                        width,

                    "height":
                        height
                },

                device_scale_factor=
                    1
            )
        )


        page.set_content(
            html_content,
            wait_until="load"
        )


        page.screenshot(
            path=image_path,
            full_page=False
        )


        browser.close()


    return image_path


# =========================================================
# COMMON SVG
# =========================================================

def icon_svg(
    icon_name,
    size=28
):

    icons = {


        # =================================================
        # SCHEDULE
        # =================================================

        "schedule":
            """
            <svg viewBox="0 0 32 32"
                 width="{size}"
                 height="{size}"
                 class="adapter-svg">

                <rect
                    x="5"
                    y="7"
                    width="22"
                    height="20"
                    rx="1"
                />

                <path d="M10 4 V10" />
                <path d="M22 4 V10" />
                <path d="M5 12 H27" />

                <path d="M10 16 H12" />
                <path d="M15 16 H17" />
                <path d="M20 16 H22" />

                <path d="M10 21 H12" />
                <path d="M15 21 H17" />

            </svg>
            """,


        # =================================================
        # REST
        # =================================================

        "rest":
            """
            <svg viewBox="0 0 32 32"
                 width="{size}"
                 height="{size}"
                 class="adapter-svg">

                <path
                    d="
                        M8 23
                        H21
                        C26 23 28 19 27 16
                        C27 12 24 10 21 10
                        C19 6 15 5 12 7
                        C9 8 8 10 8 13
                        C5 14 4 16 4 19
                        C4 21 6 23 8 23
                    "
                />

                <circle
                    cx="24"
                    cy="23"
                    r="4"
                />

                <path d="M24 20.5 V25.5" />
                <path d="M21.5 23 H26.5" />

            </svg>
            """,


        # =================================================
        # SOAP
        # =================================================

        "soap":
            """
            <svg viewBox="0 0 32 32"
                 width="{size}"
                 height="{size}"
                 class="adapter-svg">

                <path
                    d="
                        M7 22
                        H23
                        C27 22 29 19 28 16
                        C28 13 25 11 22 11
                        C20 7 16 6 13 8
                        C10 9 9 11 9 14
                        C6 14 4 16 4 19
                        C4 21 5 22 7 22
                    "
                />

                <path d="M12 17 H22" />
                <path d="M12 20 H22" />
                <path d="M12 23 H22" />

            </svg>
            """,


        # =================================================
        # DATABASE
        # =================================================

        "database":
            """
            <svg viewBox="0 0 32 32"
                 width="{size}"
                 height="{size}"
                 class="adapter-svg">

                <ellipse
                    cx="16"
                    cy="8"
                    rx="9"
                    ry="4"
                />

                <path
                    d="
                        M7 8
                        V15
                        C7 17 11 19 16 19
                        C21 19 25 17 25 15
                        V8
                    "
                />

                <path
                    d="
                        M7 15
                        V22
                        C7 24 11 26 16 26
                        C21 26 25 24 25 22
                        V15
                    "
                />

            </svg>
            """,


        # =================================================
        # GLOBE
        # ERP / HCM / WEB
        # =================================================

        "globe":
            """
            <svg viewBox="0 0 32 32"
                 width="{size}"
                 height="{size}"
                 class="adapter-svg">

                <circle
                    cx="15"
                    cy="15"
                    r="10"
                />

                <path d="M5 15 H25" />
                <path d="M15 5 C10 10 10 20 15 25" />
                <path d="M15 5 C20 10 20 20 15 25" />

                <circle
                    cx="24"
                    cy="23"
                    r="4"
                />

                <path d="M24 20.5 V25.5" />
                <path d="M21.5 23 H26.5" />

            </svg>
            """,


        # =================================================
        # FILE / FTP
        # =================================================

        "file":
            """
            <svg viewBox="0 0 32 32"
                 width="{size}"
                 height="{size}"
                 class="adapter-svg">

                <path
                    d="
                        M5 10
                        H13
                        L16 13
                        H27
                        V25
                        H5
                        Z
                    "
                />

                <path d="M5 10 V7 H13 L16 10" />

                <circle
                    cx="24"
                    cy="24"
                    r="4"
                />

            </svg>
            """,


        # =================================================
        # CLOUD FALLBACK
        # =================================================

        "cloud":
            """
            <svg viewBox="0 0 32 32"
                 width="{size}"
                 height="{size}"
                 class="adapter-svg">

                <path
                    d="
                        M7 23
                        H23
                        C27 23 29 20 28 16
                        C28 13 25 11 22 11
                        C20 7 16 6 13 8
                        C10 9 9 11 9 14
                        C6 14 4 16 4 19
                        C4 21 5 23 7 23
                    "
                />

            </svg>
            """,


        # =================================================
        # POWER
        # =================================================

        "power":
            """
            <svg viewBox="0 0 32 32"
                 width="{size}"
                 height="{size}"
                 class="adapter-svg">

                <path d="M16 4 V16" />

                <path
                    d="
                        M9 8
                        C5 11 4 15 5 19
                        C6 24 10 27 16 27
                        C22 27 26 24 27 19
                        C28 15 27 11 23 8
                    "
                />

            </svg>
            """
    }


    svg = (
        icons.get(
            icon_name,
            icons["cloud"]
        )
    )


    return svg.format(
        size=size
    )


# =========================================================
# MAP SMART TAG -> ICON
# =========================================================

def get_adapter_icon_name(
    adapter
):

    adapter = (
        str(
            adapter
            or
            ""
        )
        .strip()
        .lower()
    )


    if (
        "dbaas" in adapter
        or
        "database" in adapter
    ):

        return "database"


    if "rest" in adapter:

        return "rest"


    if "soap" in adapter:

        return "soap"


    if (
        "erp" in adapter
        or
        "hcm" in adapter
        or
        "web" in adapter
    ):

        return "globe"


    if (
        "ftp" in adapter
        or
        "sftp" in adapter
        or
        "file" in adapter
    ):

        return "file"


    return "cloud"


# =========================================================
# BUILD FLOW ICONS
# =========================================================

def build_flow_icons_html(
    integration
):

    trigger_icon = (
        integration.get(
            "trigger_icon",
            "rest"
        )
        or
        "rest"
    )


    adapter_tags = (
        integration.get(
            "adapter_tags",
            []
        )
        or
        []
    )


    parts = [

        '<div class="flow-icon">',
        icon_svg(
            trigger_icon,
            27
        ),
        '</div>',

        '<div class="flow-arrow">→</div>'
    ]


    visible_adapters = (
        adapter_tags[:3]
    )


    for adapter in visible_adapters:

        icon_name = (
            get_adapter_icon_name(
                adapter
            )
        )


        parts.extend([

            '<div class="flow-icon">',

            icon_svg(
                icon_name,
                27
            ),

            '</div>'
        ])


    remaining = (
        len(
            adapter_tags
        )
        -
        len(
            visible_adapters
        )
    )


    if remaining > 0:

        parts.append(
            (
                '<div class="extra-adapters">'
                f'+{remaining}'
                '</div>'
            )
        )


    return "".join(
        parts
    )


# =========================================================
# COMMON ROW CSS
# =========================================================

def get_row_css():

    return """
        * {
            box-sizing: border-box;
        }

        html,
        body {
            width: 1500px;
            height: 96px;

            margin: 0;
            padding: 0;

            overflow: hidden;

            background: #FFFFFF;

            font-family:
                "Segoe UI",
                "Helvetica Neue",
                Arial,
                sans-serif;

            color: #161513;
        }

        .integration-row {
            width: 1500px;
            height: 96px;

            display: grid;

            grid-template-columns:
                150px
                minmax(430px, 1fr)
                150px
                190px
                155px
                190px;

            align-items: center;

            border-top: 1px solid #DCDCDC;
            border-bottom: 1px solid #DCDCDC;

            background: #FFFFFF;
        }

        .integration-row > div {
            min-width: 0;

            padding:
                14px
                16px;
        }

        .flow-icons {
            display: flex;

            align-items: center;

            gap: 6px;

            white-space: nowrap;
        }

        .flow-icon {
            width: 28px;
            height: 28px;

            display: inline-flex;

            align-items: center;

            justify-content: center;

            flex:
                0
                0
                28px;
        }

        .adapter-svg {
            fill: none;

            stroke: #161513;

            stroke-width: 1.7;

            stroke-linecap: round;

            stroke-linejoin: round;
        }

        .flow-arrow {
            margin:
                0
                1px;

            font-size: 17px;

            font-weight: 600;
        }

        .extra-adapters {
            margin-left: 2px;

            font-size: 13px;
        }

        .integration-name {
            display: flex;

            flex-direction: column;

            gap: 5px;
        }

        .integration-name strong {
            overflow: hidden;

            font-size: 16px;

            font-weight: 500;

            line-height: 1.25;

            text-overflow: ellipsis;

            white-space: nowrap;
        }

        .integration-name span {
            color: #4C4844;

            font-size: 12px;
        }

        .version,
        .style {
            font-size: 14px;
        }

        .status {
            display: flex;

            justify-content: center;
        }

        .status-badge {
            min-width: 78px;

            min-height: 26px;

            padding:
                5px
                13px;

            display: inline-flex;

            align-items: center;

            justify-content: center;

            border-radius: 999px;

            font-size: 13px;

            line-height: 1;
        }

        .status-configured {
            background: #DDECF2;
        }

        .status-active {
            background: #D7EDC5;
        }

        .actions {
            align-self: stretch;

            padding:
                0
                18px !important;

            display: flex;

            align-items: center;

            justify-content: flex-end;

            gap: 16px;

            background: #F7F7F8;
        }

        .action-icon {
            position: relative;

            width: 34px;
            height: 34px;

            display: inline-flex;

            align-items: center;

            justify-content: center;
        }

        .action-icon svg {
            width: 25px;
            height: 25px;
        }

        .activate-focus::after {
            content: "";

            position: absolute;

            inset: -5px;

            border: 2px solid #C74634;

            border-radius: 50%;
        }

        .more {
            font-size: 23px;

            letter-spacing: 1px;
        }

        .expand {
            font-size: 23px;
        }
    """


# =========================================================
# BUILD INTEGRATION ROW HTML
# =========================================================

def build_integration_row_html(
    integration,
    status="Configured",
    highlight_activate=False
):

    name = escape_html(
        integration.get(
            "name",
            ""
        )
    )


    code = escape_html(
        integration.get(
            "code",
            ""
        )
    )


    version = escape_html(
        integration.get(
            "version_display",
            ""
        )
        or
        integration.get(
            "version",
            ""
        )
    )


    style = escape_html(
        integration.get(
            "style_display",
            ""
        )
        or
        integration.get(
            "type",
            ""
        )
    )


    flow_html = (
        build_flow_icons_html(
            integration
        )
    )


    is_active = (
        str(
            status
        ).lower()
        ==
        "active"
    )


    status_class = (

        "status-active"

        if is_active

        else

        "status-configured"

    )


    action_html = ""


    if not is_active:

        focus_class = (

            " activate-focus"

            if highlight_activate

            else
            ""

        )


        action_html = f"""
            <div class="action-icon{focus_class}">
                {icon_svg("power", 25)}
            </div>

            <div class="more">
                •••
            </div>

            <div class="expand">
                ⌄
            </div>
        """


    else:

        action_html = """
            <div class="more">
                •••
            </div>

            <div class="expand">
                ⌄
            </div>
        """


    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <style>

            {get_row_css()}

        </style>

    </head>

    <body>

        <div class="integration-row">

            <div class="flow-icons">

                {flow_html}

            </div>


            <div class="integration-name">

                <strong>
                    {name}
                </strong>

                <span>
                    {code}
                </span>

            </div>


            <div class="version">
                {version}
            </div>


            <div class="style">
                {style}
            </div>


            <div class="status">

                <span
                    class="
                        status-badge
                        {status_class}
                    "
                >
                    {escape_html(status)}
                </span>

            </div>


            <div class="actions">

                {action_html}

            </div>

        </div>

    </body>

    </html>
    """


# =========================================================
# RENDER INTEGRATION ROW
# =========================================================

def render_oic_integration_row_image(
    integration,
    status="Configured",
    highlight_activate=False
):

    html_content = (
        build_integration_row_html(

            integration,

            status=status,

            highlight_activate=
                highlight_activate

        )
    )


    return render_html_exact(
        html_content,
        width=1500,
        height=96
    )


# =========================================================
# RENDER ACTIVATE SYMBOL
# =========================================================

def render_oic_activate_icon_image():

    html_content = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <style>

            * {{
                box-sizing: border-box;
            }}

            html,
            body {{

                width: 48px;
                height: 48px;

                margin: 0;

                display: flex;

                align-items: center;

                justify-content: center;

                overflow: hidden;

                background: #FFFFFF;
            }}

            svg {{

                fill: none;

                stroke: #161513;

                stroke-width: 1.8;

                stroke-linecap: round;

                stroke-linejoin: round;
            }}

        </style>

    </head>

    <body>

        {icon_svg("power", 34)}

    </body>

    </html>
    """


    return render_html_exact(
        html_content,
        width=48,
        height=48
    )


# =========================================================
# BUILD ACTIVATION DRAWER
# =========================================================

def build_activation_drawer_html(
    integration
):

    name = escape_html(
        integration.get(
            "name",
            ""
        )
    )


    version = escape_html(
        integration.get(
            "version_display",
            ""
        )
        or
        integration.get(
            "version",
            ""
        )
    )


    return f"""
    <!DOCTYPE html>

    <html lang="en">

    <head>

        <meta charset="UTF-8">

        <style>

            * {{
                box-sizing: border-box;
            }}


            html,
            body {{

                width: 424px;
                height: 760px;

                margin: 0;

                overflow: hidden;

                background: #FFFFFF;

                color: #161513;

                font-family:
                    "Segoe UI",
                    "Helvetica Neue",
                    Arial,
                    sans-serif;
            }}


            .drawer {{

                width: 424px;
                height: 760px;

                display: flex;

                flex-direction: column;

                background: #FFFFFF;

                border-left:
                    1px solid #D7D4D1;
            }}


            .drawer-header {{

                min-height: 92px;

                padding:
                    18px
                    18px
                    17px
                    24px;

                display: flex;

                align-items: flex-start;

                justify-content: space-between;

                background: #F1EFED;
            }}


            .drawer-header-text {{

                min-width: 0;

                padding-right: 15px;
            }}


            .drawer-header h1 {{

                margin:
                    0
                    0
                    5px;

                color: #161513;

                font-size: 22px;

                font-weight: 700;

                line-height: 1.2;
            }}


            .drawer-header p {{

                margin: 0;

                overflow: hidden;

                color: #5B5652;

                font-size: 14px;

                line-height: 1.4;

                text-overflow: ellipsis;

                white-space: nowrap;
            }}


            .help {{

                width: 17px;
                height: 17px;

                margin-top: 5px;

                display: flex;

                align-items: center;

                justify-content: center;

                flex:
                    0
                    0
                    auto;

                border:
                    1.7px solid #161513;

                border-radius: 50%;

                font-size: 11px;

                font-weight: 700;
            }}


            .drawer-body {{

                flex: 1;

                overflow: hidden;

                background: #FFFFFF;
            }}


            .section {{

                padding:
                    20px
                    24px;
            }}


            .section h2 {{

                margin:
                    0
                    0
                    11px;

                font-size: 14px;

                font-weight: 650;

                line-height: 1.35;
            }}


            .radio-row,
            .checkbox-row {{

                height: 32px;

                display: flex;

                align-items: center;

                gap: 9px;

                color: #312E2B;

                font-size: 14px;
            }}


            .radio {{

                position: relative;

                width: 15px;
                height: 15px;

                flex:
                    0
                    0
                    15px;

                border:
                    1.4px solid #312E2B;

                border-radius: 50%;

                background: #FFFFFF;
            }}


            .radio.selected::after {{

                content: "";

                position: absolute;

                top: 3px;
                left: 3px;

                width: 7px;
                height: 7px;

                border-radius: 50%;

                background: #312E2B;
            }}


            .checkbox {{

                width: 15px;
                height: 15px;

                flex:
                    0
                    0
                    15px;

                border:
                    1.4px solid #312E2B;

                border-radius: 1px;

                background: #FFFFFF;
            }}


            .info-row {{

                margin-top: 2px;

                display: flex;

                align-items: flex-start;

                gap: 7px;
            }}


            .info-icon {{

                width: 14px;
                height: 14px;

                margin-top: 1px;

                display: flex;

                align-items: center;

                justify-content: center;

                flex:
                    0
                    0
                    14px;

                border-radius: 50%;

                background: #0572A1;

                color: #FFFFFF;

                font-size: 10px;

                font-weight: 700;
            }}


            .info-row p {{

                margin: 0;

                color: #5B5652;

                font-size: 10.5px;

                line-height: 1.35;
            }}


            .runtime {{

                margin-top: 7px;

                padding-top: 20px;

                border-top:
                    1px solid #E3E0DD;
            }}


            .runtime-info {{

                margin-bottom: 19px;
            }}


            .drawer-footer {{

                height: 66px;

                padding:
                    15px
                    24px;

                display: flex;

                align-items: center;

                justify-content: flex-end;

                gap: 9px;

                flex:
                    0
                    0
                    66px;

                border-top:
                    1px solid #DDD9D6;

                background: #F1EFED;
            }}


            .button {{

                height: 34px;

                padding:
                    0
                    14px;

                border-radius: 3px;

                font-family: inherit;

                font-size: 13px;

                font-weight: 600;
            }}


            .cancel {{

                min-width: 72px;

                border:
                    1px solid #77736F;

                background: #FFFFFF;

                color: #312E2B;
            }}


            .activate {{

                position: relative;

                min-width: 79px;

                border:
                    1px solid #312E2B;

                background: #312E2B;

                color: #FFFFFF;
            }}


            .activate::after {{

                content: "";

                position: absolute;

                inset: -5px;

                border:
                    2px solid #C74634;

                border-radius: 5px;
            }}

        </style>

    </head>


    <body>

        <aside class="drawer">


            <header class="drawer-header">

                <div class="drawer-header-text">

                    <h1>
                        Activate integration
                    </h1>

                    <p>
                        {name} ({version})
                    </p>

                </div>


                <div class="help">
                    ?
                </div>

            </header>


            <main class="drawer-body">


                <section class="section">

                    <h2>
                        Select tracing level
                    </h2>


                    <div class="radio-row">

                        <span class="radio selected"></span>

                        <span>
                            Production
                        </span>

                    </div>


                    <div class="radio-row">

                        <span class="radio"></span>

                        <span>
                            Audit
                        </span>

                    </div>


                    <div class="radio-row">

                        <span class="radio"></span>

                        <span>
                            Debug (Not recommended)
                        </span>

                    </div>


                    <div class="info-row">

                        <span class="info-icon">
                            i
                        </span>

                        <p>
                            All activities outside loops and
                            invoke/logger activity inside loops
                            (up to a 1000 iterations) are shown
                            in the activity stream and this data
                            is retained for a period of 32 days.
                        </p>

                    </div>

                </section>


                <section class="section runtime">

                    <h2>
                        Configure runtime options
                    </h2>


                    <div class="checkbox-row">

                        <span class="checkbox"></span>

                        <span>
                            Allow to run again
                        </span>

                    </div>


                    <div class="info-row runtime-info">

                        <span class="info-icon">
                            i
                        </span>

                        <p>
                            When you run again an integration,
                            it creates a new instance and runs
                            again any transactions.
                        </p>

                    </div>


                    <div class="checkbox-row">

                        <span class="checkbox"></span>

                        <span>
                            Enable payload validation
                        </span>

                    </div>

                </section>

            </main>


            <footer class="drawer-footer">

                <button class="button cancel">
                    Cancel
                </button>

                <button class="button activate">
                    Activate
                </button>

            </footer>


        </aside>

    </body>

    </html>
    """


# =========================================================
# RENDER ACTIVATION DRAWER
# =========================================================

def render_oic_activation_drawer_image(
    integration
):

    return render_html_exact(

        build_activation_drawer_html(
            integration
        ),

        width=424,

        height=760

    )


# =========================================================
# PACKAGE ACTIVE
# =========================================================

def render_oic_package_active_image(
    package_name,
    integrations
):

    integrations = (
        integrations
        or
        []
    )


    rows = []


    for integration in integrations:

        name = escape_html(
            integration.get(
                "name",
                ""
            )
        )


        version = escape_html(
            integration.get(
                "version_display",
                ""
            )
            or
            integration.get(
                "version",
                ""
            )
        )


        style = escape_html(
            integration.get(
                "style_display",
                ""
            )
        )


        rows.append(
            f"""
            <div class="package-row">

                <div>
                    {name} ({version})
                </div>

                <div>
                    {style}
                </div>

                <div>
                    <span class="active-badge">
                        Active
                    </span>
                </div>

            </div>
            """
        )


    row_html = "".join(
        rows
    )


    height = (
        175
        +
        (
            max(
                len(
                    integrations
                ),
                1
            )
            *
            48
        )
    )


    html_content = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <style>

            * {{
                box-sizing: border-box;
            }}


            html,
            body {{

                width: 1500px;
                height: {height}px;

                margin: 0;

                overflow: hidden;

                background: #FFFFFF;

                color: #161513;

                font-family:
                    "Segoe UI",
                    Arial,
                    sans-serif;
            }}


            .package {{

                width: 1500px;

                background: #FFFFFF;
            }}


            .package-header {{

                min-height: 108px;

                padding:
                    22px
                    36px;

                display: flex;

                align-items: center;

                justify-content: space-between;

                border-bottom:
                    1px solid #E1E1E1;
            }}


            .package-header h2 {{

                margin:
                    0
                    0
                    4px;

                font-size: 22px;
            }}


            .package-header p {{

                margin: 0;

                font-size: 14px;
            }}


            .steps {{

                display: flex;

                align-items: flex-start;
            }}


            .step {{

                width: 92px;

                display: flex;

                flex-direction: column;

                align-items: center;

                gap: 6px;

                color: #2F6B20;

                font-size: 12px;

                font-weight: 600;
            }}


            .check {{

                width: 21px;
                height: 21px;

                display: flex;

                align-items: center;

                justify-content: center;

                border-radius: 50%;

                background: #3F7D20;

                color: #FFFFFF;

                font-size: 13px;
            }}


            .line {{

                width: 45px;
                height: 1px;

                margin-top: 10px;

                background: #888481;
            }}


            .table-header,
            .package-row {{

                display: grid;

                grid-template-columns:
                    1.7fr
                    1fr
                    .6fr;

                align-items: center;
            }}


            .table-header {{

                height: 48px;

                padding:
                    0
                    35px;

                border-bottom:
                    1px solid #DDDDDD;

                font-weight: 600;
            }}


            .package-row {{

                height: 48px;

                padding:
                    0
                    35px;

                border-bottom:
                    1px solid #E5E5E5;

                font-size: 14px;
            }}


            .active-badge {{

                padding:
                    5px
                    14px;

                border-radius: 999px;

                background: #D7EDC5;

                font-size: 13px;
            }}

        </style>

    </head>

    <body>

        <section class="package">

            <header class="package-header">

                <div>

                    <h2>
                        Review and activate
                    </h2>

                    <p>
                        Check if all the integrations are ready to activate
                    </p>

                </div>


                <div class="steps">

                    <div class="step">

                        <span class="check">
                            ✓
                        </span>

                        <span>
                            Connections
                        </span>

                    </div>


                    <span class="line"></span>


                    <div class="step">

                        <span class="check">
                            ✓
                        </span>

                        <span>
                            Lookups
                        </span>

                    </div>


                    <span class="line"></span>


                    <div class="step">

                        <span class="check">
                            ✓
                        </span>

                        <span>
                            Libraries
                        </span>

                    </div>


                    <span class="line"></span>


                    <div class="step">

                        <span class="check">
                            ✓
                        </span>

                        <span>
                            Activation
                        </span>

                    </div>

                </div>

            </header>


            <div class="table-header">

                <div>
                    Name
                </div>

                <div>
                    Style
                </div>

                <div>
                    Status
                </div>

            </div>


            {row_html}

        </section>

    </body>

    </html>
    """


    return render_html_exact(
        html_content,
        width=1500,
        height=height
    )