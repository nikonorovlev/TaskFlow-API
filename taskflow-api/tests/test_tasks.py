import pytest

URL = "/api/v1/tasks/"

def make(client, **kwargs):
    return client.post(URL, json={"title": "Example", **kwargs})

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}

def test_root(client):
    assert client.get("/").status_code == 200

def test_create(client):
    r = make(client, priority="high")
    assert r.status_code == 201
    assert r.json()["priority"] == "high"
    assert r.json()["id"] == 1

def test_create_defaults(client):
    assert make(client).json()["status"] == "todo"

def test_get(client):
    task_id = make(client).json()["id"]
    assert client.get(f"{URL}{task_id}").status_code == 200

def test_get_missing(client):
    assert client.get(f"{URL}999").status_code == 404

def test_list(client):
    make(client)
    make(client, title="Second")
    assert len(client.get(URL).json()) == 2

def test_update(client):
    task_id = make(client).json()["id"]
    r = client.patch(f"{URL}{task_id}", json={"status": "done"})
    assert r.status_code == 200
    assert r.json()["title"] == "Example"
    assert r.json()["status"] == "done"

def test_update_missing(client):
    assert client.patch(f"{URL}999", json={"title": "x"}).status_code == 404

def test_delete(client):
    task_id = make(client).json()["id"]
    assert client.delete(f"{URL}{task_id}").status_code == 204
    assert client.get(f"{URL}{task_id}").status_code == 404

def test_delete_missing(client):
    assert client.delete(f"{URL}999").status_code == 404

def test_filter_status(client):
    make(client, status="done")
    make(client)
    assert len(client.get(URL, params={"status": "done"}).json()) == 1

def test_filter_priority(client):
    make(client, priority="high")
    make(client)
    assert len(client.get(URL, params={"priority": "high"}).json()) == 1

def test_search(client):
    make(client, title="Learn Python")
    make(client, title="Other")
    assert len(client.get(URL, params={"search": "python"}).json()) == 1

def test_search_literal_percent(client):
    make(client, title="100% done")
    make(client, title="Other")
    assert len(client.get(URL, params={"search": "%"}).json()) == 1

def test_due_before(client):
    make(client, due_date="2026-10-15")
    make(client, due_date="2026-11-15")
    assert len(client.get(URL, params={"due_before": "2026-10-20"}).json()) == 1

def test_pagination(client):
    for i in range(3):
        make(client, title=f"Task {i}")
    assert len(client.get(URL, params={"limit": 2, "offset": 1}).json()) == 2

def test_sort_priority(client):
    make(client, title="Low", priority="low")
    make(client, title="High", priority="high")
    assert client.get(URL, params={"sort_by": "priority", "sort_order": "desc"}).json()[0]["title"] == "High"

def test_stats(client):
    make(client, status="done")
    make(client)
    assert client.get("/api/v1/stats/").json() == {"total": 2, "todo": 1, "in_progress": 0, "done": 1}

def test_stats_empty(client):
    assert client.get("/api/v1/stats/").json()["total"] == 0

@pytest.mark.parametrize("payload", [
    {"title": ""}, {"title": "   "}, {"title": "x" * 201},
    {"title": "A", "status": "invalid"}, {"title": "A", "priority": "urgent"},
    {"title": "A", "due_date": "invalid"}, {},
])
def test_invalid_create(client, payload):
    assert client.post(URL, json=payload).status_code == 422

@pytest.mark.parametrize("payload", [{"title": None}, {"status": None}, {"priority": None}, {"title": "   "}])
def test_invalid_update(client, payload):
    task_id = make(client).json()["id"]
    assert client.patch(f"{URL}{task_id}", json=payload).status_code == 422

def test_clear_description(client):
    task_id = make(client, description="Details").json()["id"]
    assert client.patch(f"{URL}{task_id}", json={"description": None}).json()["description"] is None

def test_invalid_limit(client):
    assert client.get(URL, params={"limit": 101}).status_code == 422

def test_invalid_sort(client):
    assert client.get(URL, params={"sort_by": "unknown"}).status_code == 422
