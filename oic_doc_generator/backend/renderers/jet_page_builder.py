# =========================================================
# FILE:
# oic_doc_generator/backend/renderers/jet_page_builder.py
# =========================================================
#
# Arma un HTML que dibuja una página de Visual Builder con
# Oracle JET real (tema Redwood) cargado desde el CDN de
# Oracle, en lugar de traducir las etiquetas oj-* a HTML
# simple. Así los oj-button, oj-c-select-single, oj-table,
# oj-form-layout, oj-bind-if, oj-c-dialog, etc. se ven como
# en el ERP.
#
# Qué se simula del runtime de Visual Builder:
#   $variables / $page / $flow / $application  con los
#       valores por defecto de *-page.json, *-flow.json y
#       app.json (incluye expresiones [[ ]] / {{ }} simples)
#   ArrayDataProvider            con sus datos por defecto
#   ServiceDataProvider / BO     vacíos (no hay backend)
#   $functions                   módulo JS de la página
#   $listeners                   funciones vacías
#
# Si el CDN no responde, screenshot_renderer usa el HTML del
# traductor anterior (oj_translator) como respaldo.
#
# Variables de entorno opcionales:
#   VB_RENDER_MODE    "jet" (por defecto) o "legacy"
#   VB_JET_VERSION    versión de JET del CDN (19.0.0)
#   VB_ICON_FONT_CSS  hoja de la fuente de íconos oj-ux-ico
# =========================================================

import json
import os
import re


JET_VERSION = os.getenv(
    "VB_JET_VERSION",
    "19.0.0"
)

JET_CDN = (
    f"https://static.oracle.com/cdn/jet/{JET_VERSION}"
)

ICON_FONT_CSS = os.getenv(
    "VB_ICON_FONT_CSS",
    "https://static.oracle.com/cdn/fnd/gallery/2604.0.0/"
    "images/iconfont/ojuxIconFont.min.css"
)

RENDER_MODE = os.getenv(
    "VB_RENDER_MODE",
    "jet"
).strip().lower()

# Comparaciones tipo $application.variables.perfil === 'AUDITOR'
ENUM_COMPARISON_PATTERN = re.compile(
    r"\$(application|flow|page)?\.?variables\.([A-Za-z_]\w*)"
    r"\s*[!=]==?\s*['\"]([^'\"]+)['\"]"
)


# =========================================================
# FILES
# =========================================================

def _read_text(path):

    if not path or not os.path.isfile(path):
        return ""

    for encoding in ("utf-8", "latin-1"):

        try:
            with open(path, "r", encoding=encoding) as file:
                return file.read()
        except (UnicodeDecodeError, OSError):
            continue

    return ""


def _read_json(path):

    text = _read_text(path)

    if not text:
        return {}

    try:
        data = json.loads(text)
    except ValueError:
        return {}

    return data if isinstance(data, dict) else {}


def _page_files(page_html_path):

    # main-x-page.html -> main-x-page.json / main-x-page.js
    base = re.sub(r"\.html$", "", page_html_path)

    return (
        base + ".json",
        base + ".js"
    )


def _flow_files(page_html_path, application_folder):

    # flows/<flow>/pages/x-page.html -> flows/<flow>/<flow>-flow.json
    pages_folder = os.path.dirname(page_html_path)

    if os.path.basename(pages_folder) != "pages":
        return ("", "")

    flow_folder = os.path.dirname(pages_folder)

    flow_name = os.path.basename(flow_folder)

    return (
        os.path.join(flow_folder, f"{flow_name}-flow.json"),
        os.path.join(flow_folder, f"{flow_name}-flow.js")
    )


# =========================================================
# STATE
# =========================================================

def _scope(model):

    return {
        "variables": model.get("variables") or {},
        "constants": model.get("constants") or {},
        "types": model.get("types") or {}
    }


def _enum_overrides(html, scopes):

    # Si una variable se compara con textos fijos
    # (=== 'AUDITOR', === 'EMPLEADO') y su valor por defecto
    # no es ninguno de ellos (p. ej. 'DESCONOCIDO' hasta que
    # una cadena la cambia al entrar), se usa el primer texto
    # para que la captura muestre la pantalla con contenido.
    literals = {}

    for scope_name, variable, literal in ENUM_COMPARISON_PATTERN.findall(
        html or ""
    ):

        scope_name = scope_name or "page"

        literals.setdefault(
            (scope_name, variable),
            []
        ).append(literal)

    overrides = {}

    for (scope_name, variable), values in literals.items():

        definition = (
            scopes.get(scope_name, {})
            .get("variables", {})
            .get(variable)
        )

        if not isinstance(definition, dict):
            continue

        if definition.get("type") not in ("string", None):
            continue

        default = definition.get("defaultValue")

        if isinstance(default, str) and default in values:
            continue

        overrides.setdefault(scope_name, {})[variable] = values[0]

    return overrides


def build_vb_state(
    page_html_path,
    application_folder,
    page_html=""
):

    page_json_path, page_js_path = _page_files(page_html_path)

    flow_json_path, flow_js_path = _flow_files(
        page_html_path,
        application_folder
    )

    app_json = _read_json(
        os.path.join(application_folder, "app.json")
    )

    scopes = {
        "application": _scope(app_json),
        "flow": _scope(_read_json(flow_json_path)),
        "page": _scope(_read_json(page_json_path))
    }

    return {
        "scopes": scopes,
        "overrides": _enum_overrides(page_html, scopes),
        "modules": {
            "application": _read_text(
                os.path.join(application_folder, "app.js")
            ),
            "flow": _read_text(flow_js_path),
            "page": _read_text(page_js_path)
        }
    }


# =========================================================
# HTML
# =========================================================

def _script_json(data):

    # JSON seguro dentro de <script>: sin "</script>" ni "<!--"
    return (
        json.dumps(data, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace(" ", "\\u2028")
        .replace(" ", "\\u2029")
    )


JET_RUNTIME_JS = r"""
(function () {

  var STATE = window.__VB_STATE;

  window.__VB_READY = false;
  window.__VB_OK = false;
  window.__VB_ERRORS = [];

  function log(message) {
    window.__VB_ERRORS.push(String(message));
  }

  function finish(ok) {
    var root = document.getElementById("vb-root");
    if (root) { root.style.visibility = "visible"; }
    window.__VB_OK = ok;
    window.__VB_READY = true;
  }

  // ------------------------------------------------------
  // Módulos JET de las etiquetas usadas en la página
  // ------------------------------------------------------

  var SPECIAL = {
    "oj-input-password": "ojs/ojinputtext",
    "oj-text-area": "ojs/ojinputtext",
    "oj-input-date": "ojs/ojdatetimepicker",
    "oj-input-date-time": "ojs/ojdatetimepicker",
    "oj-input-time": "ojs/ojdatetimepicker",
    "oj-date-picker": "ojs/ojdatetimepicker",
    "oj-combobox-one": "ojs/ojselectcombobox",
    "oj-combobox-many": "ojs/ojselectcombobox",
    "oj-select-one": "ojs/ojselectcombobox",
    "oj-select-many": "ojs/ojselectcombobox",
    "oj-buttonset-one": "ojs/ojbutton",
    "oj-buttonset-many": "ojs/ojbutton",
    "oj-menu-button": "ojs/ojbutton",
    "oj-progress-bar": "ojs/ojprogress-bar",
    "oj-progress-circle": "ojs/ojprogress-circle",
    "oj-module": "ojs/ojmodule-element",
    "oj-option": "ojs/ojoption",
    "oj-input-search": "ojs/ojinputsearch"
  };

  var BINDING_TAGS = {
    "oj-bind-if": 1, "oj-bind-for-each": 1, "oj-bind-text": 1,
    "oj-bind-slot": 1, "oj-bind-template-slot": 1, "oj-bind-dom": 1
  };

  function modulesFor(root) {
    var tags = {};
    var all = root.querySelectorAll("*");
    for (var i = 0; i < all.length; i++) {
      tags[all[i].localName] = 1;
    }
    // Las plantillas (<template>) no aparecen en querySelectorAll
    var templates = root.querySelectorAll("template");
    for (var t = 0; t < templates.length; t++) {
      var inner = templates[t].content.querySelectorAll("*");
      for (var j = 0; j < inner.length; j++) {
        tags[inner[j].localName] = 1;
      }
    }
    var modules = {};
    Object.keys(tags).forEach(function (tag) {
      if (tag.indexOf("oj-") !== 0 || BINDING_TAGS[tag]) { return; }
      if (tag.indexOf("oj-c-") === 0) {
        modules["oj-c/" + tag.substring(5)] = 1;
      } else if (SPECIAL[tag]) {
        modules[SPECIAL[tag]] = 1;
      } else {
        modules["ojs/oj" + tag.substring(3).replace(/-/g, "")] = 1;
      }
    });
    if (tags["oj-menu-button"]) { modules["ojs/ojmenu"] = 1; }
    return Object.keys(modules);
  }

  function load(name) {
    return new Promise(function (resolve) {
      var guard = setTimeout(function () {
        log("módulo sin respuesta: " + name);
        resolve(null);
      }, 20000);
      require([name], function (m) { clearTimeout(guard); resolve(m); }, function (error) {
        clearTimeout(guard);
        log("módulo no cargado: " + name);
        if (error && error.requireModules) {
          error.requireModules.forEach(function (id) { requirejs.undef(id); });
        }
        resolve(null);
      });
    });
  }

  // ------------------------------------------------------
  // Variables de Visual Builder
  // ------------------------------------------------------

  var PRIMITIVES = {
    "string": null, "number": null, "boolean": null,
    "any": null, "date": null, "datetime": null, "time": null
  };

  function allTypes() {
    var types = {};
    ["application", "flow", "page"].forEach(function (scope) {
      var defined = (STATE.scopes[scope] || {}).types || {};
      Object.keys(defined).forEach(function (name) {
        types[name] = defined[name];
      });
    });
    return types;
  }

  var TYPES = allTypes();

  function shape(type, depth) {
    if (depth > 6 || type === undefined || type === null) { return null; }
    if (Array.isArray(type)) { return []; }
    if (typeof type === "object") {
      if (type["@decorators"] || type.endpoint) { return null; }
      var result = {};
      Object.keys(type).forEach(function (key) {
        result[key] = shape(type[key], depth + 1);
      });
      return result;
    }
    if (typeof type !== "string") { return null; }
    if (/\[\]$/.test(type)) { return []; }
    if (type === "object") { return {}; }
    if (Object.prototype.hasOwnProperty.call(PRIMITIVES, type)) { return null; }
    if (TYPES[type]) { return shape(TYPES[type], depth + 1); }
    return null;
  }

  var EXPRESSION = /^\s*(\[\[|\{\{)([\s\S]*)(\]\]|\}\})\s*$/;

  function evaluate(text, context) {
    try {
      var names = Object.keys(context);
      var values = names.map(function (n) { return context[n]; });
      return Function.apply(null, names.concat(["return (" + text + ");"]))
        .apply(null, values);
    } catch (error) {
      return undefined;
    }
  }

  function resolveValue(value, context, depth) {
    depth = depth || 0;
    if (depth > 8) { return value; }
    if (typeof value === "string") {
      var match = value.match(EXPRESSION);
      if (match) {
        var result = evaluate(match[2], context);
        return result === undefined ? null : result;
      }
      return value;
    }
    if (Array.isArray(value)) {
      return value.map(function (item) { return resolveValue(item, context, depth + 1); });
    }
    if (value && typeof value === "object") {
      var out = {};
      Object.keys(value).forEach(function (key) {
        out[key] = resolveValue(value[key], context, depth + 1);
      });
      return out;
    }
    return value;
  }

  function isProvider(type) {
    return typeof type === "string" && type.indexOf("vb/") === 0;
  }

  function makeProvider(definition, context, ArrayDataProvider) {
    var type = definition.type;
    var settings = definition.defaultValue || {};
    var keys = settings.keyAttributes || settings.idAttribute || "@index";
    var data = [];
    if (/ArrayDataProvider/.test(type)) {
      data = resolveValue(settings.data, context);
      if (!Array.isArray(data)) { data = []; }
    }
    // ServiceDataProvider, BusinessObjectProvider, etc.: sin
    // backend, se muestran vacíos ("No data to display").
    return new ArrayDataProvider(data, { keyAttributes: keys });
  }

  function buildScope(name, context, ArrayDataProvider, variables) {
    var scope = STATE.scopes[name] || {};
    var definitions = scope.variables || {};
    var overrides = (STATE.overrides || {})[name] || {};
    var providers = [];

    Object.keys(definitions).forEach(function (key) {
      var definition = definitions[key] || {};
      if (isProvider(definition.type)) { providers.push(key); return; }
      var value;
      if (Object.prototype.hasOwnProperty.call(overrides, key)) {
        value = overrides[key];
      } else if (definition.defaultValue !== undefined && definition.defaultValue !== null) {
        value = definition.defaultValue;
      } else {
        value = shape(definition.type, 0);
      }
      variables[key] = value;
    });

    // Segunda pasada: expresiones que leen otras variables
    Object.keys(variables).forEach(function (key) {
      var resolved = resolveValue(variables[key], context);
      if ((resolved === null || resolved === undefined)
          && !(definitions[key] && PRIMITIVES.hasOwnProperty(definitions[key].type))) {
        resolved = shape(definitions[key].type, 0);
      }
      variables[key] = resolved;
    });

    providers.forEach(function (key) {
      try {
        variables[key] = makeProvider(definitions[key], context, ArrayDataProvider);
      } catch (error) {
        log("proveedor " + key + ": " + error);
        variables[key] = new ArrayDataProvider([], { keyAttributes: "@index" });
      }
    });

    return variables;
  }

  // ------------------------------------------------------
  // Módulos JS (PageModule, FlowModule, AppModule)
  // ------------------------------------------------------

  function noop() { return undefined; }

  var NOT_FUNCTIONS = {
    then: 1, toJSON: 1, constructor: 1, prototype: 1,
    __proto__: 1, nodeType: 1, length: 1
  };

  function lenient(target) {
    return new Proxy(target || {}, {
      get: function (object, property) {
        if (property in object) {
          var value = object[property];
          return typeof value === "function" ? value.bind(object) : value;
        }
        // "then": si no, una promesa que resuelve este objeto
        // lo trataría como promesa y nunca terminaría.
        if (typeof property === "symbol" || NOT_FUNCTIONS[property]) {
          return undefined;
        }
        return noop;
      }
    });
  }

  function loadModule(source) {
    return new Promise(function (resolve) {
      if (!source) { resolve(lenient({})); return; }
      try {
        var captured = null;
        var shim = function (deps, factory) {
          if (typeof deps === "function") { factory = deps; deps = []; }
          captured = { deps: deps || [], factory: factory };
        };
        shim.amd = true;
        Function("define", source)(shim);
        if (!captured) { resolve(lenient({})); return; }
        Promise.all(captured.deps.map(function (dep) {
          if (/^vb\//.test(dep)) { return Promise.resolve({}); }
          return load(dep);
        })).then(function (deps) {
          try {
            var result = captured.factory.apply(null, deps);
            if (typeof result === "function") {
              try { result = new result({}); } catch (e) { result = {}; }
            }
            resolve(lenient(result || {}));
          } catch (error) {
            log("módulo JS: " + error);
            resolve(lenient({}));
          }
        });
      } catch (error) {
        log("módulo JS: " + error);
        resolve(lenient({}));
      }
    });
  }

  // ------------------------------------------------------
  // Arranque
  // ------------------------------------------------------

  var timeout = setTimeout(function () {
    log("tiempo de espera agotado");
    finish(false);
  }, 40000);

  require(
    ["knockout", "ojs/ojcontext", "ojs/ojarraydataprovider", "ojs/ojknockout"],
    function (ko, Context, ArrayDataProvider) {

      // La página se parsea aparte (como hace Visual Builder):
      // un </div> sobrante en la página no cierra #vb-root.
      var root = document.getElementById("vb-root");
      var pageTemplate = document.getElementById("vb-page");
      root.appendChild(document.importNode(pageTemplate.content, true));

      Promise.all(modulesFor(root).map(load).concat([
        loadModule(STATE.modules.application),
        loadModule(STATE.modules.flow),
        loadModule(STATE.modules.page)
      ])).then(function (results) {

        var count = results.length;
        var appFunctions = results[count - 3];
        var flowFunctions = results[count - 2];
        var pageFunctions = results[count - 1];

        var user = {
          userName: "usuario", fullName: "Usuario", firstName: "Usuario",
          lastName: "", email: "usuario@empresa.com", isAuthenticated: true,
          roles: [], permissions: [], languageCode: "es"
        };

        var application = {
          variables: {}, constants: {}, functions: appFunctions,
          path: "", user: user, translations: {}, responsive: {},
          builtinUtils: {}, currentPage: {}
        };
        var flow = { variables: {}, constants: {}, functions: flowFunctions };
        var page = { variables: {}, constants: {}, functions: pageFunctions };

        var base = {
          $application: application, $flow: flow, $page: page,
          $variables: page.variables, $constants: page.constants,
          $functions: pageFunctions, $listeners: lenient({}),
          $base: application, $extension: application, $global: application
        };

        // Cada ámbito se llena sobre su propio objeto, así las
        // expresiones ($variables.x, $application.variables.y)
        // ven las variables ya creadas.
        buildScope("application", base, ArrayDataProvider, application.variables);
        buildScope("flow", base, ArrayDataProvider, flow.variables);
        buildScope("page", base, ArrayDataProvider, page.variables);

        ["application", "flow", "page"].forEach(function (scope) {
          var constants = (STATE.scopes[scope] || {}).constants || {};
          var target = { application: application, flow: flow, page: page }[scope].constants;
          Object.keys(constants).forEach(function (key) {
            target[key] = (constants[key] || {}).defaultValue;
          });
        });

        var viewModel = {
          $application: application,
          $flow: flow,
          $page: page,
          $variables: page.variables,
          $constants: page.constants,
          $functions: pageFunctions,
          $listeners: lenient({}),
          $translations: {},
          $base: application,
          $extension: application,
          $global: application,
          $i18n: {}
        };

        try {
          ko.applyBindings(viewModel, root);
        } catch (error) {
          log("applyBindings: " + error);
        }

        Context.getPageContext().getBusyContext().whenReady(25000)
          .catch(function (error) { log("busy: " + error); })
          .then(function () {
            setTimeout(function () {
              clearTimeout(timeout);
              finish(true);
            }, 600);
          });
      });
    },
    function (error) {
      log("JET no cargó: " + error);
      clearTimeout(timeout);
      finish(false);
    }
  );
})();
"""


PAGE_CSS = """
html, body {
    margin: 0;
    padding: 0;
    background: #f9f8f6;
}

#vb-root {
    visibility: hidden;
    max-width: 1200px;
    margin: 0 auto;
    padding: 16px 24px 32px 24px;
    box-sizing: border-box;
}
"""


def build_jet_html(
    page_html,
    app_css="",
    state=None,
    header_html="",
    footer_html=""
):

    state = state or {
        "scopes": {},
        "overrides": {},
        "modules": {}
    }

    body = f"{header_html or ''}{page_html or ''}{footer_html or ''}"

    return f"""<!DOCTYPE html>
<html lang="es" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{JET_CDN}/default/css/redwood/oj-redwood-min.css">
<link rel="stylesheet" href="{JET_CDN}/3rdparty/oraclejet-preact/amd/Theme-redwood/theme.css">
<link rel="stylesheet" href="{ICON_FONT_CSS}">
<style>{PAGE_CSS}</style>
<style>{app_css or ''}</style>
</head>
<body class="oj-web-applayout-body">
<div id="vb-root"></div>
<template id="vb-page">
{body}
</template>
<script>window.__VB_STATE = {_script_json(state)};</script>
<script src="{JET_CDN}/3rdparty/require/require.js"></script>
<script src="{JET_CDN}/default/js/bundles-config.js"></script>
<script>{JET_RUNTIME_JS}</script>
</body>
</html>
"""


# =========================================================
# ENTRY POINT
# =========================================================

def jet_rendering_enabled():

    return RENDER_MODE != "legacy"


def _split_shell(shell_html):

    # Shell del VB de OIC: cabecera arriba de la página y el
    # <footer> abajo. Las App UI de VB Studio no tienen shell.
    if not shell_html:
        return ("", "")

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(shell_html, "html.parser")

    footer = soup.find("footer")

    footer_html = ""

    if footer:
        footer_html = str(footer)
        footer.extract()

    # El contenedor donde VB inyecta la página queda vacío.
    for tag in soup.find_all(["oj-module", "oj-vb-content"]):
        tag.decompose()

    return (str(soup), footer_html)


def build_vb_jet_html(page, vb_metadata):

    application_folder = (vb_metadata or {}).get("application_folder")

    page_path = (page or {}).get("path")

    page_html = (page or {}).get("html", "")

    if not application_folder or not page_path:
        return None

    state = build_vb_state(
        page_path,
        application_folder,
        page_html
    )

    header_html, footer_html = _split_shell(
        vb_metadata.get("shell_html", "")
    )

    return build_jet_html(
        page_html=page_html,
        app_css=vb_metadata.get("app_css", ""),
        state=state,
        header_html=header_html,
        footer_html=footer_html
    )
