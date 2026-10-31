### HMS

hospital Management System

HMS uses standard Frappe Desk for its forms and dashboards. Open `/desk/patient`
to start; legacy `/hms` URLs redirect there. The custom React frontend has been
removed, so HMS has no separate frontend dependency install or build step.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app hms
```

### Standalone workflows and documentation

Pharmacy stock, invoices, payment allocation and refunds run within HMS on Frappe;
ERPNext is not required. See [workflow rules and regression checks](docs/WORKFLOWS.md)
and the [staff user guide](docs/user-guide/README.md). The guide includes 22 chapters,
a [quick reference](docs/USER-GUIDE-QUICK-REFERENCE.md), a Hospital Live screenshot,
and a printable edition. Workflow screenshots and cursor/click GIF recordings remain
on the capture checklist. See the
[media checklist](docs/USER-GUIDE-MEDIA-STATUS.md) for pending captures and the
[maintenance notes](docs/USER-GUIDE-MAINTENANCE.md) for offline export.

### Functional modules

HMS ships six modules with separate sidebars and dock icons: HMS Core, Reception,
Clinical, Inpatient, Pharmacy and Billing. The original `HMS` module remains the
shared core so existing guide URLs and bookmarks remain available. See the
[module ownership and migration notes](docs/MODULES.md).

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/hms
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
