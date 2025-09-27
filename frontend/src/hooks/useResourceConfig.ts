import { useMemo } from "react"

declare global {
  interface Window {
    frappe: {
      boot: {
        hms_doctypes: Record<string, any>
        doctypes: Record<string, any>
        user_permissions: Record<string, any>
        permissions: Record<string, any>
        // Add other boot properties as needed
      }
    }
  }
}

export interface ResourceField {
  fieldname: string
  fieldtype: string
  label: string
  options?: string
  reqd: boolean
  in_list_view: boolean
  read_only: boolean
  hidden: boolean
  default?: string | null
}

export interface ResourceConfig {
  fields: ResourceField[]
  list_view_fields: string[]
  title_field: string
  search_fields: string
  sort_field: string
  sort_order: string
}

export interface ResourcePermissions {
  read: boolean
  create: boolean
  write: boolean
  delete: boolean
}

export function useResourceConfig(doctype: string) {
  return useMemo(() => {
    // Get boot data from window.frappe.boot
    const bootData = window.frappe?.boot
    
    // Debug: Log available doctypes
    console.log('Available doctypes in boot:', Object.keys(bootData?.hms_doctypes || {}))
    console.log('Requested doctype:', doctype, 'Config:', bootData?.hms_doctypes?.[doctype])

    if (!bootData) {
      return {
        config: null,
        permissions: null,
        listViewFields: [],
        searchField: 'name',
        hasAccess: false,
        isLoading: false,
        error: 'Boot data not available'
      }
    }

    const doctypeConfig = bootData.hms_doctypes?.[doctype]

    // Check if doctype exists in HMS doctypes
    if (!doctypeConfig) {
      return {
        config: null,
        permissions: { read: false, create: false, write: false, delete: false },
        listViewFields: [],
        searchField: 'name',
        hasAccess: false,
        isLoading: false,
        error: `Doctype "${doctype}" not found in HMS doctypes`
      }
    }

    // Check user permissions - look for doctype permissions in boot data
    // If no specific permissions found, assume access if doctype exists in hms_doctypes
    const userPermissions = bootData.user_permissions?.[doctype] || bootData.permissions?.[doctype]
    
    let permissions = {
      read: true,
      create: true,
      write: true,
      delete: true
    }

    // If specific permissions exist, use them
    if (userPermissions) {
      permissions = {
        read: userPermissions.read !== false,
        create: userPermissions.create !== false,
        write: userPermissions.write !== false,
        delete: userPermissions.delete !== false
      }
    }

    // User has access if they have at least read permission
    const hasAccess = permissions.read

    return {
      config: doctypeConfig,
      permissions,
      listViewFields: doctypeConfig.list_view_fields || [],
      searchField: doctypeConfig.search_fields || 'name',
      hasAccess,
      isLoading: false,
      error: null
    }
  }, [doctype])
}

export function useAvailableResources() {
  return useMemo(() => {
    // Get boot data from window.frappe.boot
    const bootData = window.frappe?.boot

    if (!bootData) {
      return {
        resources: [],
        isLoading: false,
        error: 'Boot data not available'
      }
    }

    // Get all available HMS doctypes from boot data
    const availableResources = Object.keys(bootData.hms_doctypes || {})

    return {
      resources: availableResources,
      isLoading: false,
      error: null
    }
  }, [])
}
