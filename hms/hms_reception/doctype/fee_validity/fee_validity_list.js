frappe.listview_settings["Fee Validity"] = {
  get_indicator(doc) {
    if (doc.status === "Active") {
      return [__("Active"), "green", "status,=,Active"];
    }
    if (doc.status === "Completed") {
      return [__("Completed"), "blue", "status,=,Completed"];
    }
    if (doc.status === "Expired") {
      return [__("Expired"), "red", "status,=,Expired"];
    }
    if (doc.status === "Cancelled") {
      return [__("Cancelled"), "gray", "status,=,Cancelled"];
    }
  },
};

