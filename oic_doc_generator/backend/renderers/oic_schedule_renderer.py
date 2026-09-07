# =========================================================
# FILE:
# oic_doc_generator/backend/renderers/
# oic_schedule_renderer.py
# =========================================================

from oic_doc_generator.backend.renderers.oic_installation_renderer import (
    render_html_exact,
    escape_html,
    icon_svg
)


# =========================================================
# COMMON DATA
# =========================================================

def get_schedule_data(
    integration
):

    schedule = (
        integration.get(
            "schedule",
            {}
        )
        or
        {}
    )


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


    code = escape_html(
        integration.get(
            "code",
            ""
        )
    )


    schedule_name = escape_html(
        schedule.get(
            "name",
            ""
        )
        or
        (
            "Schedule "
            +
            code
        )
    )


    ical = escape_html(
        schedule.get(
            "ical_expression",
            ""
        )
    )


    return {

        "name":
            name,

        "version":
            version,

        "code":
            code,

        "schedule_name":
            schedule_name,

        "ical":
            ical
    }


# =========================================================
# ACTION MENU
# =========================================================

def render_oic_schedule_menu_image(
    integration,
    action="Schedule"
):

    selected_action = (
        str(
            action
            or
            ""
        ).strip()
    )


    options = [

        "Configure",

        "Schedule",

        "View",

        "Update property values",

        "Run",

        "Track instances",

        "Configure activation",

        "Create new version",

        "Clone",

        "Export"
    ]


    rows = []


    for option in options:

        selected_class = (

            "menu-item selected"

            if option.lower()
            ==
            selected_action.lower()

            else

            "menu-item"

        )


        rows.append(
            f"""
            <div class="{selected_class}">
                {escape_html(option)}
            </div>
            """
        )


    menu_html = "".join(
        rows
    )

    power_icon = (
        icon_svg(
            "power",
            size=28
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

                width: 305px;
                height: 575px;

                margin: 0;

                overflow: hidden;

                background: #F7F7F8;

                color: #161513;

                font-family:
                    "Segoe UI",
                    Arial,
                    sans-serif;
            }}


            .screen {{

                position: relative;

                width: 305px;
                height: 575px;

                background: #F7F7F8;
            }}


            .menu {{

                position: absolute;

                top: 5px;
                left: 22px;

                width: 204px;

                overflow: hidden;

                border-radius: 2px;

                background: #FFFFFF;

                box-shadow:
                    0
                    2px
                    8px
                    rgba(
                        0,
                        0,
                        0,
                        .22
                    );
            }}


            .menu-item {{

                min-height: 48px;

                padding:
                    0
                    16px;

                display: flex;

                align-items: center;

                border-bottom:
                    1px solid
                    #E5E5E5;

                background:
                    #FFFFFF;

                font-size: 16px;
            }}


            .menu-item:last-child {{

                border-bottom:
                    none;
            }}


            .menu-item.selected {{

                background:
                    #F0F4F5;

                font-weight:
                    600;

                box-shadow:
                    inset
                    3px
                    0
                    0
                    #0572A1;
            }}


            .row-actions {{

                position: absolute;

                right: 0;
                bottom: 7px;

                width: 188px;
                height: 58px;

                display: flex;

                align-items: center;

                justify-content: flex-end;

                gap: 11px;

                padding-right: 12px;

                background: #F7F7F8;

                border-top:
                    1px solid
                    #E0E0E0;
            }}


            .active {{

                margin-right: 14px;

                padding:
                    5px
                    13px;

                border-radius:
                    18px;

                background:
                    #D7EDC5;

                font-size:
                    13px;
            }}


            .power {{

                width:
                    30px;

                height:
                    30px;

                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    center;
            }}


            .power svg {{

                width:
                    28px;

                height:
                    28px;

                fill:
                    none;

                stroke:
                    #161513;

                stroke-width:
                    1.8;

                stroke-linecap:
                    round;

                stroke-linejoin:
                    round;
            }}


            .more {{

                width: 29px;
                height: 43px;

                display: flex;

                align-items: center;

                justify-content: center;

                border:
                    1px solid #0572A1;

                border-radius:
                    4px;

                color:
                    #161513;

                font-size:
                    20px;

                letter-spacing:
                    1px;
            }}


            .arrow {{

                font-size:
                    27px;

                line-height:
                    1;
            }}

        </style>

    </head>


    <body>

        <div class="screen">

            <div class="menu">

                {menu_html}

            </div>


            <div class="row-actions">

                <span class="active">
                    Active
                </span>

                    <span class="power">
                        {power_icon}
                    </span>

                <span class="more">
                    •••
                </span>

                <span class="arrow">
                    ⌄
                </span>

            </div>

        </div>

    </body>

    </html>
    """


    return render_html_exact(
        html_content,
        width=305,
        height=575
    )


# =========================================================
# SCHEDULE OVERVIEW
# =========================================================

def render_oic_schedule_overview_image(
    integration
):

    data = (
        get_schedule_data(
            integration
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
                height: 590px;

                margin: 0;

                overflow: hidden;

                background: #FFFFFF;

                color: #FFFFFF;

                font-family:
                    "Segoe UI",
                    Arial,
                    sans-serif;
            }}


            .top {{

                height: 46px;

                padding:
                    0
                    22px;

                display: flex;

                align-items: center;

                justify-content: space-between;

                background:
                    #312E2B;
            }}


            .oracle {{

                font-size:
                    23px;

                font-weight:
                    700;
            }}


            .env {{

                font-size:
                    14px;
            }}


            .page {{

                height:
                    255px;

                padding:
                    14px
                    30px;

                background:
                    #494D53;
            }}


            .title {{

                margin:
                    0
                    0
                    23px;

                font-family:
                    Georgia,
                    serif;

                font-size:
                    27px;

                font-weight:
                    400;
            }}


            .schedule-card {{

                min-height:
                    68px;

                padding:
                    15px
                    18px;

                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    space-between;

                background:
                    #303338;

                border:
                    1px solid
                    #666A70;
            }}


            .schedule-left {{

                display:
                    flex;

                align-items:
                    center;

                gap:
                    13px;
            }}


            .schedule-name {{

                font-size:
                    16px;

                font-weight:
                    700;
            }}


            .stopped {{

                padding:
                    4px
                    10px;

                border-radius:
                    16px;

                background:
                    #D9412C;

                font-size:
                    12px;
            }}


            .buttons {{

                display:
                    flex;

                gap:
                    8px;
            }}


            .button {{

                height:
                    36px;

                padding:
                    0
                    15px;

                border:
                    1px solid
                    #6E7378;

                border-radius:
                    3px;

                display:
                    flex;

                align-items:
                    center;

                gap:
                    8px;

                background:
                    transparent;

                color:
                    #FFFFFF;

                font-size:
                    13px;

                font-weight:
                    600;
            }}


            .date {{

                margin-top:
                    12px;

                text-align:
                    right;

                font-size:
                    13px;
            }}


            .future {{

                height:
                    289px;

                padding:
                    15px
                    36px;

                background:
                    #FFFFFF;

                color:
                    #161513;
            }}


            .future strong {{

                display:
                    block;

                margin-bottom:
                    17px;

                font-size:
                    14px;
            }}


            .future-header {{

                height:
                    42px;

                display:
                    grid;

                grid-template-columns:
                    1fr
                    1fr;

                align-items:
                    center;

                border-top:
                    1px solid #EEE;

                border-bottom:
                    1px solid #DDD;

                font-size:
                    13px;

                font-weight:
                    600;
            }}


            .empty {{

                padding-top:
                    11px;

                font-size:
                    13px;
            }}

        </style>

    </head>


    <body>

        <div class="top">

            <div class="oracle">
                ORACLE
            </div>

            <div class="env">
                Oracle Integration (Prod)
            </div>

        </div>


        <section class="page">

            <h1 class="title">

                Schedule and future runs -
                {data["name"]}
                ({data["version"]})

            </h1>


            <div class="schedule-card">

                <div class="schedule-left">

                    <span>
                        ›
                    </span>

                    <span class="schedule-name">
                        {data["schedule_name"]}
                    </span>

                    <span class="stopped">
                        Stopped
                    </span>

                </div>


                <div class="buttons">

                    <div class="button">
                        ◉ Start
                    </div>

                    <div class="button">
                        ✎ Edit
                    </div>

                    <div class="button">
                        ☰
                    </div>

                </div>

            </div>


            <div class="date">
                Schedule configuration
            </div>

        </section>


        <section class="future">

            <strong>
                0 future instances
            </strong>


            <div class="future-header">

                <span>
                    Type
                </span>

                <span>
                    Scheduled time
                </span>

            </div>


            <div class="empty">

                No data to display.
                Start schedule to see future instances.

            </div>

        </section>

    </body>

    </html>
    """


    return render_html_exact(
        html_content,
        width=1500,
        height=590
    )


# =========================================================
# ICAL EDITOR
# =========================================================

def render_oic_ical_editor_image(
    integration
):

    data = (
        get_schedule_data(
            integration
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

                width:
                    1500px;

                height:
                    610px;

                margin:
                    0;

                overflow:
                    hidden;

                background:
                    #FFFFFF;

                color:
                    #161513;

                font-family:
                    "Segoe UI",
                    Arial,
                    sans-serif;
            }}


            .top {{

                height:
                    46px;

                padding:
                    0
                    24px;

                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    space-between;

                background:
                    #312E2B;

                color:
                    #FFFFFF;
            }}


            .oracle {{

                font-size:
                    23px;

                font-weight:
                    700;
            }}


            .header {{

                height:
                    70px;

                padding:
                    0
                    28px;

                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    space-between;

                background:
                    #494D53;

                color:
                    #FFFFFF;
            }}


            .title {{

                font-family:
                    Georgia,
                    serif;

                font-size:
                    26px;
            }}


            .save {{

                padding:
                    10px
                    18px;

                border-radius:
                    3px;

                background:
                    #FFFFFF;

                color:
                    #161513;

                font-size:
                    13px;

                font-weight:
                    600;
            }}


            .content {{

                margin:
                    14px
                    20px;

                padding:
                    20px;

                min-height:
                    455px;

                border:
                    1px solid #DDD;

                background:
                    #FFFFFF;
            }}


            .section-title {{

                margin-bottom:
                    15px;

                padding-bottom:
                    10px;

                border-bottom:
                    1px solid #DDD;

                font-size:
                    14px;
            }}


            .radios {{

                display:
                    flex;

                gap:
                    30px;

                margin-bottom:
                    12px;

                font-size:
                    14px;
            }}


            .radio {{

                display:
                    inline-flex;

                align-items:
                    center;

                gap:
                    7px;
            }}


            .circle {{

                width:
                    14px;

                height:
                    14px;

                border:
                    1px solid #222;

                border-radius:
                    50%;
            }}


            .circle.selected {{

                position:
                    relative;
            }}


            .circle.selected::after {{

                content:
                    "";

                position:
                    absolute;

                inset:
                    3px;

                border-radius:
                    50%;

                background:
                    #161513;
            }}


            .ical-box {{

                width:
                    455px;

                margin-left:
                    0;
            }}


            .validate {{

                margin-left:
                    322px;

                margin-bottom:
                    0;

                padding:
                    10px
                    14px;

                display:
                    inline-block;

                border:
                    1px solid #777;

                border-radius:
                    3px;

                font-size:
                    12px;

                font-weight:
                    600;
            }}


            textarea {{

                width:
                    455px;

                height:
                    98px;

                padding:
                    12px;

                resize:
                    none;

                border:
                    1px solid #777;

                border-radius:
                    3px;

                font-family:
                    "Segoe UI",
                    Arial,
                    sans-serif;

                font-size:
                    13px;
            }}


            .effective {{

                margin-top:
                    25px;

                padding-top:
                    10px;

                border-top:
                    1px solid #DDD;

                font-size:
                    13px;
            }}


            .effective strong {{

                display:
                    block;

                margin-bottom:
                    16px;
            }}


            .field {{

                margin:
                    12px
                    0;
            }}


            .label {{

                display:
                    inline-block;

                width:
                    70px;
            }}


            .timezone {{

                display:
                    inline-block;

                min-width:
                    300px;

                padding:
                    9px
                    12px;

                border:
                    1px solid #AAA;

                border-radius:
                    3px;
            }}


            .note {{

                margin-top:
                    15px;

                color:
                    #777;

                font-size:
                    13px;

                font-style:
                    italic;
            }}

        </style>

    </head>


    <body>

        <div class="top">

            <span class="oracle">
                ORACLE
            </span>

            <span>
                Oracle Integration (Prod)
            </span>

        </div>


        <div class="header">

            <span class="title">

                {data["schedule_name"]}

            </span>

            <span class="save">
                Save
            </span>

        </div>


        <div class="content">

            <div class="section-title">
                Define recurrence
            </div>


            <div class="radios">

                <span class="radio">

                    <span class="circle"></span>

                    Simple

                </span>


                <span class="radio">

                    <span class="circle selected"></span>

                    iCal

                </span>

            </div>


            <div class="ical-box">

                <div class="validate">
                    Validate expression
                </div>


                <textarea>{data["ical"]}</textarea>

            </div>


            <div class="effective">

                <strong>
                    This schedule is effective:
                </strong>


                <div class="field">

                    <span class="label">
                        From
                    </span>

                    Configurar según la ventana de pase

                </div>


                <div class="field">

                    <span class="label">
                        Until
                    </span>

                    Never (repeat indefinitely)

                </div>


                <div class="field">

                    <span class="label">
                        Time zone
                    </span>

                    <span class="timezone">
                        (UTC-05:00) Lima - Peru Standard Time
                    </span>

                </div>


                <div class="note">

                    You must start up the schedule
                    for these settings to take effect

                </div>

            </div>

        </div>

    </body>

    </html>
    """


    return render_html_exact(
        html_content,
        width=1500,
        height=610
    )


# =========================================================
# START SCHEDULE DIALOG
# =========================================================

def render_oic_start_schedule_dialog_image(
    integration,
    execution_user="usuario.integrador"
):

    data = (
        get_schedule_data(
            integration
        )
    )


    execution_user = escape_html(
        execution_user
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

                width:
                    600px;

                height:
                    340px;

                margin:
                    0;

                overflow:
                    hidden;

                background:
                    #FFFFFF;

                color:
                    #161513;

                font-family:
                    "Segoe UI",
                    Arial,
                    sans-serif;
            }}


            .dialog {{

                width:
                    600px;

                height:
                    340px;

                padding:
                    38px
                    34px
                    30px;

                border:
                    1px solid #CFCFCF;

                border-radius:
                    5px;

                background:
                    #FFFFFF;

                box-shadow:
                    0
                    4px
                    14px
                    rgba(
                        0,
                        0,
                        0,
                        .25
                    );
            }}


            h1 {{

                margin:
                    0
                    0
                    28px;

                font-family:
                    Georgia,
                    serif;

                font-size:
                    25px;

                font-weight:
                    700;
            }}


            .schedule-name {{

                margin-left:
                    30px;

                margin-bottom:
                    10px;

                font-size:
                    15px;

                font-weight:
                    700;
            }}


            .user-row {{

                margin-left:
                    30px;

                display:
                    flex;

                align-items:
                    center;

                gap:
                    14px;
            }}


            .user-label {{

                width:
                    104px;

                font-size:
                    14px;
            }}


            .select {{

                width:
                    250px;

                padding:
                    11px
                    14px;

                display:
                    flex;

                justify-content:
                    space-between;

                border:
                    1px solid #999;

                border-radius:
                    4px;

                font-size:
                    14px;
            }}


            .question {{

                margin:
                    10px
                    0
                    0
                    30px;

                font-size:
                    14px;

                line-height:
                    1.35;
            }}


            .info {{

                display:
                    inline-flex;

                width:
                    14px;

                height:
                    14px;

                margin-right:
                    8px;

                align-items:
                    center;

                justify-content:
                    center;

                border-radius:
                    50%;

                background:
                    #161513;

                color:
                    #FFFFFF;

                font-size:
                    10px;
            }}


            .footer {{

                position:
                    absolute;

                right:
                    34px;

                bottom:
                    31px;

                display:
                    flex;

                gap:
                    7px;
            }}


            .button {{

                height:
                    37px;

                padding:
                    0
                    17px;

                display:
                    flex;

                align-items:
                    center;

                border-radius:
                    3px;

                font-size:
                    13px;

                font-weight:
                    600;
            }}


            .cancel {{

                border:
                    1px solid #888;

                background:
                    #FFFFFF;
            }}


            .confirm {{

                border:
                    1px solid #312E2B;

                background:
                    #312E2B;

                color:
                    #FFFFFF;
            }}

        </style>

    </head>


    <body>

        <div class="dialog">

            <h1>
                Start schedule
            </h1>


            <div class="schedule-name">
                {data["schedule_name"]}
            </div>


            <div class="user-row">

                <span class="user-label">
                    Start schedule<br>
                    as user
                </span>

                <span class="select">

                    {execution_user}

                    <span>
                        ▾
                    </span>

                </span>

            </div>


            <div class="question">

                <span class="info">
                    i
                </span>

                Are you sure you want to start the
                schedule as user {execution_user}?

            </div>


            <div class="footer">

                <span class="button cancel">
                    Cancel
                </span>

                <span class="button confirm">
                    Confirm
                </span>

            </div>

        </div>

    </body>

    </html>
    """


    return render_html_exact(
        html_content,
        width=600,
        height=340
    )