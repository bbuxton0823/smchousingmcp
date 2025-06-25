# San Mateo County Housing MCP Server - Deployment Guide

**Author:** Manus AI  
**Version:** 1.0.0  
**Date:** June 25, 2025

## Executive Summary

The San Mateo County Housing Model Context Protocol (MCP) Server represents a comprehensive solution for accessing housing data from the San Mateo County Department of Housing website through a standardized MCP interface. This deployment guide provides detailed instructions for installing, configuring, and integrating the MCP server into applications that require access to housing statistics, income limits, public notices, and eligibility checking capabilities.

The server addresses the challenge of accessing structured housing data from a government website that lacks a public API by implementing web scraping techniques combined with intelligent caching and data processing. Through the MCP protocol, applications can seamlessly integrate with this data source using a standardized interface that abstracts away the complexities of web scraping and data extraction.

This guide covers all aspects of deployment, from initial system requirements through production deployment considerations, ensuring that developers and system administrators have the information needed to successfully implement and maintain the MCP server in their environments.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Process](#installation-process)
3. [Configuration Management](#configuration-management)
4. [MCP Integration](#mcp-integration)
5. [Production Deployment](#production-deployment)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Security Considerations](#security-considerations)




## System Requirements

The San Mateo County Housing MCP Server has been designed to operate efficiently across various computing environments, from development workstations to production servers. Understanding the system requirements is crucial for ensuring optimal performance and reliability of the service.

### Hardware Requirements

The server's hardware requirements vary significantly based on the expected usage patterns and deployment scale. For development and testing environments, minimal hardware specifications are sufficient, while production deployments may require more robust infrastructure to handle concurrent requests and maintain responsive performance.

**Minimum Requirements:**
- CPU: 1 core, 2.0 GHz processor
- Memory: 2 GB RAM
- Storage: 1 GB available disk space
- Network: Stable internet connection with at least 10 Mbps bandwidth

**Recommended Requirements:**
- CPU: 2+ cores, 2.5 GHz processor
- Memory: 4 GB RAM or higher
- Storage: 5 GB available disk space (for caching and temporary files)
- Network: High-speed internet connection with 50+ Mbps bandwidth

The memory requirements are particularly important when the server processes large PDF documents or handles multiple concurrent requests. The storage requirements include space for temporary PDF downloads, cache files, and log storage. Network bandwidth is critical since the server performs web scraping operations that require reliable connectivity to the San Mateo County website.

### Software Dependencies

The MCP server relies on several software components that must be properly installed and configured before deployment. These dependencies fall into three categories: core runtime requirements, web scraping dependencies, and optional performance enhancements.

**Core Runtime Requirements:**

Python 3.11 or higher serves as the primary runtime environment for the MCP server. The server leverages modern Python features and type annotations that require this minimum version. The Python installation should include pip for package management and virtual environment support for isolated deployments.

Essential Python packages include:
- `requests` (2.32.0+) for HTTP client functionality
- `beautifulsoup4` (4.13.0+) for HTML parsing
- `pydantic` (2.11.0+) for data validation and serialization
- `structlog` (25.0.0+) for structured logging
- `asyncio` (built-in) for asynchronous operations

**Web Scraping Dependencies:**

For enhanced web scraping capabilities, particularly when dealing with dynamic content that requires JavaScript execution, the server can optionally utilize Selenium WebDriver. While the server includes fallback mechanisms that work without Selenium, installing these components enables access to more comprehensive data extraction.

Chrome or Chromium browser installation is required for Selenium operations:
- Google Chrome (latest stable version)
- ChromeDriver (matching Chrome version)
- Selenium Python package (4.0.0+)

**PDF Processing Dependencies:**

The server processes PDF documents containing income limits data. For production deployments, installing PDF processing libraries enables more accurate data extraction:
- `pdfplumber` (0.10.0+) for PDF text and table extraction
- `PyPDF2` or `pypdf` (3.0.0+) as alternative PDF processors

**Optional Performance Enhancements:**

Redis can be configured as a high-performance caching backend to improve response times and reduce load on the source website:
- Redis server (6.0+)
- `redis-py` Python client (4.0.0+)

### Operating System Compatibility

The MCP server has been developed and tested across multiple operating systems to ensure broad compatibility. The primary development and testing environment utilizes Ubuntu 22.04 LTS, but the server operates effectively on various Linux distributions, macOS, and Windows systems.

**Linux Systems:**
Ubuntu 22.04 LTS represents the primary supported platform, with extensive testing ensuring reliable operation. Other Debian-based distributions including Ubuntu 20.04, Debian 11, and Linux Mint are fully compatible. Red Hat Enterprise Linux, CentOS, and Fedora systems require minor package management adjustments but operate without functional limitations.

**macOS Systems:**
macOS 12 (Monterey) and later versions provide full compatibility with the MCP server. The Homebrew package manager simplifies dependency installation, and the server operates efficiently on both Intel and Apple Silicon processors.

**Windows Systems:**
Windows 10 and Windows 11 support the MCP server through Windows Subsystem for Linux (WSL) or native Python installations. WSL2 provides the most seamless experience, closely matching Linux deployment characteristics.

### Network and Security Requirements

The MCP server requires outbound internet connectivity to access the San Mateo County housing website and download PDF documents. Understanding the network requirements and implementing appropriate security measures ensures reliable operation while maintaining system security.

**Network Connectivity:**
The server initiates HTTPS connections to `smcgov.org` on port 443 for web scraping operations. PDF downloads may require sustained connections for several minutes depending on document size. The server respects rate limiting and implements delays between requests to avoid overwhelming the source website.

**Firewall Configuration:**
Outbound connections to `smcgov.org` (IP addresses may vary) must be permitted through firewalls. If the server operates behind a corporate firewall, ensure that HTTPS traffic to government websites is allowed. No inbound connections are required for the MCP server itself, as it communicates through stdin/stdout following the MCP protocol.

**Security Considerations:**
The server does not store sensitive personal information but may cache public housing data temporarily. Ensure that cache directories have appropriate file permissions and consider encryption for sensitive deployment environments. Regular security updates for all dependencies maintain protection against known vulnerabilities.



## Installation Process

The installation process for the San Mateo County Housing MCP Server involves several stages, each designed to ensure a robust and reliable deployment. This section provides comprehensive instructions for different installation scenarios, from development environments to production deployments.

### Development Environment Setup

Setting up a development environment enables testing, customization, and integration development without affecting production systems. The development setup prioritizes ease of installation and debugging capabilities over performance optimization.

**Step 1: Environment Preparation**

Begin by creating an isolated Python environment to prevent dependency conflicts with other projects. Virtual environments provide clean separation and simplify dependency management throughout the development lifecycle.

```bash
# Create project directory
mkdir smcgov-housing-mcp-dev
cd smcgov-housing-mcp-dev

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip to latest version
pip install --upgrade pip
```

The virtual environment isolation ensures that the MCP server dependencies do not interfere with other Python projects on the development system. This approach also simplifies testing different dependency versions and rolling back changes when necessary.

**Step 2: Source Code Installation**

Download or clone the MCP server source code into the prepared environment. The server includes all necessary configuration files, documentation, and example scripts for immediate testing.

```bash
# If downloading from a repository
git clone <repository-url> .

# Or if extracting from an archive
tar -xzf smcgov-housing-mcp.tar.gz
mv smcgov-housing-mcp/* .
```

Verify that all essential files are present, including the main server script, configuration files, and documentation. The directory structure should match the architecture described in the README file.

**Step 3: Dependency Installation**

Install the required Python packages using the provided requirements file. The installation process automatically resolves dependencies and ensures compatibility between packages.

```bash
# Install core dependencies
pip install -r requirements.txt

# Verify installation
python -c "import requests, beautifulsoup4, pydantic, structlog; print('Core dependencies installed successfully')"
```

For development environments, consider installing additional debugging and testing tools that facilitate development workflows:

```bash
# Optional development dependencies
pip install pytest pytest-asyncio black flake8 mypy
```

**Step 4: Optional Component Installation**

Install optional components based on the intended development scope. Selenium WebDriver enables testing of dynamic content extraction, while PDF processing libraries allow testing of income limits functionality.

```bash
# Install Selenium for enhanced web scraping
pip install selenium

# Install Chrome/Chromium (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install chromium-browser

# Install PDF processing libraries
pip install pdfplumber PyPDF2
```

**Step 5: Development Testing**

Validate the development installation by running the included test scripts. These tests verify that all components function correctly and identify any configuration issues.

```bash
# Run basic functionality tests
python test_server.py

# Run demonstration script
python demo.py
```

Successful test execution confirms that the development environment is properly configured and ready for customization or integration development.

### Production Environment Setup

Production deployments require additional considerations for security, performance, and reliability. The production setup emphasizes stability, monitoring, and maintainability over development convenience.

**Step 1: System User Creation**

Create a dedicated system user for running the MCP server. This security practice limits the server's system access and simplifies permission management.

```bash
# Create system user (Ubuntu/Debian)
sudo useradd -r -s /bin/false -d /opt/smcgov-housing-mcp smchousing

# Create application directory
sudo mkdir -p /opt/smcgov-housing-mcp
sudo chown smchousing:smchousing /opt/smcgov-housing-mcp
```

The dedicated user account prevents the MCP server from accessing sensitive system resources and provides clear separation from other services.

**Step 2: Application Installation**

Install the MCP server application in the dedicated directory with appropriate permissions and ownership settings.

```bash
# Switch to application directory
cd /opt/smcgov-housing-mcp

# Extract application files (as root or with sudo)
sudo tar -xzf /path/to/smcgov-housing-mcp.tar.gz --strip-components=1
sudo chown -R smchousing:smchousing .

# Create virtual environment as application user
sudo -u smchousing python3.11 -m venv venv
sudo -u smchousing ./venv/bin/pip install --upgrade pip
sudo -u smchousing ./venv/bin/pip install -r requirements.txt
```

**Step 3: Configuration Management**

Create production configuration files with appropriate security settings and performance optimizations. Production configurations should enable caching, implement rate limiting, and configure appropriate logging levels.

```bash
# Create configuration directory
sudo mkdir -p /etc/smcgov-housing-mcp
sudo chown smchousing:smchousing /etc/smcgov-housing-mcp

# Create environment configuration
sudo -u smchousing tee /etc/smcgov-housing-mcp/production.env << EOF
SMC_HOUSING_CACHE_TTL=24
SMC_HOUSING_SELENIUM_HEADLESS=true
SMC_HOUSING_REQUEST_TIMEOUT=30
SMC_HOUSING_REQUEST_DELAY=2.0
SMC_HOUSING_MAX_RETRIES=3
SMC_HOUSING_LOG_LEVEL=INFO
EOF
```

**Step 4: Service Configuration**

Configure the MCP server as a system service for automatic startup and process management. System service integration ensures reliable operation and simplifies maintenance procedures.

```bash
# Create systemd service file
sudo tee /etc/systemd/system/smcgov-housing-mcp.service << EOF
[Unit]
Description=San Mateo County Housing MCP Server
After=network.target

[Service]
Type=simple
User=smchousing
Group=smchousing
WorkingDirectory=/opt/smcgov-housing-mcp
Environment=PATH=/opt/smcgov-housing-mcp/venv/bin
EnvironmentFile=/etc/smcgov-housing-mcp/production.env
ExecStart=/opt/smcgov-housing-mcp/venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable smcgov-housing-mcp
sudo systemctl start smcgov-housing-mcp
```

**Step 5: Production Validation**

Verify that the production installation operates correctly by testing core functionality and monitoring system resources.

```bash
# Check service status
sudo systemctl status smcgov-housing-mcp

# Test MCP functionality
sudo -u smchousing /opt/smcgov-housing-mcp/venv/bin/python demo.py

# Monitor resource usage
top -p $(pgrep -f "python server.py")
```

### Container Deployment

Container deployment provides consistent environments across different infrastructure platforms and simplifies scaling and maintenance operations. Docker containers encapsulate all dependencies and configuration requirements.

**Step 1: Dockerfile Creation**

Create a Dockerfile that defines the container environment with all necessary dependencies and security configurations.

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd -r -s /bin/false smchousing

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN chown -R smchousing:smchousing /app

# Switch to application user
USER smchousing

# Expose MCP communication (stdin/stdout)
CMD ["python", "server.py"]
```

**Step 2: Container Build and Testing**

Build the container image and verify that it operates correctly in the containerized environment.

```bash
# Build container image
docker build -t smcgov-housing-mcp:latest .

# Test container functionality
docker run --rm -i smcgov-housing-mcp:latest < test_input.json
```

**Step 3: Production Container Deployment**

Deploy the container using orchestration platforms such as Docker Compose, Kubernetes, or cloud container services.

```yaml
# docker-compose.yml example
version: '3.8'
services:
  smcgov-housing-mcp:
    image: smcgov-housing-mcp:latest
    restart: unless-stopped
    environment:
      - SMC_HOUSING_CACHE_TTL=24
      - SMC_HOUSING_LOG_LEVEL=INFO
    volumes:
      - ./cache:/app/cache
    stdin_open: true
    tty: true
```

Container deployment provides consistent operation across different environments and simplifies scaling for high-availability deployments.


## Configuration Management

Effective configuration management ensures that the San Mateo County Housing MCP Server operates optimally across different environments while maintaining security and performance standards. The server supports multiple configuration methods, allowing administrators to choose the approach that best fits their deployment architecture and operational requirements.

### Environment Variables

The MCP server utilizes environment variables as the primary configuration mechanism, providing flexibility for different deployment scenarios while maintaining security best practices. Environment variables can be set through system configuration, container orchestration platforms, or configuration files.

**Core Server Configuration:**

The server name and version identification variables control how the MCP server identifies itself to clients and in logging output. These settings are particularly important in environments with multiple MCP servers or when debugging connectivity issues.

`SMC_HOUSING_SERVER_NAME` defines the server identifier used in MCP protocol responses and logging. The default value "smcgov-housing-mcp" provides clear identification, but organizations may prefer custom naming conventions that align with their infrastructure standards.

`SMC_HOUSING_SERVER_VERSION` specifies the version string reported to MCP clients. While the default "1.0.0" matches the initial release, administrators should update this value when deploying customized versions or applying patches.

**Caching Configuration:**

Cache configuration variables significantly impact server performance and resource utilization. Proper cache tuning reduces load on the source website while ensuring that clients receive current information.

`SMC_HOUSING_CACHE_TTL` controls the default cache time-to-live in hours for most data types. The default value of 24 hours balances data freshness with performance, but environments with different requirements may benefit from adjustment. Development environments might use shorter TTL values (1-6 hours) for testing, while production environments serving stable data could extend TTL to 48-72 hours.

`SMC_HOUSING_CACHE_TTL_INCOME_LIMITS` specifically controls caching for income limits data, which changes infrequently. The default 720 hours (30 days) reflects the annual update cycle for income limits, but administrators should verify the actual update frequency for their use case.

`SMC_HOUSING_CACHE_TTL_NOTICES` manages caching for public notices, which require more frequent updates. The default 6 hours ensures that new notices appear promptly while reducing redundant requests.

`SMC_HOUSING_REDIS_URL` enables Redis caching when specified. The URL format follows standard Redis connection strings: `redis://localhost:6379` for local Redis instances or `redis://username:password@hostname:port/database` for authenticated connections. Redis caching significantly improves performance in high-traffic environments.

**Web Scraping Configuration:**

Web scraping configuration variables control how the server interacts with the San Mateo County website. These settings balance data extraction reliability with respectful resource usage.

`SMC_HOUSING_SELENIUM_HEADLESS` determines whether Selenium WebDriver operates in headless mode. The default "true" value is appropriate for production environments, while "false" enables visual debugging in development environments.

`SMC_HOUSING_REQUEST_TIMEOUT` sets the maximum time in seconds for HTTP requests. The default 30 seconds accommodates slow network conditions and large PDF downloads, but environments with reliable high-speed connections might reduce this value to 15-20 seconds.

`SMC_HOUSING_REQUEST_DELAY` specifies the minimum delay in seconds between requests to the source website. The default 1.0 second respects the website's resources while maintaining reasonable performance. Environments experiencing rate limiting should increase this value to 2-3 seconds.

`SMC_HOUSING_MAX_RETRIES` controls the number of retry attempts for failed requests. The default value of 3 provides resilience against temporary network issues without excessive delay. High-reliability environments might increase this to 5, while development environments could reduce it to 1-2.

`SMC_HOUSING_USER_AGENT` defines the User-Agent string sent with HTTP requests. The default identifies the MCP server appropriately, but some environments may require custom User-Agent strings for compliance or monitoring purposes.

**Logging Configuration:**

Logging configuration affects both operational visibility and system performance. Proper logging configuration enables effective monitoring and troubleshooting while avoiding excessive resource consumption.

`SMC_HOUSING_LOG_LEVEL` controls the verbosity of log output. Available levels include DEBUG, INFO, WARNING, ERROR, and CRITICAL. Development environments typically use DEBUG or INFO for comprehensive visibility, while production environments should use INFO or WARNING to balance visibility with performance.

### Configuration Files

While environment variables provide the primary configuration mechanism, configuration files offer structured approaches for complex deployments and enable version control of configuration settings.

**Environment File Configuration:**

Environment files provide a convenient method for managing multiple configuration variables in a single location. The server automatically loads configuration from `.env` files when present, simplifying deployment automation.

```bash
# .env file example
SMC_HOUSING_SERVER_NAME=smcgov-housing-mcp-prod
SMC_HOUSING_CACHE_TTL=48
SMC_HOUSING_REDIS_URL=redis://redis-server:6379/0
SMC_HOUSING_REQUEST_DELAY=2.0
SMC_HOUSING_LOG_LEVEL=INFO
```

Environment files should be secured with appropriate file permissions (600 or 640) to prevent unauthorized access to configuration settings, particularly when they contain sensitive information such as Redis credentials.

**JSON Configuration Support:**

For environments requiring structured configuration with validation, JSON configuration files provide type safety and schema validation capabilities.

```json
{
  "server": {
    "name": "smcgov-housing-mcp-prod",
    "version": "1.0.0"
  },
  "cache": {
    "ttl_hours": 48,
    "redis_url": "redis://redis-server:6379/0"
  },
  "scraping": {
    "request_timeout": 30,
    "request_delay": 2.0,
    "max_retries": 3,
    "selenium_headless": true
  },
  "logging": {
    "level": "INFO"
  }
}
```

JSON configuration enables configuration validation and provides clear structure for complex deployments with multiple environment-specific settings.

### Environment-Specific Configuration

Different deployment environments require distinct configuration approaches to optimize performance, security, and operational characteristics. Understanding environment-specific requirements ensures appropriate configuration for each deployment scenario.

**Development Environment Configuration:**

Development environments prioritize debugging capabilities and rapid iteration over performance optimization. Configuration settings should enable comprehensive logging and reduce caching to ensure that changes are immediately visible.

Development-specific settings include reduced cache TTL values (1-6 hours), DEBUG logging level, disabled Selenium headless mode for visual debugging, and reduced request delays for faster testing cycles. Development environments may also disable Redis caching to simplify setup and reduce dependencies.

**Testing Environment Configuration:**

Testing environments balance realistic operation with controlled conditions for automated testing and quality assurance. Configuration should enable comprehensive monitoring while maintaining predictable behavior for test automation.

Testing configurations typically include moderate cache TTL values (6-12 hours), INFO logging level, enabled Selenium headless mode for automated testing, and standard request delays to simulate production conditions. Testing environments may use in-memory caching or dedicated Redis instances to avoid interference with other environments.

**Production Environment Configuration:**

Production environments prioritize performance, reliability, and security. Configuration settings should optimize resource utilization while maintaining data accuracy and system stability.

Production configurations include extended cache TTL values (24-72 hours), WARNING or INFO logging levels, enabled Selenium headless mode, increased request delays to respect source website resources, and Redis caching for optimal performance. Production environments should also implement monitoring and alerting for configuration-related issues.

### Security Configuration

Security configuration protects both the MCP server and the source website from unauthorized access and abuse. Implementing appropriate security measures ensures responsible operation and maintains compliance with organizational security policies.

**Access Control Configuration:**

The MCP server operates through stdin/stdout communication, inheriting access controls from the parent process. Ensure that only authorized processes can communicate with the MCP server by implementing appropriate process-level security controls.

File system permissions should restrict access to configuration files, cache directories, and log files to the MCP server user account and authorized administrators. Configuration files containing sensitive information such as Redis credentials should use restrictive permissions (600) to prevent unauthorized access.

**Rate Limiting Configuration:**

Rate limiting configuration prevents the MCP server from overwhelming the source website and ensures respectful resource usage. Proper rate limiting maintains service availability while demonstrating responsible web scraping practices.

Configure request delays and retry limits based on the source website's capacity and terms of service. Monitor request patterns and adjust configuration as needed to maintain optimal balance between performance and resource respect.

**Data Security Configuration:**

While the MCP server processes public information, implementing data security measures protects against potential information disclosure and ensures compliance with organizational data handling policies.

Configure cache encryption for sensitive deployment environments, implement secure communication channels for Redis connections, and ensure that temporary files are properly secured and cleaned up after processing.


## MCP Integration

Integrating the San Mateo County Housing MCP Server with applications and MCP clients requires understanding the Model Context Protocol specification and implementing appropriate communication patterns. This section provides comprehensive guidance for various integration scenarios, from simple command-line usage to complex application architectures.

### Understanding the MCP Protocol

The Model Context Protocol defines a standardized interface for communication between AI applications and external data sources. The protocol operates through JSON-RPC messages exchanged over stdin/stdout, enabling seamless integration with various application architectures while maintaining security and performance.

**Protocol Fundamentals:**

MCP communication follows a request-response pattern where clients send JSON-RPC requests to the server and receive structured responses. The protocol supports three primary interaction types: server initialization, tool execution, and resource access. Each interaction type serves specific purposes in the overall integration architecture.

Server initialization establishes the communication session and negotiates capabilities between the client and server. During initialization, the client provides information about its capabilities and requirements, while the server responds with available tools and resources. This negotiation ensures compatibility and enables optimal integration configuration.

Tool execution represents the primary interaction pattern for accessing housing data. Clients invoke specific tools with appropriate parameters, and the server responds with structured data or error information. The tool execution pattern supports both synchronous and asynchronous operations, depending on the complexity of the requested operation.

Resource access provides clients with contextual information about the housing data domain and available capabilities. Resources include documentation, schema definitions, and contextual information that helps clients understand and utilize the available tools effectively.

**Message Structure and Format:**

MCP messages follow the JSON-RPC 2.0 specification, ensuring compatibility with existing JSON-RPC libraries and tools. Understanding the message structure enables effective debugging and custom client development.

Request messages include a unique identifier, method name, and parameters object. The identifier enables correlation between requests and responses, particularly important in asynchronous communication scenarios. Method names follow a hierarchical structure that clearly identifies the requested operation type.

Response messages include the request identifier, result data, or error information. Successful responses contain structured data that matches the tool's output schema, while error responses provide detailed information about failure causes and potential resolution steps.

### Client Integration Patterns

Different application architectures require distinct integration approaches to effectively utilize the MCP server capabilities. Understanding common integration patterns enables selection of the most appropriate approach for specific use cases.

**Command-Line Integration:**

Command-line integration provides the simplest approach for testing and scripting scenarios. This pattern involves direct process execution with stdin/stdout communication, making it ideal for automation scripts and development testing.

```bash
# Direct command-line usage
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"cli-client","version":"1.0.0"}}}' | python server.py

# Scripted integration example
#!/bin/bash
RESPONSE=$(echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_housing_statistics","arguments":{}}}' | python server.py)
echo "Housing Statistics: $RESPONSE"
```

Command-line integration enables rapid prototyping and testing of MCP functionality without requiring complex application development. This approach is particularly valuable for data analysis workflows and administrative scripts.

**Library Integration:**

Library integration involves embedding the MCP server within larger applications through process management and communication libraries. This pattern provides more sophisticated control over server lifecycle and communication patterns.

```python
import subprocess
import json
import asyncio

class SMCHousingMCPClient:
    def __init__(self, server_path):
        self.server_path = server_path
        self.process = None
    
    async def start(self):
        self.process = await asyncio.create_subprocess_exec(
            'python', self.server_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Initialize the server
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "python-client", "version": "1.0.0"}
            }
        }
        
        await self.send_request(init_request)
    
    async def send_request(self, request):
        request_json = json.dumps(request) + '\n'
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        response_line = await self.process.stdout.readline()
        return json.loads(response_line.decode())
    
    async def get_housing_statistics(self):
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_housing_statistics",
                "arguments": {}
            }
        }
        
        response = await self.send_request(request)
        return json.loads(response["result"]["content"][0]["text"])
    
    async def close(self):
        if self.process:
            self.process.terminate()
            await self.process.wait()

# Usage example
async def main():
    client = SMCHousingMCPClient('/path/to/server.py')
    await client.start()
    
    stats = await client.get_housing_statistics()
    print(f"Total affordable units: {stats['total_affordable_units']}")
    
    await client.close()

asyncio.run(main())
```

Library integration provides robust error handling, connection management, and type safety for production applications requiring reliable MCP communication.

**Service Integration:**

Service integration involves deploying the MCP server as a managed service that multiple applications can access through standardized interfaces. This pattern enables centralized housing data access with appropriate scaling and monitoring capabilities.

```yaml
# Kubernetes deployment example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smcgov-housing-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: smcgov-housing-mcp
  template:
    metadata:
      labels:
        app: smcgov-housing-mcp
    spec:
      containers:
      - name: mcp-server
        image: smcgov-housing-mcp:latest
        env:
        - name: SMC_HOUSING_CACHE_TTL
          value: "24"
        - name: SMC_HOUSING_REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: smcgov-housing-mcp-service
spec:
  selector:
    app: smcgov-housing-mcp
  ports:
  - port: 8080
    targetPort: 8080
```

Service integration enables horizontal scaling, load balancing, and centralized monitoring for high-availability deployments serving multiple applications.

### Application Integration Examples

Real-world application integration requires understanding specific use cases and implementing appropriate data flow patterns. These examples demonstrate common integration scenarios and provide templates for custom implementations.

**Web Application Integration:**

Web applications can integrate housing data through backend services that communicate with the MCP server. This pattern enables rich user interfaces while maintaining separation between presentation and data access layers.

```python
from flask import Flask, jsonify, request
import asyncio
from smchousing_client import SMCHousingMCPClient

app = Flask(__name__)
mcp_client = SMCHousingMCPClient('/path/to/server.py')

@app.route('/api/housing/statistics')
async def get_housing_statistics():
    try:
        stats = await mcp_client.get_housing_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/housing/eligibility', methods=['POST'])
async def check_eligibility():
    data = request.get_json()
    
    try:
        result = await mcp_client.check_eligibility(
            annual_income=data['annual_income'],
            family_size=data['family_size'],
            ami_category=data.get('ami_category', '80%')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/housing/notices')
async def get_public_notices():
    limit = request.args.get('limit', 10, type=int)
    
    try:
        notices = await mcp_client.get_public_notices(limit=limit)
        return jsonify(notices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    asyncio.run(mcp_client.start())
    app.run(debug=True)
```

Web application integration enables user-friendly interfaces for housing data access while maintaining backend flexibility and scalability.

**Data Analysis Integration:**

Data analysis workflows can leverage the MCP server to access housing data for research, reporting, and decision-making purposes. This integration pattern emphasizes data extraction and transformation capabilities.

```python
import pandas as pd
import matplotlib.pyplot as plt
from smchousing_client import SMCHousingMCPClient

async def analyze_housing_data():
    client = SMCHousingMCPClient('/path/to/server.py')
    await client.start()
    
    # Get housing statistics
    stats = await client.get_housing_statistics()
    
    # Get income limits for analysis
    income_limits = []
    for year in [2023, 2024, 2025]:
        for family_size in range(1, 9):
            limits = await client.get_income_limits(year=year, family_size=family_size)
            income_limits.extend(limits)
    
    # Convert to DataFrame for analysis
    df_limits = pd.DataFrame([limit for limit in income_limits])
    
    # Analyze income trends
    yearly_trends = df_limits.groupby(['year', 'family_size'])['ami_80_percent'].mean()
    
    # Create visualizations
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot housing statistics
    units_by_status = stats['units_by_status']
    ax1.pie(units_by_status.values(), labels=units_by_status.keys(), autopct='%1.1f%%')
    ax1.set_title('Housing Units by Status')
    
    # Plot income trends
    for family_size in range(1, 5):
        family_data = yearly_trends.xs(family_size, level='family_size')
        ax2.plot(family_data.index, family_data.values, marker='o', label=f'{family_size} person')
    
    ax2.set_title('80% AMI Income Limits by Year')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Income Limit ($)')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('housing_analysis.png')
    
    await client.close()

# Run analysis
asyncio.run(analyze_housing_data())
```

Data analysis integration enables comprehensive examination of housing trends and supports evidence-based policy and planning decisions.

**Chatbot Integration:**

Chatbot applications can integrate housing data to provide interactive assistance for housing-related inquiries. This pattern combines natural language processing with structured data access.

```python
import openai
from smchousing_client import SMCHousingMCPClient

class HousingChatbot:
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.openai_client = openai.OpenAI()
    
    async def process_query(self, user_message):
        # Determine intent and extract parameters
        intent_response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Analyze the user's housing-related query and extract relevant parameters."},
                {"role": "user", "content": user_message}
            ]
        )
        
        # Based on intent, call appropriate MCP tools
        if "eligibility" in user_message.lower():
            # Extract income and family size from message
            # Call eligibility check tool
            result = await self.mcp_client.check_eligibility(
                annual_income=75000,  # Extracted from message
                family_size=3         # Extracted from message
            )
            
            return f"Based on your income and family size, you {'are' if result['eligible'] else 'are not'} eligible for housing assistance."
        
        elif "statistics" in user_message.lower():
            stats = await self.mcp_client.get_housing_statistics()
            return f"San Mateo County has {stats['total_affordable_units']} affordable housing units across {stats['total_projects']} projects."
        
        else:
            return "I can help you with housing eligibility, statistics, and public notices. What would you like to know?"

# Usage example
async def main():
    mcp_client = SMCHousingMCPClient('/path/to/server.py')
    await mcp_client.start()
    
    chatbot = HousingChatbot(mcp_client)
    
    response = await chatbot.process_query("Am I eligible for housing assistance with $75,000 income and 3 family members?")
    print(response)
    
    await mcp_client.close()

asyncio.run(main())
```

Chatbot integration provides natural language interfaces for housing data access, making information more accessible to diverse user populations.


## Production Deployment

Production deployment of the San Mateo County Housing MCP Server requires careful consideration of scalability, reliability, and operational requirements. This section addresses the critical aspects of production deployment, from infrastructure planning through operational procedures.

### Infrastructure Requirements

Production infrastructure must support the MCP server's operational characteristics while providing appropriate scalability and reliability. The server's resource requirements vary based on usage patterns, caching configuration, and integration complexity.

**Compute Resources:**

Production deployments typically require dedicated compute resources to ensure consistent performance and isolation from other services. Virtual machines or containers should be sized based on expected concurrent usage and data processing requirements.

For moderate usage scenarios (up to 100 requests per hour), a single-core virtual machine with 2 GB RAM provides adequate performance. High-usage scenarios (500+ requests per hour) benefit from multi-core systems with 4-8 GB RAM to support concurrent request processing and caching operations.

**Storage Requirements:**

Storage requirements include space for application files, cache data, temporary PDF downloads, and log files. Production deployments should provision adequate storage with appropriate performance characteristics for the expected workload.

Cache storage requirements depend on the configured TTL values and data volume. A typical deployment with 24-hour caching requires 100-500 MB for cache data, while extended caching periods may require 1-2 GB. Temporary storage for PDF processing requires an additional 50-100 MB.

**Network Considerations:**

Network configuration affects both performance and reliability of the MCP server. Production deployments should ensure adequate bandwidth and implement appropriate security controls for external connectivity.

Outbound bandwidth requirements depend on the frequency of data updates and PDF downloads. Typical deployments require 1-5 Mbps sustained bandwidth, with burst capacity for large PDF downloads. Network latency to the San Mateo County website affects response times, particularly for real-time requests.

### High Availability Configuration

High availability deployment ensures continuous service availability despite individual component failures. The MCP server's stateless design simplifies high availability implementation through redundancy and load balancing.

**Load Balancing:**

Load balancing distributes requests across multiple MCP server instances to improve performance and provide fault tolerance. Since the MCP server communicates through stdin/stdout, traditional HTTP load balancers require adaptation for MCP protocol support.

```yaml
# Kubernetes horizontal pod autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: smcgov-housing-mcp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: smcgov-housing-mcp
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Redundancy Planning:**

Redundancy planning addresses potential failure scenarios and ensures appropriate backup systems. The MCP server's stateless design enables straightforward redundancy implementation through multiple deployment regions or availability zones.

Geographic redundancy protects against regional outages and provides improved performance for distributed user bases. Deploy MCP server instances in multiple regions with appropriate failover mechanisms to maintain service availability during regional disruptions.

**Data Backup and Recovery:**

While the MCP server primarily processes public data, backup and recovery procedures protect against configuration loss and enable rapid deployment restoration. Focus backup efforts on configuration files, custom modifications, and operational procedures.

Configuration backup should include environment files, service definitions, and deployment scripts. Store backups in version control systems with appropriate access controls and retention policies. Test recovery procedures regularly to ensure rapid restoration capabilities.

## Monitoring and Maintenance

Effective monitoring and maintenance ensure optimal performance and early detection of potential issues. The MCP server provides multiple monitoring interfaces and supports integration with standard monitoring platforms.

### Performance Monitoring

Performance monitoring tracks key metrics that indicate server health and operational efficiency. Understanding normal performance baselines enables early detection of degradation and capacity planning for growth.

**Key Performance Indicators:**

Response time metrics indicate the server's ability to process requests efficiently. Monitor average response times for different tool types, with particular attention to operations requiring web scraping or PDF processing. Establish baseline response times during normal operation and alert on significant deviations.

Cache hit rates directly impact performance and external resource usage. Monitor cache effectiveness across different data types and adjust TTL values based on hit rate analysis. High cache hit rates (>80%) indicate effective caching configuration, while low hit rates may require TTL adjustment or cache size increases.

Resource utilization monitoring tracks CPU, memory, and storage usage patterns. Establish normal utilization ranges and implement alerting for resource exhaustion scenarios. Memory usage patterns help optimize cache configuration and identify potential memory leaks.

**Monitoring Implementation:**

```python
# Example monitoring integration
import structlog
import time
from prometheus_client import Counter, Histogram, Gauge

# Metrics definitions
REQUEST_COUNT = Counter('mcp_requests_total', 'Total MCP requests', ['method', 'status'])
REQUEST_DURATION = Histogram('mcp_request_duration_seconds', 'Request duration', ['method'])
CACHE_HIT_RATE = Gauge('mcp_cache_hit_rate', 'Cache hit rate percentage')

class MonitoringMixin:
    def __init__(self):
        self.logger = structlog.get_logger()
    
    async def handle_request_with_monitoring(self, request):
        method = request.get('method', 'unknown')
        start_time = time.time()
        
        try:
            response = await self.handle_request(request)
            REQUEST_COUNT.labels(method=method, status='success').inc()
            return response
        except Exception as e:
            REQUEST_COUNT.labels(method=method, status='error').inc()
            self.logger.error("Request failed", method=method, error=str(e))
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_DURATION.labels(method=method).observe(duration)
```

### Log Management

Comprehensive log management provides visibility into server operations and enables effective troubleshooting. The MCP server uses structured logging to facilitate automated analysis and monitoring integration.

**Log Configuration:**

Configure appropriate log levels based on operational requirements and storage constraints. Production environments typically use INFO or WARNING levels to balance visibility with performance, while development environments may use DEBUG for comprehensive troubleshooting.

Log rotation prevents excessive disk usage while maintaining historical data for analysis. Configure log rotation based on file size (10-50 MB) or time intervals (daily/weekly) depending on log volume and retention requirements.

**Log Analysis:**

Structured logging enables automated analysis and alerting based on log patterns. Implement log aggregation and analysis tools to identify trends, detect anomalies, and support troubleshooting efforts.

```bash
# Example log analysis queries
# Find error patterns
grep "level.*error" /var/log/smcgov-housing-mcp.log | jq '.error' | sort | uniq -c

# Monitor request patterns
grep "method.*tools/call" /var/log/smcgov-housing-mcp.log | jq '.params.name' | sort | uniq -c

# Analyze response times
grep "duration" /var/log/smcgov-housing-mcp.log | jq '.duration' | awk '{sum+=$1; count++} END {print "Average:", sum/count}'
```

### Maintenance Procedures

Regular maintenance ensures continued optimal performance and addresses potential issues before they impact operations. Establish maintenance schedules and procedures that minimize service disruption while maintaining system health.

**Routine Maintenance:**

Cache maintenance involves periodic cleanup of expired entries and optimization of cache configuration. Monitor cache performance and adjust TTL values based on data update patterns and usage requirements.

Dependency updates maintain security and performance improvements from upstream packages. Establish regular update schedules with appropriate testing procedures to ensure compatibility and stability.

**Preventive Maintenance:**

Capacity planning anticipates growth requirements and ensures adequate resources for future needs. Monitor usage trends and resource utilization to identify when scaling or optimization is required.

Performance optimization involves analyzing bottlenecks and implementing improvements to enhance efficiency. Regular performance reviews identify opportunities for configuration tuning and architectural improvements.

## Troubleshooting

Effective troubleshooting requires understanding common issues and implementing systematic diagnostic procedures. This section provides guidance for identifying and resolving typical operational problems.

### Common Issues

**Connection Problems:**

Network connectivity issues represent the most common source of operational problems. The MCP server requires reliable connectivity to the San Mateo County website for data extraction and PDF downloads.

Symptoms of connectivity issues include timeout errors, failed PDF downloads, and empty response data. Diagnostic steps include verifying network connectivity, checking firewall configurations, and testing direct access to source URLs.

**Performance Issues:**

Performance degradation may result from various factors including resource constraints, cache misses, or external service slowdowns. Systematic performance analysis identifies the root cause and appropriate resolution strategies.

Monitor response times, resource utilization, and cache hit rates to identify performance bottlenecks. Compare current performance against established baselines to quantify degradation and track improvement efforts.

**Data Quality Issues:**

Data quality problems may arise from changes to the source website structure or content format. The MCP server includes fallback mechanisms and error handling to maintain operation despite source changes.

Implement data validation and quality checks to detect inconsistencies or missing information. Monitor extraction success rates and implement alerting for significant quality degradation.

### Diagnostic Procedures

**Log Analysis:**

Structured logging provides comprehensive diagnostic information for troubleshooting various issues. Implement systematic log analysis procedures to efficiently identify problem causes and resolution approaches.

```bash
# Diagnostic log analysis examples
# Check for recent errors
tail -n 1000 /var/log/smcgov-housing-mcp.log | grep "level.*error"

# Analyze request patterns
grep "method.*tools/call" /var/log/smcgov-housing-mcp.log | tail -n 100 | jq '.params.name'

# Monitor cache performance
grep "cache" /var/log/smcgov-housing-mcp.log | tail -n 50 | jq '{event: .event, key: .key}'
```

**Performance Testing:**

Performance testing validates server operation under various load conditions and identifies capacity limits. Implement regular performance testing to establish baselines and detect degradation.

```python
# Performance testing script
import asyncio
import time
from smchousing_client import SMCHousingMCPClient

async def performance_test():
    client = SMCHousingMCPClient('/path/to/server.py')
    await client.start()
    
    # Test response times for different operations
    operations = [
        ('get_housing_statistics', {}),
        ('get_income_limits', {'year': 2025, 'family_size': 3}),
        ('check_eligibility', {'annual_income': 75000, 'family_size': 3})
    ]
    
    for operation, args in operations:
        start_time = time.time()
        try:
            result = await getattr(client, operation)(**args)
            duration = time.time() - start_time
            print(f"{operation}: {duration:.2f}s - Success")
        except Exception as e:
            duration = time.time() - start_time
            print(f"{operation}: {duration:.2f}s - Error: {e}")
    
    await client.close()

asyncio.run(performance_test())
```

## Security Considerations

Security considerations ensure that the MCP server operates safely while protecting both the deployment environment and the source website from potential threats. Implementing comprehensive security measures maintains operational integrity and demonstrates responsible resource usage.

### Access Control

Access control mechanisms prevent unauthorized usage and ensure that only legitimate applications can interact with the MCP server. The server's stdin/stdout communication model inherits access controls from the parent process, requiring careful process management.

**Process-Level Security:**

Run the MCP server under dedicated user accounts with minimal system privileges. Implement process isolation through containers or virtual machines to limit potential security impact from vulnerabilities or misconfigurations.

Configure file system permissions to restrict access to configuration files, cache directories, and log files. Sensitive configuration information should be protected with restrictive permissions (600) and appropriate ownership settings.

**Network Security:**

While the MCP server does not accept inbound network connections, outbound connectivity requires security consideration. Implement network controls that allow necessary connectivity while preventing unauthorized access or data exfiltration.

Configure firewalls to permit outbound HTTPS connections to the San Mateo County website while blocking unnecessary network access. Monitor network traffic patterns to detect anomalous behavior or potential security incidents.

### Data Protection

Data protection measures ensure that housing information is handled appropriately and that temporary data storage does not create security vulnerabilities. While the server processes public information, implementing data protection demonstrates security best practices.

**Cache Security:**

Implement appropriate security controls for cache storage, particularly when using Redis or other external caching systems. Configure authentication and encryption for cache connections to prevent unauthorized access or data interception.

Regularly clean up temporary files and cache entries to minimize data exposure duration. Implement secure deletion procedures for sensitive temporary files to prevent data recovery from storage media.

**Logging Security:**

Configure logging to avoid capturing sensitive information while maintaining adequate diagnostic capability. Implement log rotation and secure storage to prevent unauthorized access to operational information.

Monitor log access and implement alerting for unauthorized log access attempts. Ensure that log files are included in backup and retention policies with appropriate security controls.

### Compliance Considerations

Compliance considerations ensure that the MCP server operation aligns with organizational policies and regulatory requirements. Understanding compliance requirements enables appropriate implementation of security controls and operational procedures.

**Data Handling Compliance:**

While the MCP server processes public information, organizational data handling policies may require specific security controls or operational procedures. Review applicable policies and implement necessary controls to ensure compliance.

Document data flows and processing procedures to support compliance auditing and verification. Maintain records of security controls and operational procedures to demonstrate compliance with applicable requirements.

**Operational Compliance:**

Implement operational procedures that align with organizational security policies and industry best practices. Regular security reviews and updates ensure continued compliance as requirements evolve.

Establish incident response procedures for security events or operational issues. Document procedures and conduct regular training to ensure effective response to potential security incidents.

---

## Conclusion

The San Mateo County Housing MCP Server provides a robust and scalable solution for accessing housing data through the Model Context Protocol. This deployment guide has covered all aspects of implementation, from initial installation through production operation and maintenance.

Successful deployment requires careful attention to system requirements, configuration management, and operational procedures. The modular architecture and comprehensive error handling ensure reliable operation across various deployment scenarios, while the standardized MCP interface enables seamless integration with diverse applications.

Regular monitoring, maintenance, and security reviews ensure continued optimal performance and protection against potential issues. The server's design emphasizes responsible resource usage and demonstrates best practices for web scraping and data integration.

For additional support and updates, refer to the project documentation and community resources. The MCP server represents a foundation for housing data access that can be extended and customized to meet specific organizational requirements while maintaining compatibility with the broader MCP ecosystem.

## References

[1] Model Context Protocol Specification - https://spec.modelcontextprotocol.io/
[2] San Mateo County Department of Housing - https://www.smcgov.org/housing
[3] Python asyncio Documentation - https://docs.python.org/3/library/asyncio.html
[4] Pydantic Data Validation - https://docs.pydantic.dev/
[5] BeautifulSoup Documentation - https://www.crummy.com/software/BeautifulSoup/bs4/doc/
[6] Selenium WebDriver Documentation - https://selenium-python.readthedocs.io/
[7] Redis Caching Documentation - https://redis.io/documentation
[8] Docker Container Deployment - https://docs.docker.com/
[9] Kubernetes Orchestration - https://kubernetes.io/docs/
[10] JSON-RPC 2.0 Specification - https://www.jsonrpc.org/specification

