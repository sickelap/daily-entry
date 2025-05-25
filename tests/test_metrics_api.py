from uuid import UUID
from dateutil import parser
from app import config
from app.model import MetricEntity, UserEntity, ValueEntity
from sqlmodel import delete, select
from tests.conftest import (
    INVALID_TOKEN,
    VALID_TOKEN,
)


def isuuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except Exception:
        return False


def create_metric(session, user, name, values=[], clear=True):
    if clear:
        session.exec(delete(MetricEntity))
    metric = MetricEntity(user=user, name=str(name))
    session.add(metric)
    session.commit()
    session.refresh(metric)
    for value in values:
        session.add(ValueEntity(**value, metric=metric))
    session.commit()
    session.refresh(metric)
    return metric


def test_get_metrics_as_anonymous(client):
    response = client.get(f"{config.API_PREFIX}{config.METRICS_URI}")
    assert response.status_code == 401


def test_get_metrics_with_invalid_token(client):
    response = client.get(
        f"{config.API_PREFIX}{config.METRICS_URI}",
        headers={config.AUTH_HEADER: INVALID_TOKEN},
    )
    assert response.status_code == 403


def test_create_metric(client, session):
    session.exec(delete(MetricEntity))
    headers = {config.AUTH_HEADER: VALID_TOKEN}
    payload = {"name": "height"}
    response = client.post(
        f"{config.API_PREFIX}{config.METRICS_URI}", headers=headers, json=payload
    )
    assert response.status_code == 200
    metrics = session.exec(
        select(MetricEntity)
        .join(UserEntity)
        .where(UserEntity.token == UUID(VALID_TOKEN))
    ).all()
    assert metrics is not None
    assert len(metrics) == 1
    assert metrics[0].name == "height"


def test_get_metrics(client, user, session):
    create_metric(session, user, "one")
    create_metric(session, user, "two", clear=False)

    headers = {config.AUTH_HEADER: VALID_TOKEN}
    response = client.get(f"{config.API_PREFIX}{config.METRICS_URI}", headers=headers)
    assert response.status_code == 200
    metrics = session.exec(
        select(MetricEntity)
        .join(UserEntity)
        .where(UserEntity.token == UUID(VALID_TOKEN))
    ).all()
    assert len(response.json()) == len(metrics)


def test_add_values_without_timestamp(client, session, user):
    metric = create_metric(session, user, "three")
    values_uri = config.VALUES_URI.replace("{metric_id}", str(metric.id))

    headers = {config.AUTH_HEADER: str(user.token)}
    payload = [{"value": 123.4}]
    response = client.post(
        f"{config.API_PREFIX}{values_uri}", headers=headers, json=payload
    )
    assert response.status_code == 200
    stats = session.exec(select(ValueEntity).where(ValueEntity.metric == metric)).all()
    assert stats is not None
    assert len(stats) == 1
    assert float(stats[0].value) == 123.4


def test_add_values_with_int_timestamp(client, session, user):
    metric = create_metric(session, user, "four")
    headers = {config.AUTH_HEADER: VALID_TOKEN}
    payload = [
        {"timestamp": 1, "value": 123.4},
        {"timestamp": 2, "value": 123.5},
        {"timestamp": 3, "value": 123.6},
    ]
    values_uri = config.VALUES_URI.replace("{metric_id}", str(metric.id))
    response = client.post(
        f"{config.API_PREFIX}{values_uri}", headers=headers, json=payload
    )
    assert response.status_code == 200
    values_in_db = session.exec(
        select(ValueEntity).join(MetricEntity).where(MetricEntity.id == metric.id)
    ).all()
    assert values_in_db is not None
    assert len(values_in_db) == len(payload)
    for index, entry in enumerate(payload):
        assert entry["timestamp"] == values_in_db[index].timestamp
        assert entry["value"] == float(values_in_db[index].value)


def test_add_values_with_str_timestamp(client, session, user):
    metric = create_metric(session, user, "one")
    values_uri = config.VALUES_URI.replace("{metric_id}", str(metric.id))
    headers = {config.AUTH_HEADER: VALID_TOKEN}
    payload = [
        {"timestamp": "01/11/2025 08:01:55", "value": 123.4},
        {"timestamp": "02/11/2025 09:19:28", "value": 123.5},
        {"timestamp": "03/11/2025 10:11:11", "value": 123.6},
    ]
    response = client.post(
        f"{config.API_PREFIX}{values_uri}", headers=headers, json=payload
    )
    assert response.status_code == 200
    values_in_db = session.exec(
        select(ValueEntity).where(ValueEntity.metric == metric)
    ).all()
    assert values_in_db is not None
    assert len(values_in_db) == len(payload)
    for index, entry in enumerate(payload):
        parsed_timestamp = int(
            parser.parse(entry["timestamp"], dayfirst=True).timestamp()
        )
        assert parsed_timestamp == values_in_db[index].timestamp
        assert entry["value"] == float(values_in_db[index].value)
