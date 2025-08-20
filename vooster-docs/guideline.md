# Code Guideline: Slack Q&A Instant Search MVP

## 1. Project Overview

This project aims to build a web application that allows developers and PMs to quickly find technical solutions from internal Slack conversations. It involves importing Slack data, generating OpenAI embeddings, storing them in ChromaDB, providing a natural language question input and answer API, and a simple web UI. The core technologies used are Python 3.11, FastAPI, ChromaDB, OpenAI embeddings, and Streamlit.

Key architectural decisions include:
- A layered architecture with separation of concerns (API, business logic, data access, infrastructure).
- Domain-driven organization, separating Slack data processing, embedding generation, search, and UI into distinct modules.
- Feature-based modules for search, data upload, and UI themes.

## 2. Core Principles

- **Readability**: Code should be easy to understand and maintain.
- **Efficiency**: Code should be optimized for performance and resource utilization.
- **Testability**: Code should be designed to facilitate unit and integration testing.
- **Modularity**: Code should be broken down into reusable components.
- **Consistency**: Code should adhere to a consistent style and structure.

## 3. Language-Specific Guidelines

### Python

#### File Organization and Directory Structure

-   Follow the defined file and folder structure in the TRD.
-   Each module should have a clear purpose and responsibility.
-   Use descriptive filenames.

#### Import/Dependency Management

-   Use `requirements.txt` for managing dependencies.
-   Use absolute imports for project modules and relative imports within the same package.
-   Sort imports alphabetically within each group (standard library, third-party, local).

```python
# MUST: Correct import style
import os
import sys

import pandas as pd
from chromadb import Client

from app.core import config
from app.services import embedding
```

```python
# MUST NOT: Avoid wildcard imports
# Reason: Makes it difficult to track dependencies and can lead to namespace collisions.
from app.core import *
```

#### Error Handling Patterns

-   Use `try...except` blocks for handling potential exceptions.
-   Log exceptions with sufficient context.
-   Raise specific exceptions when appropriate.
-   Avoid bare `except` clauses.

```python
# MUST: Proper error handling
try:
    result = some_function()
except ValueError as e:
    logger.error(f"ValueError occurred: {e}")
    raise  # Re-raise if the error cannot be handled
except Exception as e:
    logger.exception("Unexpected error occurred") # Log the full traceback
    return None # Or handle gracefully
```

```python
# MUST NOT: Bare except clause
# Reason: Catches all exceptions, making debugging difficult and potentially masking critical errors.
try:
    result = some_function()
except:
    print("An error occurred")
```

### FastAPI

#### File Organization

- Follow the directory structure defined in the TRD.
- Use separate modules for different API endpoints.

#### Dependency Injection
- Use FastAPI's dependency injection system for managing dependencies.
- Define dependencies as functions with type hints.

```python
# MUST: Using dependency injection
from fastapi import Depends, FastAPI

app = FastAPI()

def get_db():
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/{item_id}")
async def read_item(item_id: int, db: DatabaseSession = Depends(get_db)):
    item = db.query(Item).get(item_id)
    return item
```

#### Response Models

- Use Pydantic models for defining request and response bodies.
- Ensure response models accurately reflect the data being returned.

```python
# MUST: Using Pydantic models
from pydantic import BaseModel

class Message(BaseModel):
    text: str
    role: str
    ts: str

from typing import List
class ResponseModel(BaseModel):
    results: List[Message]

@app.post("/search", response_model=ResponseModel)
async def search(query: str):
    # ... search logic ...
    return ResponseModel(results=[...])
```

### Streamlit

#### File Organization

- Separate UI components into reusable functions.
- Use a main file to orchestrate the UI.

#### State Management

- Use Streamlit's `st.session_state` for managing state.
- Avoid directly modifying session state variables.

```python
# MUST: Using st.session_state
import streamlit as st

if 'counter' not in st.session_state:
    st.session_state['counter'] = 0

def increment_counter():
    st.session_state['counter'] += 1

st.button('Increment', on_click=increment_counter)
st.write(f"Counter: {st.session_state['counter']}")
```

#### UI Components

- Use Streamlit's built-in UI components.
- Customize UI components using CSS or JavaScript if necessary.

## 4. Code Style Rules

### MUST Follow:

-   **PEP 8 Compliance**: Adhere to PEP 8 style guidelines for Python code.
    *   Rationale: Improves readability and consistency.
    *   Implementation: Use a linter (e.g., `flake8`, `pylint`) to enforce PEP 8.
-   **Descriptive Naming**: Use clear and descriptive names for variables, functions, and classes.
    *   Rationale: Makes code easier to understand and maintain.
    *   Implementation: Choose names that accurately reflect the purpose of the element.
-   **Docstrings**: Write docstrings for all functions, classes, and modules.
    *   Rationale: Provides documentation and helps with code understanding.
    *   Implementation: Use reStructuredText or Google-style docstrings.
-   **Type Hints**: Use type hints for function arguments and return values.
    *   Rationale: Improves code readability and helps with static analysis.
    *   Implementation: Add type hints to function signatures (e.g., `def add(x: int, y: int) -> int:`).
-   **Logging**: Use the `logging` module for logging events.
    *   Rationale: Provides a structured way to record events and debug issues.
    *   Implementation: Configure a logger and use it to log events at appropriate levels (e.g., `INFO`, `WARNING`, `ERROR`).
-   **Unit Tests**: Write unit tests for all critical functionality.
    *   Rationale: Ensures code correctness and prevents regressions.
    *   Implementation: Use `pytest` or `unittest` to write and run tests.
-   **Asynchronous Programming**: Use `async` and `await` for I/O-bound operations.
    *   Rationale: Improves application performance and responsiveness.
    *   Implementation: Use `async def` to define asynchronous functions and `await` to call them.
-   **Consistent Formatting**: Use a code formatter (e.g., `black`) to ensure consistent code formatting.
    *   Rationale: Improves code readability and reduces style-related debates.
    *   Implementation: Configure a code formatter and run it automatically on every commit.

```python
# MUST: Proper docstring example
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    """Processes the input data by cleaning and transforming it.

    Args:
        data: A Pandas DataFrame containing the data to process.

    Returns:
        A Pandas DataFrame containing the processed data.
    """
    # ... processing logic ...
    return processed_data
```

### MUST NOT Do:

-   **Code Duplication**: Avoid duplicating code.
    *   Rationale: Makes code harder to maintain and increases the risk of errors.
    *   Implementation: Extract common logic into reusable functions or classes.
-   **Hardcoded Values**: Avoid hardcoding values in the code.
    *   Rationale: Makes code less flexible and harder to configure.
    *   Implementation: Use configuration files or environment variables to store values.
-   **Long Functions**: Avoid writing long functions.
    *   Rationale: Makes code harder to understand and maintain.
    *   Implementation: Break down long functions into smaller, more manageable functions.
-   **Nested Conditional Statements**: Avoid deeply nested conditional statements.
    *   Rationale: Makes code harder to read and understand.
    *   Implementation: Use guard clauses or refactor the code to reduce nesting.
-   **Ignoring Errors**: Avoid ignoring errors without handling them.
    *   Rationale: Can lead to unexpected behavior and make debugging difficult.
    *   Implementation: Handle errors gracefully and log them appropriately.
-   **Over-Engineering**: Avoid over-engineering solutions.
    *   Rationale: Can lead to unnecessary complexity and increased development time.
    *   Implementation: Keep solutions simple and focused on the core requirements.
-   **Unnecessary Comments**: Avoid writing obvious or redundant comments.
    *   Rationale: Clutters the code and makes it harder to read.
    *   Implementation: Write comments only when necessary to explain complex logic or non-obvious behavior.
-   **Global Variables**: Avoid using global variables.
    *   Rationale: Makes code harder to reason about and can lead to unexpected side effects.
    *   Implementation: Use dependency injection or pass data explicitly between functions.
-   **Complex State Management**: Avoid overly complex state management patterns for this MVP.
    * Rationale: Adds unnecessary overhead and complexity. Streamlit's `st.session_state` is sufficient.
-   **Huge, Multi-Responsibility Modules**: Avoid creating single files with excessive lines of code and multiple responsibilities.
    * Rationale: Reduces maintainability and makes it difficult to understand the module's purpose.

```python
# MUST NOT: Hardcoding values
# Reason: Makes the code inflexible and difficult to configure.
def connect_to_database():
    host = "localhost"  # Hardcoded host
    port = 5432         # Hardcoded port
    # ...
```

```python
# MUST NOT: Ignoring Errors
# Reason: Hides potential issues and makes debugging difficult.
try:
    result = some_operation()
except Exception:
    pass  # Ignoring the error
```

## 5. Architecture Patterns

### Component/Module Structure Guidelines

-   **Layered Architecture**: Separate the application into layers (API, business logic, data access, infrastructure).
-   **Domain-Driven Design**: Organize code around domain concepts (e.g., Slack data, embeddings, search).
-   **Feature-Based Modules**: Group code by features (e.g., search, data upload, UI themes).
-   **Shared Components**: Store common utilities and data types in a shared module.

### Data Flow Patterns

-   **Client-Server Communication**: Use HTTP requests and JSON responses for communication between the Streamlit UI and the FastAPI API.
-   **Database Interaction**: Use ChromaDB's API to interact with the vector database.
-   **External Service Integration**: Use OpenAI's API to generate embeddings and summarize answers.
-   **Data Synchronization**: Re-index embeddings in ChromaDB whenever Slack data is updated.

### State Management Conventions

-   Use Streamlit's `st.session_state` for managing UI state.
-   Avoid complex state management patterns for this MVP.

### API Design Standards

-   **RESTful API**: Design APIs following RESTful principles.
-   **JSON Format**: Use JSON for request and response bodies.
-   **Descriptive Endpoints**: Use clear and descriptive endpoint names.
-   **Pydantic Models**: Use Pydantic models for request and response validation.
-   **Error Handling**: Return appropriate HTTP status codes for errors.
-   **Asynchronous Operations**: Use asynchronous operations for I/O-bound tasks.

```python
# MUST: Example of a RESTful API endpoint
from fastapi import FastAPI

app = FastAPI()

@app.get("/messages/{message_id}")
async def get_message(message_id: int):
    """Retrieves a message by its ID."""
    # ... logic to retrieve message from database ...
    return {"message": "example message"}
```
