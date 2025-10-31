app_name = "hms"
app_title = "HMS"
app_publisher = "nani-samireddy"
app_description = "hospital Management System"
app_email = "nanisamireddy05@gmail.com"
app_license = "mit"

# App visuals and home
app_icon = "octicon octicon-hubot"
app_color = "blue"
app_home = "/app/hms"

add_to_apps_screen = [
	{
		"name": "hms",
		"logo": "/assets/hms/images/hms.svg",
		"title": "HMS",
		"route": "/app/hms",
	}
]
# required_apps = []


# Boot
# ----
# extend_bootinfo = "hms.boot.boot_session"

extend_bootinfo = "hms.boot.boot_session"

# Website redirects
website_route_rules = [
	{
		"from_route": "/hms/<path:app_path>",
		"to_route": "hms",
	},
]

global_search_doctypes = {
	"HMS": [
		{"doctype": "Patient", "index": 1},
		{"doctype": "Patient Visit", "index": 2},
		{"doctype": "IP Record", "index": 3},
		{"doctype": "Discharge Summary", "index": 4},
		{"doctype": "Lab Report", "index": 5},
		{"doctype": "Healthcare Practitioner", "index": 6},
		{"doctype": "Patient Appointment", "index": 7},
		{"doctype": "Fee Validity", "index": 8},
		{"doctype": "Ward", "index": 9},
		{"doctype": "Bed", "index": 10},
		{"doctype": "Medicine", "index": 11}
	]
}


# Fixtures
# ----------
fixtures = [
	{
		"doctype": "Custom HTML Block",
		"filters": [["name", "in", ("HMS Dashboard Profile")]]
	},
	{
		"doctype": "Role",
		"filters": [["name", "in", ("Receptionist", "Pharmacist", "Doctor")]]
	}
]
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hms/css/hms.css"
# app_include_js = "/assets/hms/js/hms.js"

# include js, css files in header of web template
# web_include_css = "/assets/hms/css/hms.css"
# web_include_js = "/assets/hms/js/hms.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hms/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "hms/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
role_home_page = {
	"Receptionist": "/app/reception-dashboard",
	"Doctor": "/app/doctor-dashboard",
	"Pharmacist": "/app/pharmacist-dashboard",
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "hms.utils.jinja_methods",
# 	"filters": "hms.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hms.install.before_install"
# after_install = "hms.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hms.uninstall.before_uninstall"
# after_uninstall = "hms.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hms.utils.before_app_install"
# after_app_install = "hms.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hms.utils.before_app_uninstall"
# after_app_uninstall = "hms.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hms.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

"""
Document Events
---------------
Hook on document methods and events
"""

doc_events = {
	"Patient Visit": {
		"after_insert": "hms.hms.doctype.fee_validity.fee_validity.manage_fee_validity_on_visit",
	}
}

# Scheduled Tasks
# ---------------


scheduler_events = {
	# "all": [
	# 	"hms.tasks.all"
	# ],
	"daily": [
		"hms.tasks.daily",
		"hms.hms.doctype.fee_validity.fee_validity.update_validity_status",
	],
	# "hourly": [
	# 	"hms.tasks.hourly"
	# ],
	# "weekly": [
	# 	"hms.tasks.weekly"
	# ],
	# "monthly": [
	# 	"hms.tasks.monthly"
	# ],
}

# Testing
# -------

# before_tests = "hms.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hms.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hms.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hms.utils.before_request"]
# after_request = ["hms.utils.after_request"]

# Job Events
# ----------
# before_job = ["hms.utils.before_job"]
# after_job = ["hms.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"hms.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
