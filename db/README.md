# Database Management

This project uses:

* **PostgreSQL** — the actual database
* **Docker Compose** — runs PostgreSQL in a container
* **SQLAlchemy** — defines the database structure using Python models
* **Alembic** — manages database changes (migrations)

---

## 1. Start the Database

Start PostgreSQL with Docker Compose:

```bash
docker compose --env-file ../.env/.env-dev up -d
```

Check that the database is running:

```bash
docker ps
```

You should see:

```text
toran_postgres ... Up
```

To see the database logs:

```bash
docker logs toran_postgres
```

Stop the database:

```bash
docker compose down
```

> `docker compose down -v` also deletes the database volume and **all database data**.

---

## 2. Database Models

The database structure is defined in:

```text
models.py
```

For example:

```python
class Duty(Base):
    __tablename__ = "duties"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone_number = Column(String)
```

Think of `models.py` as the **desired structure of the database**.

If you want to add a new column, change the model.

---

## 3. Alembic

Alembic keeps track of changes to the database.

Initialize Alembic (only needed once):

```bash
alembic init alembic
```

After changing `models.py`, create a migration:

```bash
alembic revision --autogenerate -m "describe your change"
```

For example:

```bash
alembic revision --autogenerate -m "add phone number to duties"
```

Alembic creates a new file in:

```text
alembic/versions/
```

**Always check the generated migration before applying it.**

---

## 4. Apply Migrations

Apply all migrations that haven't been applied yet:

```bash
alembic upgrade head
```

`head` means:

> Bring the database to the latest version.

---

## 5. Check Current Database Version

```bash
alembic current
```

See the migration history:

```bash
alembic history
```

---

## 6. Undo a Migration

Go back one migration:

```bash
alembic downgrade -1
```

Go back to a specific migration:

```bash
alembic downgrade <revision_id>
```

Be careful with downgrades because they can delete data.

---

## 7. The Normal Workflow

Most of the time, you will do this:

### Step 1 — Change the model

Edit:

```text
models.py
```

For example, add:

```python
email = Column(String)
```

### Step 2 — Create a migration

```bash
alembic revision --autogenerate -m "add email to duties"
```

### Step 3 — Check the migration

Look inside:

```text
alembic/versions/
```

Make sure Alembic generated what you expected.

### Step 4 — Apply it

```bash
alembic upgrade head
```

That's it.

---

## 8. Important Concept

There are three different things:

```text
models.py
    ↓
"What I want the database to look like"

Alembic migrations
    ↓
"How the database should change"

PostgreSQL
    ↓
"The actual database"
```

For example:

```text
models.py
    ↓
Add phone_number
    ↓
alembic revision --autogenerate
    ↓
New migration
    ↓
alembic upgrade head
    ↓
PostgreSQL now has phone_number
```

---

## 9. Useful Commands Cheat Sheet

```bash
# Start PostgreSQL
docker compose --env-file ../.env/.env-dev up -d

# Stop PostgreSQL
docker compose down

# Check containers
docker ps

# View PostgreSQL logs
docker logs toran_postgres

# Create migration after changing models.py
alembic revision --autogenerate -m "describe change"

# Apply migrations
alembic upgrade head

# Show current migration
alembic current

# Show migration history
alembic history

# Undo last migration
alembic downgrade -1
```

### Golden Rule

**Never manually change the database structure if you can avoid it.**

Change `models.py` → create a migration → review it → run `alembic upgrade head`.

This keeps the database structure consistent between developers, computers, and environments.
