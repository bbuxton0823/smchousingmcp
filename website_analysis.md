# San Mateo County Housing Website Analysis

## Website URL
https://www.smcgov.org/housing

## Main Navigation Sections
1. **Apply to Housing Programs** - Applications for various housing assistance programs
2. **Current Program Participants** - Resources for existing participants
3. **Landlords and Property Owners** - Information for property owners
4. **Partners** - Partner organizations and resources
5. **Policy & Planning Resources** - Policy documents and planning information
6. **NOFA's, Bids & Proposals** - Notice of Funding Availability and procurement
7. **About DOH** - Department information

## Key Features Identified

### "How Do I..." Section
- Apply for other Affordable Housing
- Report a Change to your Rental Assistance Application
- Apply for Section 8/MTW/HCV Rental Assistance on Rent Cafe

### "Check these out..." Section
- Public Notices
- Housing & Community Development Committee (HCDC)
- Tenants Protections and Rights
- Income Limits and Rent Payments
- DOH Dashboards
- Housing Authority Voucher Program Briefings

## Data Sources to Explore
1. Housing program applications and eligibility
2. Public notices and announcements
3. Income limits and rent payment schedules
4. Dashboard data and statistics
5. Committee meeting information
6. Tenant rights and protections information
7. NOFA and procurement opportunities

## Next Steps
- Explore each major section to understand data structure
- Identify dynamic content vs static pages
- Determine what data would be most valuable for MCP server
- Analyze forms and application processes



## Detailed Analysis Results

### Dashboard Data (https://www.smcgov.org/housing/doh-dashboards)
**Affordable Housing Dashboard:**
- Total Affordable Units: 4,939
- Total Number of Affordable Projects: 68
- Housing Units Status: Complete (2,875), Predevelopment (1,202), Construction (862)
- Area Median Income (AMI) Targeting data
- Existing and Planned Housing Units by City (bar chart data)
- Interactive map with housing unit locations

**Affordable Housing Funding Sources Dashboard:**
- Total Amount of County Funding: $305.3M
- Total Amount of Federal Funding: $52.6M
- Measure K leveraging: $16.6 of Private, Local, State and Federal Resources
- Affordable Housing Development Project Funding Sources
- County Affordable Housing Project Funding Sources

### Income Limits Data (https://www.smcgov.org/housing/income-limits-and-rent-payments)
- Annual income limits by family size and AMI percentage
- Maximum affordable rent payments
- Available for years 2025, 2024, 2023
- Historical data available back to 2002
- Downloadable PDF documents with structured data

### Public Notices (https://www.smcgov.org/housing/doh-public-notices)
**Types of Notices:**
- Annual Action Plan amendments and hearings
- Public meetings for CDBG, HOME, PLHA, and ESG NOFAs
- Environmental reviews for housing projects
- Notice of Funding Availability (NOFA) needs assessments
- Intent to Request Release of Funds (NOI/RROF)
- Tenant improvement notices
- Consolidation Plan amendments

### Data Sources Suitable for MCP Server
1. **Dashboard APIs/Data** - Housing statistics, funding data, project status
2. **Income Limits** - Structured PDF data that can be parsed
3. **Public Notices** - Regular announcements and updates
4. **Housing Programs** - Application information and eligibility
5. **Committee Information** - Meeting schedules and agendas
6. **Tenant Rights** - Protection and rights information
7. **NOFA/Procurement** - Funding opportunities and bids

### Technical Observations
- Website uses Esri for dashboard visualizations
- Data appears to be updated regularly
- Multiple PDF documents with structured data
- Some content may require web scraping
- Interactive elements suggest underlying APIs or data sources

