from celery import Celery
from core.config import settings

celery_app = Celery(
    "aitools",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        # Les tâches de chaque module sont déclarées ici
        # Ajoutez une ligne par module avec des tâches async
    ],
)

celery_app.conf.update(
    # Sérialisation JSON (plus sécurisé que pickle)
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Expiration des résultats après 1h
    result_expires=3600,

    # Retry automatique sur erreur de connexion broker
    broker_connection_retry_on_startup=True,

    # Limite de temps par tâche (10 minutes max)
    task_soft_time_limit=600,
    task_time_limit=660,

    # Routage des queues par priorité
    task_routes={
    },

    # Queues disponibles
    task_queues={
        "fast": {"exchange": "fast", "routing_key": "fast"},
        "slow": {"exchange": "slow", "routing_key": "slow"},
        "default": {"exchange": "default", "routing_key": "default"},
    },
    task_default_queue="default",
)
