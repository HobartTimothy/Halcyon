from celery import Celery

from agent.bootstrap.settings import Settings, get_settings


def create_celery_app(settings: Settings | None = None) -> Celery:
    resolved = settings or get_settings()
    app = Celery(
        "agent",
        broker=resolved.broker_url,
        backend=resolved.result_backend_url,
        include=["agent.entrypoints.workers.tasks.agent"],
    )

    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_routes={
            "agent.run.execute": {"queue": "agent.realtime"},
            "agent.run.resume": {"queue": "agent.resume"},
            "agent.memory.extract": {"queue": "memory.extract"},
            "agent.maintenance.*": {"queue": "maintenance"},
        },
    )
    return app


celery_app = create_celery_app()
