from agent.entrypoints.workers.celery_app import create_celery_app


def test_agent_task_is_routed_to_realtime_queue() -> None:
    app = create_celery_app()
    route = app.conf.task_routes["agent.run.execute"]
    assert route == {"queue": "agent.realtime"}


def test_worker_uses_json_only_serialization() -> None:
    app = create_celery_app()
    assert app.conf.task_serializer == "json"
    assert app.conf.accept_content == ["json"]
