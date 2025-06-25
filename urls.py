"""URL configuration for San Mateo County Housing website."""

# Base URLs
BASE_URL = "https://www.smcgov.org"
HOUSING_BASE = f"{BASE_URL}/housing"

# Main sections
URLS = {
    "housing_home": HOUSING_BASE,
    "dashboards": f"{HOUSING_BASE}/doh-dashboards",
    "income_limits": f"{HOUSING_BASE}/income-limits-and-rent-payments",
    "public_notices": f"{HOUSING_BASE}/doh-public-notices",
    "apply_programs": f"{HOUSING_BASE}/apply-housing-programs",
    "current_participants": f"{HOUSING_BASE}/current-program-participants",
    "landlords": f"{HOUSING_BASE}/landlords-and-property-owners",
    "partners": f"{HOUSING_BASE}/partners",
    "policy_planning": f"{HOUSING_BASE}/policy-planning-resources",
    "nofas": f"{HOUSING_BASE}/nofas-bids-proposals",
    "about": f"{HOUSING_BASE}/about-doh",
    "tenant_rights": f"{HOUSING_BASE}/tenants-protections-and-rights",
    "hcdc": f"{HOUSING_BASE}/housing-community-development-committee-hcdc",
    "voucher_briefings": f"{HOUSING_BASE}/housing-authority-voucher-program-briefings"
}

# Income limits PDF patterns
INCOME_LIMITS_PDFS = {
    "2025": f"{HOUSING_BASE}/sites/smcgov.org/files/2025%20Income%20%26%20Rent%20Limits.pdf",
    "2024": f"{HOUSING_BASE}/sites/smcgov.org/files/2024%20Income%20%26%20Rent%20Limits.pdf",
    "2023": f"{HOUSING_BASE}/sites/smcgov.org/files/2023%20Income%20%26%20Rent%20Limits.pdf"
}

# Dashboard selectors (for web scraping)
DASHBOARD_SELECTORS = {
    "total_units": "[data-testid='total-affordable-units']",
    "total_projects": "[data-testid='total-projects']",
    "county_funding": "[data-testid='county-funding']",
    "federal_funding": "[data-testid='federal-funding']",
    "units_status_chart": "[data-testid='units-status-chart']",
    "units_by_city_chart": "[data-testid='units-by-city-chart']"
}

# Common CSS selectors
SELECTORS = {
    "notice_links": "a[href*='notice']",
    "pdf_links": "a[href$='.pdf']",
    "content_main": ".main-content",
    "page_title": "h1",
    "breadcrumb": ".breadcrumb"
}

