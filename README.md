# TravelORM

A Python ORM library for the Travel Itinerary application database.

## Overview

TravelORM provides a simple, consistent interface for interacting with the Travel Itinerary database. It handles database connections, transaction management, and provides model classes for all database tables.

## Features

- Database connection management with AWS Secrets Manager integration
- Model classes for all database tables
- Basic CRUD operations for all models
- Transaction management
- Support for complex queries

## Installation

```bash
# Install from the repository
pip install -e /path/to/TravelORM

# Or install directly in development mode
cd /path/to/TravelORM
pip install -e .
```

## Usage

```python
from travel_orm import connection
from travel_orm.models import TravelAdvisor, Itinerary

# Test the database connection
connection_status = connection.test_connection()
print(connection_status)

# Create a new travel advisor
advisor = TravelAdvisor.create(
    name="Jane Smith",
    phone_number="555-123-4567",
    company_name="Luxury Travel Co."
)

# Create an itinerary
itinerary = Itinerary.create(
    travel_advisor_id=advisor.id,
    start_date="2025-07-01",
    duration=7,
    destination="Paris, France"
)

# Get an itinerary by ID
itinerary = Itinerary.get_by_id("123e4567-e89b-12d3-a456-426614174000")

# List all travel advisors
advisors = TravelAdvisor.list_all()

# Update an itinerary
itinerary.update(
    duration=10,
    destination="Paris and London"
)

# Delete an itinerary
itinerary.delete()
```

## Development

### Running Tests

```bash
cd /path/to/TravelORM
pytest
```

## License

Proprietary - All rights reserved.
